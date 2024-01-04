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
                // Copy the generated password to the password field when clicked
                $("#generatedPassword").click(function() {
                    $("#floatingPassword").val(data.password);
                });
            },
            error: function(error) {
                console.log(error);
            },
        });
    }

    $("#generatePasswordIcon").click(function() {
        $(this).blur();
        if ($("#passwordGenerator").is(":hidden")) {
            requestPasswordGeneration();
            $("#passwordGenerator").slideDown(400, function() {
                $("html, body").animate(
                    {
                        scrollTop: $(this).offset().top,
                    },
                    1000,
                );
            });
        } else {
            $("#passwordGenerator").slideUp(400, function() {
                $("html, body").animate(1000);
            });
        }
    });

    $("#generatePasswordButton").click(function(event) {
        event.preventDefault();
        requestPasswordGeneration();
    });
});
