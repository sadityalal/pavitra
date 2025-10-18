// static/js/login.js
// Login page specific functionality

function initializeLoginPage() {
    console.log('Initializing login page...');

    // Password toggle functionality
    const passwordToggle = document.querySelector('.password-toggle');
    const passwordInput = document.getElementById('password');

    if (passwordToggle && passwordInput) {
        passwordToggle.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);

            const icon = this.querySelector('i');
            if (type === 'text') {
                icon.classList.remove('bi-eye');
                icon.classList.add('bi-eye-slash');
            } else {
                icon.classList.remove('bi-eye-slash');
                icon.classList.add('bi-eye');
            }
        });
    }

    // Form validation enhancement
    const loginForm = document.querySelector('.auth-form-content');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const email = document.getElementById('email');
            const password = document.getElementById('password');

            if (!email.value || !password.value) {
                e.preventDefault();
                showToast('Please fill in all required fields', 'error');
                return;
            }

            // Basic email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email.value)) {
                e.preventDefault();
                showToast('Please enter a valid email address', 'error');
                return;
            }
        });
    }

    // Auto-focus on email field
    const emailField = document.getElementById('email');
    if (emailField && !emailField.value) {
        emailField.focus();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we're on a login page
    if (document.querySelector('.login-form')) {
        initializeLoginPage();
    }
});