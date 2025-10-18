document.addEventListener('DOMContentLoaded', function() {
  // Initialize PureCounter for animated numbers
  if (typeof PureCounter !== 'undefined') {
    new PureCounter();
  }

  // Add scroll animations for team cards
  const teamCards = document.querySelectorAll('.team-card');
  teamCards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-10px)';
      this.style.transition = 'transform 0.3s ease';
    });

    card.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0)';
    });
  });
});