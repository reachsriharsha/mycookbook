// Custom JavaScript for the Flask application

$(document).ready(function() {
    console.log('Flask App loaded successfully!');
    
    // Add smooth scrolling to all links
    $('a[href*="#"]').on('click', function(e) {
        e.preventDefault();
        
        $('html, body').animate({
            scrollTop: $($(this).attr('href')).offset().top
        }, 500, 'linear');
    });
    
    // Add fade-in animation to cards
    $('.card').hide().fadeIn(1000);
    
    // Add click effect to all buttons
    $('.btn').on('click', function() {
        $(this).addClass('animate__pulse');
        setTimeout(() => {
            $(this).removeClass('animate__pulse');
        }, 600);
    });
});