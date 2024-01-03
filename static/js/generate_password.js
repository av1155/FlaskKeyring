$(document).ready(function() {
    function requestPasswordGeneration() {
        let passwordCriteria = {
            type: $("#passwordType").val(),
            length: $("#passwordLength").val(),
            numbers: $("#includeNumbers").is(":checked"),
            symbols: $("#includeSymbols").is(":checked"),
        };

        $.ajax({
            url: "/generate_password",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(passwordCriteria),
            dataType: "json",
            success: function(data) {
                $("#generatedPassword").val(data.password);
                $("#generatedPassword").focus();
            },
            error: function(error) {
                console.log(error);
            },
        });
    }

    $("#generatePasswordIcon").click(function() {
        $("#passwordGenerator").toggle();
        $(this).blur();
        requestPasswordGeneration();
    });

    $("#generatePasswordButton").click(function(event) {
        event.preventDefault();
        requestPasswordGeneration();
    });
});
