// static/js/session.js
// Session timeout and activity tracking - AUTO LOGOUT AFTER 10 MINUTES

let inactivityTimer;
let activityCheckInterval;

function startInactivityTimer() {
    console.log('Starting inactivity timer for auto-logout...');

    const resetTimer = () => {
        clearTimeout(inactivityTimer);
        // Logout after 10 minutes (600000 ms)
        inactivityTimer = setTimeout(() => {
            forceLogoutDueToInactivity();
        }, 600000); // 10 minutes
    };

    // Reset timer on user activity
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click', 'keydown'];
    events.forEach(event => {
        document.addEventListener(event, resetTimer, true);
    });

    // Also update server about activity (optional but good for sync)
    events.forEach(event => {
        document.addEventListener(event, updateServerActivity, true);
    });

    // Start the timer
    resetTimer();

    // Start periodic server session check (every 2 minutes)
    startServerSessionCheck();
}

function updateServerActivity() {
    // Only update server occasionally to avoid too many requests
    if (Math.random() < 0.1) { // 10% chance on each activity
        fetch('/api/update-activity', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            credentials: 'same-origin'
        }).catch(error => console.log('Activity update failed:', error));
    }
}

function startServerSessionCheck() {
    // Check server session status every 2 minutes
    activityCheckInterval = setInterval(() => {
        checkServerSession();
    }, 120000); // 2 minutes
}

function checkServerSession() {
    fetch('/api/check-session', {
        method: 'GET',
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            // Session might be expired on server
            if (response.status === 401) {
                forceLogoutDueToInactivity();
            }
        }
        return response.json();
    })
    .then(data => {
        if (data && data.session_valid === false) {
            forceLogoutDueToInactivity();
        }
    })
    .catch(error => {
        console.log('Session check failed:', error);
    });
}

function forceLogoutDueToInactivity() {
    console.log('Auto-logout due to inactivity');

    // Clear all timers and intervals
    clearTimeout(inactivityTimer);
    clearInterval(activityCheckInterval);

    // Show session expired message
    showToast('Your session has expired due to inactivity. Redirecting to login...', 'warning');

    // Perform server-side logout and redirect
    fetch('/auth/logout', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        credentials: 'same-origin'
    })
    .finally(() => {
        // Redirect to login page with expired parameter
        setTimeout(() => {
            window.location.href = "/login?expired=true";
        }, 2000);
    });
}

function showSessionExpiredMessage() {
    console.log('Session expired, showing message...');
    showToast('Your session has expired. Please login again.', 'info');

    // Redirect to login after a brief delay
    setTimeout(() => {
        window.location.href = "/login?expired=true";
    }, 3000);
}

// Enhanced initialization with user check
function initializeSessionTimeout() {
    // Only start if user is authenticated (check via data attribute or class)
    const isAuthenticated = document.body.classList.contains('user-authenticated') ||
                           document.querySelector('[data-user-authenticated="true"]') ||
                           document.querySelector('.user-account-menu');

    if (isAuthenticated) {
        console.log('User is authenticated, starting inactivity timer...');
        startInactivityTimer();
    } else {
        console.log('User not authenticated, skipping inactivity timer');
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeSessionTimeout();
});

// Clean up when leaving page
window.addEventListener('beforeunload', function() {
    clearTimeout(inactivityTimer);
    clearInterval(activityCheckInterval);
});