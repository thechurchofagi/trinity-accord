/* Static contents and full text work without JavaScript. */
(() => {
  'use strict';
  const toc = document.querySelector('.document-toc');
  if (!toc) return;
  const details = toc.querySelector('details');
  const summary = details.querySelector('summary');
  const current = toc.querySelector('.document-toc-current');
  const links = Array.from(toc.querySelectorAll('a[href^="#"]'));
  const chapters = links.map(link => document.getElementById(decodeURIComponent(link.hash.slice(1))));
  const narrow = matchMedia('(max-width: 1099px)');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const topnav = document.querySelector('.topnav');
  function offsets() {
    const top = Math.ceil(topnav.getBoundingClientRect().height);
    document.body.style.setProperty('--reading-nav-height', top + 'px');
    const rail = narrow.matches ? Math.ceil(summary.getBoundingClientRect().height) : 0;
    document.body.style.setProperty('--reading-scroll-offset', (top + rail + 24) + 'px');
  }
  function breakpoint() {
    details.open = !narrow.matches;
    offsets();
  }
  breakpoint();
  narrow.addEventListener('change', breakpoint);
  // Desktop contents remain available even when the summary is focused by keyboard.
  details.addEventListener('toggle', () => { if (!narrow.matches && !details.open) details.open = true; });
  if ('ResizeObserver' in window) {
    const observer = new ResizeObserver(offsets);
    observer.observe(topnav); observer.observe(summary);
  }
  let scheduled = false;
  function update() {
    scheduled = false;
    const threshold = parseFloat(getComputedStyle(document.body).getPropertyValue('--reading-scroll-offset')) + 8;
    let active = -1;
    chapters.forEach((chapter, i) => { if (chapter && chapter.getBoundingClientRect().top <= threshold) active = i; });
    if (scrollY + innerHeight >= document.documentElement.scrollHeight - 4) active = links.length - 1;
    links.forEach((link, i) => { if (i === active) link.setAttribute('aria-current', 'location'); else link.removeAttribute('aria-current'); });
    current.textContent = active < 0 ? 'Overview' : links[active].textContent;
  }
  function schedule() { if (!scheduled) { scheduled = true; requestAnimationFrame(update); } }
  addEventListener('scroll', schedule, {passive: true});
  addEventListener('resize', schedule);
  addEventListener('hashchange', schedule);
  toc.addEventListener('click', event => {
    const link = event.target.closest('a[href^="#"]');
    if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const target = document.getElementById(decodeURIComponent(link.hash.slice(1)));
    if (!target) return;
    event.preventDefault();
    if (narrow.matches) details.open = false;
    history.pushState(null, '', link.hash);
    target.setAttribute('tabindex', '-1'); target.focus({preventScroll: true});
    const offset = parseFloat(getComputedStyle(document.body).getPropertyValue('--reading-scroll-offset'));
    window.scrollTo({top: scrollY + target.getBoundingClientRect().top - offset, behavior: motion.matches ? 'instant' : 'smooth'});
    schedule();
  });
  details.addEventListener('keydown', event => {
    if (event.key === 'Escape' && narrow.matches) { details.open = false; summary.focus(); }
  });
  document.querySelectorAll('#main-content table').forEach(table => {
    const wrapper = document.createElement('div');
    wrapper.className = 'reading-table-scroll';
    const columns = Math.max(...Array.from(table.rows, row => Array.from(row.cells).reduce((n, cell) => n + cell.colSpan, 0)));
    if (columns <= 3) wrapper.classList.add('reading-table-compact');
    wrapper.setAttribute('role', 'region'); wrapper.setAttribute('aria-label', 'Scrollable data table');
    wrapper.tabIndex = 0; table.before(wrapper); wrapper.append(table);
  });
  addEventListener('load', () => {
    offsets();
    const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (target) target.scrollIntoView({behavior: 'instant', block: 'start'});
    update();
  });
  update();
})();
