$(document).ready(function () {
    // Initially show the alert
    $(".alert").css("opacity", "1");

    // Wait for 3 seconds, then fade out
    setTimeout(function () {
        $(".alert").slideUp(500); // Slide up effect for hiding
    }, 3000); // Time in milliseconds (3000ms = 3s)
});
