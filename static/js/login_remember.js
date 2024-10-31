document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("username_email");
    const rememberMeCheckbox = document.getElementById("exampleCheck1");

    // Set the input field value from localStorage if 'Remember me' was checked previously
    const rememberedUsername = localStorage.getItem("rememberedUsername");
    if (rememberedUsername) {
        inputField.value = rememberedUsername;
        rememberMeCheckbox.checked = true;
    }

    rememberMeCheckbox.addEventListener("change", function () {
        if (this.checked) {
            localStorage.setItem("rememberedUsername", inputField.value);
        } else {
            localStorage.removeItem("rememberedUsername");
        }
    });

    inputField.addEventListener("input", function () {
        if (rememberMeCheckbox.checked) {
            localStorage.setItem("rememberedUsername", inputField.value);
        }
    });
});
