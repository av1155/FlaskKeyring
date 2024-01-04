$(document).ready(function() {
    $(".alert").css("opacity", "1");

    setTimeout(function() {
        $(".alert").slideUp(500); // Slide up and fade out
    }, 3000); // Alert is visible for 3 seconds
});
