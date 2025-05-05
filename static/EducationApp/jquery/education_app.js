// JavaScript functions for EducationApp

document.addEventListener('DOMContentLoaded', function() {
    console.log('سیستم آموزش دانشگاهی آماده است.');
    
    // اضافه کردن انیمیشن به عناصر صفحه
    const elements = document.querySelectorAll('.feature');
    elements.forEach((element, index) => {
        setTimeout(() => {
            element.style.opacity = '1';
        }, 300 * index);
    });
}); 