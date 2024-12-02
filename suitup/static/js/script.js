// jQuery ready start
$(document).ready(function () {
    // Prevent closing dropdown on click inside
    $(document).on('click', '.dropdown-menu', function (e) {
        e.stopPropagation();
    });

    // Radio button interaction
    $('.js-check :radio').change(function () {
        var checkAttrName = $(this).attr('name'); // Proper camelCase for variable
        if ($(this).is(':checked')) {
            $(`input[name="${checkAttrName}"]`).closest('.js-check').removeClass('active');
            $(this).closest('.js-check').addClass('active');
        }
    });

    // Checkbox interaction
    $('.js-check :checkbox').change(function () {
        $(this).closest('.js-check').toggleClass('active', $(this).is(':checked'));
    });

    // Initialize Bootstrap tooltips
    $('[data-toggle="tooltip"]').tooltip();

    // Fade out alert and message elements after 4 seconds
    setTimeout(function () {
        $('.alert, #message').fadeOut('slow');
    }, 4000);

    // Custom jQuery initialization
    console.log('Custom jQuery code loaded');
});

// Vanilla JavaScript
const mainImage = document.getElementById('main-image');
const zoomWindow = document.getElementById('zoom-window');
const thumbnails = document.querySelectorAll('.thumbnail');

// Check if mainImage and zoomWindow exist
if (mainImage && zoomWindow) {
    // Thumbnail Click Event
    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function () {
            const fullImageUrl = this.getAttribute('data-full');
            mainImage.src = fullImageUrl;
            zoomWindow.style.backgroundImage = `url(${fullImageUrl})`;
        });
    });

    // Zoom Effect
    mainImage.addEventListener('mousemove', function (e) {
        const { left, top, width, height } = mainImage.getBoundingClientRect();
        const x = ((e.pageX - left) / width) * 100;
        const y = ((e.pageY - top) / height) * 100;

        zoomWindow.style.backgroundPosition = `${x}% ${y}%`;
        zoomWindow.style.visibility = 'visible';
    });

    mainImage.addEventListener('mouseleave', function () {
        zoomWindow.style.visibility = 'hidden';
    });
}
