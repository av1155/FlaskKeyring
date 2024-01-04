document.addEventListener("DOMContentLoaded", function() {
    var passwordInput = document.getElementById("floatingPassword");
    passwordInput.addEventListener("focus", function() {
        passwordInput.type = "text";
        window.setTimeout(function() {
            passwordInput.selectionStart = passwordInput.selectionEnd = -1;
        }, 0);
    });
    passwordInput.addEventListener("blur", function() {
        passwordInput.type = "password";
    });
});
