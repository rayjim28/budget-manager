(() => {
  const shell = document.querySelector('.app-shell');
  const button = document.querySelector('#menu-toggle');
  const scrim = document.querySelector('#mobile-scrim');
  if (shell && button && scrim) {
    function closeMenu() {
      shell.classList.remove('nav-open');
      button.setAttribute('aria-expanded', 'false');
    }
    button.addEventListener('click', () => {
      const isOpen = shell.classList.toggle('nav-open');
      button.setAttribute('aria-expanded', String(isOpen));
    });
    scrim.addEventListener('click', closeMenu);
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') closeMenu();
    });
  }
})();
