/*
================================================================================
                    MOBILE MENU HANDLER
================================================================================
Provides mobile-friendly navigation with hamburger menu
*/

let mobileMenuOpen = false;

function initMobileMenu() {
  const toggleBtn = document.querySelector('.mobile-menu-toggle');
  const mobileMenu = document.querySelector('.mobile-menu');
  
  if (!toggleBtn || !mobileMenu) return;
  
  toggleBtn.addEventListener('click', () => {
    mobileMenuOpen = !mobileMenuOpen;
    mobileMenu.classList.toggle('active', mobileMenuOpen);
    toggleBtn.setAttribute('aria-expanded', mobileMenuOpen);
  });
  
  // Close menu when a link is clicked
  mobileMenu.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      mobileMenuOpen = false;
      mobileMenu.classList.remove('active');
      toggleBtn.setAttribute('aria-expanded', false);
    });
  });
  
  // Close menu when clicking outside
  document.addEventListener('click', (e) => {
    if (mobileMenuOpen && !mobileMenu.contains(e.target) && !toggleBtn.contains(e.target)) {
      mobileMenuOpen = false;
      mobileMenu.classList.remove('active');
      toggleBtn.setAttribute('aria-expanded', false);
    }
  });
  
  // Close menu on escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && mobileMenuOpen) {
      mobileMenuOpen = false;
      mobileMenu.classList.remove('active');
      toggleBtn.setAttribute('aria-expanded', false);
    }
  });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initMobileMenu);

// Re-initialize on dynamic page loads
function reinitMobileMenu() {
  initMobileMenu();
}
