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
                $("#generatedPassword").click(function() {
                    $("#floatingPassword").val(data.password);
                });
            },
            error: function(error) {
                console.log(error);
            },
        });
    }

    // Update the display when the slider is moved
    $("#passwordLength").on("input", function() {
        $("#passwordLengthDisplay").text("Length: " + $(this).val());
    });

    $("#generatePasswordIcon").click(function() {
        $(this).blur();
        if ($("#passwordGenerator").is(":hidden")) {
            requestPasswordGeneration();
            $("#passwordGenerator").slideDown(400);
            $("html, body").animate({ scrollTop: "+=300" }, 400);
        } else {
            $("#passwordGenerator").slideUp(400);
            $("html, body").animate({ scrollTop: "-=300" }, 400);
        }
    });

    $("#generatePasswordButton").click(function(event) {
        event.preventDefault();
        requestPasswordGeneration();
    });
});
