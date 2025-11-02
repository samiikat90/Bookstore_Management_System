/**
 * Session Timeout Management for Admin Users
 * 
 * Automatically monitors admin session activity and displays warnings
 * before timeout. Provides option to extend session or logout.
 */

// Global variables for session management
let sessionTimeoutWarning = null;
let sessionCheckInterval = null;
let lastActivityTime = Date.now();

// Track user activity
function trackActivity() {
  lastActivityTime = Date.now();
}

// Activity event listeners
document.addEventListener('mousedown', trackActivity);
document.addEventListener('mousemove', trackActivity);
document.addEventListener('keypress', trackActivity);
document.addEventListener('scroll', trackActivity);
document.addEventListener('click', trackActivity);

// Check session status every 30 seconds
function checkSessionStatus() {
  // Use vanilla JS fetch instead of jQuery for compatibility with slim jQuery
  fetch('/api/session_status')
    .then(response => response.json())
    .then(data => {
      if (data.expired) {
        clearInterval(sessionCheckInterval);
        showSessionExpiredMessage();
        setTimeout(() => {
          window.location.href = '/login';
        }, 3000);
      } else if (data.show_warning && !sessionTimeoutWarning) {
        showTimeoutWarning(Math.floor(data.minutes_remaining));
      } else if (!data.show_warning && sessionTimeoutWarning) {
        hideTimeoutWarning();
      }
    })
    .catch(error => {
      console.error('Error checking session status:', error);
    });
}

// Show timeout warning modal
function showTimeoutWarning(minutesRemaining) {
  if (sessionTimeoutWarning) return; // Already showing
  
  sessionTimeoutWarning = true;
  
  // Create modal HTML
  const modalHtml = `
    <div class="modal fade" id="timeoutWarningModal" tabindex="-1" role="dialog" aria-labelledby="timeoutWarningLabel">
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content border-warning">
          <div class="modal-header bg-warning text-dark">
            <h4 class="modal-title" id="timeoutWarningLabel">
              <i class="fas fa-clock"></i> Session Timeout Warning
            </h4>
          </div>
          <div class="modal-body text-center">
            <div class="mb-3">
              <i class="fas fa-hourglass-half fa-3x text-warning"></i>
            </div>
            <h5>Your session will expire in <span id="countdown">${minutesRemaining}</span> minutes</h5>
            <p class="mb-0">Would you like to extend your session?</p>
          </div>
          <div class="modal-footer justify-content-center">
            <button type="button" class="btn btn-success" onclick="extendSession()">
              <i class="fas fa-refresh"></i> Extend Session
            </button>
            <button type="button" class="btn btn-outline-secondary" onclick="logoutNow()">
              <i class="fas fa-sign-out-alt"></i> Logout Now
            </button>
          </div>
        </div>
      </div>
    </div>
  `;
  
  // Add modal to body
  document.body.insertAdjacentHTML('beforeend', modalHtml);
  
  // Show modal
  $('#timeoutWarningModal').modal({
    backdrop: 'static',
    keyboard: false
  });
  
  // Update countdown every 10 seconds
  const countdownInterval = setInterval(() => {
    fetch('/api/session_status')
      .then(response => response.json())
      .then(data => {
        if (data.expired) {
          clearInterval(countdownInterval);
          hideTimeoutWarning();
          showSessionExpiredMessage();
          setTimeout(() => {
            window.location.href = '/login';
          }, 3000);
        } else {
          const remaining = Math.floor(data.minutes_remaining);
          const countdownElement = document.getElementById('countdown');
          if (countdownElement) {
            countdownElement.textContent = remaining;
          }
          
          if (!data.show_warning) {
            clearInterval(countdownInterval);
            hideTimeoutWarning();
          }
        }
      })
      .catch(error => {
        console.error('Error updating countdown:', error);
        clearInterval(countdownInterval);
      });
  }, 10000);
}

// Hide timeout warning
function hideTimeoutWarning() {
  sessionTimeoutWarning = null;
  $('#timeoutWarningModal').modal('hide');
  setTimeout(() => {
    const modal = document.getElementById('timeoutWarningModal');
    if (modal) {
      modal.remove();
    }
  }, 500);
}

// Extend session
function extendSession() {
  fetch('/api/extend_session', { method: 'POST' })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        hideTimeoutWarning();
        // Show brief success message
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show position-fixed';
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
        alert.innerHTML = `
          <i class="fas fa-check-circle"></i> Session extended successfully!
          <button type="button" class="close" data-dismiss="alert">
            <span>&times;</span>
          </button>
        `;
        document.body.appendChild(alert);
        setTimeout(() => {
          if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
          }
        }, 3000);
      }
    })
    .catch(error => {
      console.error('Error extending session:', error);
    });
}

// Logout immediately
function logoutNow() {
  window.location.href = '/logout';
}

// Show session expired message
function showSessionExpiredMessage() {
  hideTimeoutWarning();
  
  const alert = document.createElement('div');
  alert.className = 'alert alert-danger alert-dismissible position-fixed';
  alert.style.cssText = 'top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 9999; min-width: 300px;';
  alert.innerHTML = `
    <h5><i class="fas fa-exclamation-triangle"></i> Session Expired</h5>
    <p class="mb-0">Your session has expired due to inactivity. Redirecting to login...</p>
  `;
  document.body.appendChild(alert);
}

// Initialize session monitoring when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  // Start session monitoring
  sessionCheckInterval = setInterval(checkSessionStatus, 30000); // Check every 30 seconds
  
  // Initial session check
  checkSessionStatus();
});

// Stop monitoring when leaving page
window.addEventListener('beforeunload', function() {
  if (sessionCheckInterval) {
    clearInterval(sessionCheckInterval);
  }
});