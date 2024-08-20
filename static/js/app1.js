document.addEventListener("DOMContentLoaded", function() {
    const buttons = document.querySelectorAll(".boutons a");
    const slides = document.querySelectorAll(".slide");

    buttons.forEach(function(button, index) {
        button.addEventListener("click", function(event) {
            event.preventDefault();

            // Hide all slides
            slides.forEach(function(slide) {
                slide.style.display = "none";
            });

            // Remove active class from all buttons
            buttons.forEach(function(btn) {
                btn.classList.remove("active");
            });

            // Display the corresponding slide
            slides[index].style.display = "block";
            // Add active class to the clicked button
            button.classList.add("active");
        });
    });
});