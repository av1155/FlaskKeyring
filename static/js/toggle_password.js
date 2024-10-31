document.addEventListener("DOMContentLoaded", function () {
    const passwordInput = document.getElementById("floatingPassword");
    const togglePasswordButton = document.getElementById("togglePassword");
    const toggleIcon = togglePasswordButton.querySelector("i");

    togglePasswordButton.addEventListener("click", function () {
        if (passwordInput.type === "password") {
            passwordInput.type = "text";
            toggleIcon.classList.remove("bi-eye-slash");
            toggleIcon.classList.add("bi-eye");
        } else {
            passwordInput.type = "password";
            toggleIcon.classList.remove("bi-eye");
            toggleIcon.classList.add("bi-eye-slash");
        }
    });
});
