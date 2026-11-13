(() => {
  // Decorative hero photography is optional; gradients remain when it fails.
  document.querySelectorAll('img.hero-img').forEach(image => {
    const hideUnavailable = () => {if (!image.naturalWidth) image.style.display = 'none';};
    image.addEventListener('error', hideUnavailable);
    if (image.complete) hideUnavailable();
  });
  const header = document.querySelector('.site-header');
  const toggle = header?.querySelector('.site-menu-toggle');
  const nav = header?.querySelector('.site-navigation');
  const coworkingMenu = header?.querySelector('.site-coworking');
  document.addEventListener('click', e => {
    if (coworkingMenu && !coworkingMenu.contains(e.target)) coworkingMenu.open = false;
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && coworkingMenu?.open) {
      coworkingMenu.open = false;
      coworkingMenu.querySelector('summary').focus();
    }
  });
  if (toggle && nav) {
    const close = (restoreFocus = false) => {
      header.dataset.open = 'false';
      if (coworkingMenu) coworkingMenu.open = false;
      toggle.setAttribute('aria-expanded', 'false');
      toggle.querySelector('span').textContent = 'Menu';
      if (restoreFocus) toggle.focus();
    };
    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      header.dataset.open = String(open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.querySelector('span').textContent = open ? 'Close' : 'Menu';
    });
    nav.addEventListener('click', e => {if (e.target.closest('a')) close();});
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && header.dataset.open === 'true') close(true);
    });
    document.addEventListener('click', e => {if (!header.contains(e.target)) close();});
    header.addEventListener('focusout', () => {
      setTimeout(() => {if (!header.contains(document.activeElement)) close();}, 0);
    });
    matchMedia('(min-width:1280px)').addEventListener('change', () => close());
  }
  document.querySelectorAll('form[data-enquiry]').forEach(form => {
    form.addEventListener('submit', e => {
      e.preventDefault();
      if (!form.reportValidity()) return;
      const lines = [`Hello JobReady, I have a ${form.dataset.enquiry} enquiry.`];
      for (const [name,value] of new FormData(form)) {
        if (typeof value === 'string' && value.trim()) lines.push(`${name}: ${value.trim()}`);
      }
      lines.push('Please confirm availability, inclusions and a written quote.');
      location.assign('https://wa.me/919172712982?text=' + encodeURIComponent(lines.join('\n')));
    });
  });
})();
