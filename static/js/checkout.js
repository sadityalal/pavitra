document.addEventListener('DOMContentLoaded', function() {
  // Payment method toggle
  const paymentOptions = document.querySelectorAll('input[name="payment_method"]');
  const paymentDetails = document.querySelectorAll('.payment-details');

  paymentOptions.forEach(option => {
    option.addEventListener('change', function() {
      // Hide all payment details
      paymentDetails.forEach(detail => {
        detail.classList.add('d-none');
      });

      // Show selected payment details
      const selectedDetail = document.getElementById(this.id + '-details');
      if (selectedDetail) {
        selectedDetail.classList.remove('d-none');
      }
    });
  });

  // Form validation
  const checkoutForm = document.querySelector('.checkout-form');
  checkoutForm.addEventListener('submit', function(e) {
    const termsCheckbox = document.getElementById('terms');
    if (!termsCheckbox.checked) {
      e.preventDefault();
      alert('Please agree to the Terms and Conditions to proceed.');
      termsCheckbox.focus();
      return;
    }

    // Check if address is selected
    const selectedAddress = document.querySelector('input[name="shipping_address_id"]:checked');
    if (!selectedAddress) {
      e.preventDefault();
      alert('Please select a shipping address.');
      return;
    }
  });

  // Initialize payment method display
  const defaultPayment = document.querySelector('input[name="payment_method"]:checked');
  if (defaultPayment) {
    const defaultDetail = document.getElementById(defaultPayment.id + '-details');
    if (defaultDetail) {
      defaultDetail.classList.remove('d-none');
    }
  }
});