

// jQuery ready start
$(document).ready(function () {
  const allDropdowns = $('select'); // Cache all dropdowns
  
  function checkStock() {
    // Check if any dropdown is empty
    const hasEmptyDropdown = allDropdowns.toArray().some(dropdown => !$(dropdown).val());

    if (hasEmptyDropdown) {
      return; // Stop if any dropdown is empty
    }

    // Collect values only if all dropdowns are filled
    const selectedValues = {};
    allDropdowns.each(function () {
      selectedValues[$(this).attr('id')] = $(this).val();
    });

    $.ajax({
      url: checkStockUrl,
      type: "GET",
      data: selectedValues,
      success: function (response) {
        $('#stock-status').html(response.stock_status);
        
        if (response.can_add_to_cart) {
          $('#add-cart-button').html(`
            <button type="submit" class="btn btn-primary">
              <span class="text">Add to cart</span>
              <i class="fas fa-shopping-cart"></i>
            </button>
          `);
          let price = response.product_price.replace('$', ''); // Remove $ if present
          $('#product-price').html(`
            <h4 class="price">₹${price}</h4>
          `);
        } else {
          $('#add-cart-button').html(`
            <h5 class="text-info">Try after some time</h5>
          `);
          $('#product-price').html(`
            <h4 class="price">No Price info</h4>
          `);
        }
      },
      error: function (xhr, status, error) {
        console.error("Error:", error);
      }
    });
  }
// Call checkStock on dropdown change
allDropdowns.change(checkStock);

  // Initial check if all dropdowns have default values
if (!allDropdowns.toArray().some(dropdown => !$(dropdown).val())) {
  checkStock();
}
});


$(document).ready(function () {
    // Prevent closing dropdown on click inside
    $(document).on('click', '.dropdown-menu', function (e) {
        e.stopPropagation();
    });

    // Radio button interaction
    $('.js-check :radio').change(function () {
        var checkAttrName = $(this).attr('name'); // Proper camelCase for variable
        if ($(this).is(':checked')) {
            $('input[name=' + checkAttrName + ']').closest('.js-check').removeClass('active');
            $(this).closest('.js-check').addClass('active');
        }
    });

    // Checkbox interaction
    $('.js-check :checkbox').change(function () {
        if ($(this).is(':checked')) {
            $(this).closest('.js-check').addClass('active');
        } else {
            $(this).closest('.js-check').removeClass('active');
        }
    });

    // Initialize Bootstrap tooltips
    if ($('[data-toggle="tooltip"]').length > 0) { // Check if tooltips exist
        $('[data-toggle="tooltip"]').tooltip();
    }
 // Fade out alert messages after 4 seconds
 setTimeout(function () {
    $('.alert').fadeOut('slow');
}, 4000);
});
// jQuery ready end


const mainImage = document.getElementById('main-image');
const zoomWindow = document.getElementById('zoom-window');
const thumbnails = document.querySelectorAll('.thumbnail');

// Thumbnail Click Event
thumbnails.forEach(thumbnail => {
    thumbnail.addEventListener('click', function() {
        const fullImageUrl = this.getAttribute('data-full');
        mainImage.src = fullImageUrl;
        zoomWindow.style.backgroundImage = `url(${fullImageUrl})`;
    });
});

// Zoom Effect
mainImage.addEventListener('mousemove', function(e) {
    const { left, top, width, height } = mainImage.getBoundingClientRect();
    const x = ((e.pageX - left) / width) * 100;
    const y = ((e.pageY - top) / height) * 100;

    zoomWindow.style.backgroundPosition = `${x}% ${y}%`;
    zoomWindow.style.visibility = 'visible';
});

mainImage.addEventListener('mouseleave', function() {
    zoomWindow.style.visibility = 'hidden';
});



