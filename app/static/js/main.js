document.addEventListener('DOMContentLoaded', function () {
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach((alertEl) => {
    setTimeout(() => {
      if (alertEl && alertEl.parentNode) {
        alertEl.remove();
      }
    }, 3500);
  });
});
