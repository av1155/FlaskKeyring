// Encrypt master password using Web Crypto API
async function encryptMasterPassword(password) {
    const encoder = new TextEncoder();
    const encodedPassword = encoder.encode(password);
    const key = await crypto.subtle.generateKey({ name: "AES-GCM", length: 256 }, true, [
        "encrypt",
        "decrypt",
    ]);
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const encryptedPassword = await crypto.subtle.encrypt(
        { name: "AES-GCM", iv: iv },
        key,
        encodedPassword,
    );

    // Export the key and store it along with the encrypted password and IV
    const exportedKey = await crypto.subtle.exportKey("raw", key);
    return {
        encryptedPassword: Array.from(new Uint8Array(encryptedPassword)),
        iv: Array.from(iv),
        key: Array.from(new Uint8Array(exportedKey)),
    };
}

// Decrypt master password using Web Crypto API
async function decryptMasterPassword(encryptedData) {
    const { encryptedPassword, iv, key } = encryptedData;
    const importedKey = await crypto.subtle.importKey(
        "raw",
        new Uint8Array(key),
        { name: "AES-GCM", length: 256 },
        true,
        ["decrypt"],
    );

    try {
        const decrypted = await crypto.subtle.decrypt(
            { name: "AES-GCM", iv: new Uint8Array(iv) },
            importedKey,
            new Uint8Array(encryptedPassword),
        );
        const decoder = new TextDecoder();
        return decoder.decode(decrypted);
    } catch (e) {
        console.error("Decryption failed:", e);
        return null;
    }
}

// Function to get the encryption password, prompting the user if necessary
async function getEncryptionPassword() {
    let encryptedData = sessionStorage.getItem("encryptedMasterPassword");

    while (true) {
        if (!encryptedData) {
            // Prompt the user to enter their encryption password if not stored
            let password = await promptEncryptionPassword();
            if (password) {
                const encrypted = await encryptMasterPassword(password);
                sessionStorage.setItem("encryptedMasterPassword", JSON.stringify(encrypted));
                return password;
            } else {
                // User closed the modal; set placeholder to indicate authentication is required
                document.getElementById("unlockPasswordInput").placeholder =
                    "Authentication Required";
                return null;
            }
        } else {
            encryptedData = JSON.parse(encryptedData);
            const decryptedPassword = await decryptMasterPassword(encryptedData);

            if (decryptedPassword !== null) {
                return decryptedPassword;
            } else {
                sessionStorage.removeItem("encryptedMasterPassword");
                const retryPassword = await promptEncryptionPassword(true);
                if (retryPassword) {
                    const encrypted = await encryptMasterPassword(retryPassword);
                    sessionStorage.setItem("encryptedMasterPassword", JSON.stringify(encrypted));
                    encryptedData = sessionStorage.getItem("encryptedMasterPassword");
                } else {
                    // User canceled or did not enter a password after retry
                    document.getElementById("unlockPasswordInput").placeholder =
                        "Authentication Required";
                    return null;
                }
            }
        }
    }
}

// Function to prompt the user for the encryption password using a modal
function promptEncryptionPassword(showError = false) {
    return new Promise((resolve) => {
        const modalHtml = `
        <div class="modal fade" id="unlockModal" tabindex="-1" aria-labelledby="unlockModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Unlock Vault</h5>
                        <button type="button" class="btn-close" id="closeModalButton" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p>Please enter your master password to unlock your vault.</p>
                        <input type="password" id="unlockPasswordInput" class="form-control" placeholder="Master Password">
                        <div id="error-message" class="text-danger mt-2" style="display: ${showError ? "block" : "none"};">Incorrect master password. Please try again.</div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" id="unlockSubmitButton" class="btn btn-primary">Unlock</button>
                    </div>
                </div>
            </div>
        </div>
        `;

        document.body.insertAdjacentHTML("beforeend", modalHtml);
        const unlockModalElement = document.getElementById("unlockModal");
        const unlockModal = new bootstrap.Modal(unlockModalElement, {
            backdrop: "static",
            keyboard: false,
        });
        unlockModal.show();

        unlockModalElement.addEventListener("shown.bs.modal", () => {
            document.getElementById("unlockPasswordInput").focus();
        });

        document.getElementById("unlockSubmitButton").addEventListener("click", () => {
            const password = document.getElementById("unlockPasswordInput").value;
            if (password) {
                unlockModal.hide();
                unlockModalElement.addEventListener("hidden.bs.modal", () => {
                    unlockModalElement.remove();
                    resolve(password);
                });
            } else {
                document.getElementById("error-message").textContent =
                    "Please enter your master password.";
                document.getElementById("error-message").style.display = "block";
            }
        });

        document.getElementById("unlockPasswordInput").addEventListener("keyup", (event) => {
            if (event.key === "Enter") {
                document.getElementById("unlockSubmitButton").click();
            }
        });

        document.getElementById("closeModalButton").addEventListener("click", () => {
            unlockModal.hide();
            unlockModalElement.addEventListener("hidden.bs.modal", () => {
                unlockModalElement.remove();
                resolve(null); // Resolve null to indicate the modal was closed
            });
        });
    });
}

// Decryption function with retry mechanism
async function decryptData(data) {
    let decrypted = null;

    while (true) {
        // Get the encryption password, which will prompt if not already set
        let password = await getEncryptionPassword();

        if (!password) {
            return null;
        }

        try {
            // Attempt decryption with the entered password
            decrypted = await attemptDecryption(data, password);
            if (decrypted !== null) {
                // If successful, store the correct password and return the decrypted data
                sessionStorage.setItem("encryptionPassword", password);
                return decrypted;
            } else {
                // Clear stored password and re-prompt if decryption fails
                sessionStorage.removeItem("encryptedMasterPassword");
                // The loop will continue, and getEncryptionPassword will re-prompt
            }
        } catch (e) {
            console.error("Decryption failed:", e);
            // Clear session storage if decryption fails
            sessionStorage.removeItem("encryptionPassword");
        }
    }
}

// Helper function to attempt decryption with provided password
async function attemptDecryption(data, password) {
    const encoder = new TextEncoder();
    const passwordKey = await crypto.subtle.importKey(
        "raw",
        encoder.encode(password),
        { name: "PBKDF2" },
        false,
        ["deriveBits", "deriveKey"],
    );

    const salt = new Uint8Array(data.salt.map(Number));
    const key = await crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt: salt,
            iterations: 100000,
            hash: "SHA-256",
        },
        passwordKey,
        { name: "AES-GCM", length: 256 },
        true,
        ["decrypt"],
    );

    const iv = new Uint8Array(data.iv.map(Number));
    const ciphertext = new Uint8Array(data.ciphertext.map(Number));

    try {
        const decrypted = await crypto.subtle.decrypt({ name: "AES-GCM", iv: iv }, key, ciphertext);
        const decoder = new TextDecoder();
        return decoder.decode(decrypted);
    } catch (e) {
        // Decryption failed
        return null;
    }
}

// Encryption function (unchanged)
async function encryptData(data) {
    const password = await getEncryptionPassword();
    if (!password) {
        // Password not available, stop further execution
        return null;
    }
    const encoder = new TextEncoder();
    const passwordKey = await crypto.subtle.importKey(
        "raw",
        encoder.encode(password),
        { name: "PBKDF2" },
        false,
        ["deriveBits", "deriveKey"],
    );

    const salt = crypto.getRandomValues(new Uint8Array(16));
    const key = await crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt: salt,
            iterations: 100000,
            hash: "SHA-256",
        },
        passwordKey,
        { name: "AES-GCM", length: 256 },
        true,
        ["encrypt"],
    );

    const iv = crypto.getRandomValues(new Uint8Array(12));
    const ciphertext = await crypto.subtle.encrypt(
        { name: "AES-GCM", iv: iv },
        key,
        encoder.encode(data),
    );

    return {
        ciphertext: Array.from(new Uint8Array(ciphertext)),
        iv: Array.from(iv),
        salt: Array.from(salt),
    };
}

// Inactivity timeout function (unchanged)
function setupInactivityTimeout() {
    let inactivityTimer;

    function resetTimer() {
        clearTimeout(inactivityTimer);
        // Set timer for 15 minutes (900,000 milliseconds)
        inactivityTimer = setTimeout(logout, 900000);
    }

    function logout() {
        // Clear stored session data for encryption and logout
        sessionStorage.removeItem("encryptionPassword");
        sessionStorage.removeItem("encryptedMasterPassword");
        alert("Session expired due to inactivity.");
        window.location.href = "/logout"; // Redirect to logout route
    }

    // Add event listeners for user activity
    window.addEventListener("load", resetTimer, true);
    document.addEventListener("mousemove", resetTimer, true);
    document.addEventListener("keypress", resetTimer, true);
    document.addEventListener("scroll", resetTimer, true);
    document.addEventListener("click", resetTimer, true);
}

// Initialize the inactivity timeout when the window loads
window.addEventListener("load", () => {
    setupInactivityTimeout();
});
