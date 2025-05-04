$(document).ready(function() {
    // انیمیشن برای دکمه
    $('a').hover(
        function() {
            $(this).addClass('scale-105');
        },
        function() {
            $(this).removeClass('scale-105');
        }
    );

    // انیمیشن برای آیکون‌ها
    $('.fa-university, .fa-book-open, .fa-arrow-left').addClass('animate-pulse');
});