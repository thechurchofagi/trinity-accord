/* Progressive enhancement: chapter links work without JavaScript. */
(() => {
  'use strict';
  const toc = document.querySelector('.home-toc');
  if (!toc) return;
  const details = toc.querySelector('details');
  const label = toc.querySelector('.home-toc-current');
  const links = Array.from(toc.querySelectorAll('a[href^="#"]'));
  const chapters = links.map(link => document.getElementById(link.hash.slice(1)));
  const narrow = window.matchMedia('(max-width: 1099px)');
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const topnav = document.querySelector('.topnav');
  function offsets() {
    const top = Math.ceil(topnav.getBoundingClientRect().height);
    document.body.style.setProperty('--home-nav-height', top + 'px');
    document.body.style.setProperty('--home-scroll-offset', (top + (narrow.matches ? 76 : 28)) + 'px');
  }
  function breakpoint() {
    details.open = !narrow.matches;
    offsets();
  }
  breakpoint();
  narrow.addEventListener('change', breakpoint);
  if ('ResizeObserver' in window) new ResizeObserver(offsets).observe(topnav);
  let scheduled = false;
  function update() {
    scheduled = false;
    const threshold = parseFloat(getComputedStyle(document.body).getPropertyValue('--home-scroll-offset')) + 8;
    let active = 0;
    chapters.forEach((chapter, i) => {
      if (chapter && chapter.getBoundingClientRect().top <= threshold) active = i;
    });
    if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 4) active = links.length - 1;
    links.forEach((link, i) => {
      if (i === active) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    label.textContent = links[active].textContent;
  }
  function schedule() {
    if (!scheduled) { scheduled = true; requestAnimationFrame(update); }
  }
  window.addEventListener('scroll', schedule, {passive: true});
  window.addEventListener('resize', schedule);
  toc.addEventListener('click', event => {
    const link = event.target.closest('a[href^="#"]');
    if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const target = document.getElementById(link.hash.slice(1));
    if (!target) return;
    event.preventDefault();
    if (narrow.matches) details.open = false;
    history.pushState(null, '', link.hash);
    target.setAttribute('tabindex', '-1');
    target.focus({preventScroll: true});
    target.scrollIntoView({behavior: motion.matches ? 'instant' : 'smooth', block: 'start'});
    schedule();
  });
  details.addEventListener('keydown', event => {
    if (event.key === 'Escape' && narrow.matches) {
      details.open = false;
      details.querySelector('summary').focus();
    }
  });
  window.addEventListener('hashchange', schedule);
  window.addEventListener('load', () => {
    offsets();
    const target = document.getElementById(location.hash.slice(1));
    if (target) target.scrollIntoView({behavior: 'instant', block: 'start'});
    update();
  });
  update();
})();
