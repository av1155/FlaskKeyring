document.addEventListener("DOMContentLoaded", function() {
    const inputField = document.getElementById("username_email");
    const rememberMeCheckbox = document.getElementById("exampleCheck1");

    // Check if 'Remember me' is checked and set the input field value
    if (rememberMeCheckbox.checked) {
        inputField.value = localStorage.getItem("lastLogin") || "";
    }

    rememberMeCheckbox.addEventListener("change", function() {
        if (this.checked) {
            localStorage.setItem("lastLogin", inputField.value);
        } else {
            localStorage.removeItem("lastLogin");
            inputField.value = "";
        }
    });

    inputField.addEventListener("input", function() {
        if (rememberMeCheckbox.checked) {
            localStorage.setItem("lastLogin", inputField.value);
        }
    });
});
