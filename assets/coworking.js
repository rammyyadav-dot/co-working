(() => {
  const input = document.querySelector('#workspace-search');
  if (!input) return;
  const cards = [...document.querySelectorAll('[data-workspace]')];
  const buttons = [...document.querySelectorAll('[data-category-filter]')];
  const status = document.querySelector('#results-count');
  const more = document.querySelector('#workspace-more');
  const empty = document.querySelector('#workspace-empty');
  let category = 'all', limit = 12;
  function update() {
    const query = input.value.trim().toLocaleLowerCase('en-IN');
    const words = query.split(/\s+/).filter(Boolean);
    const matches = cards.filter(card => (category === 'all' || card.dataset.category === category) && words.every(word => card.dataset.search.toLocaleLowerCase('en-IN').includes(word)));
    cards.forEach(card => { card.hidden = true; });
    matches.slice(0, limit).forEach(card => { card.hidden = false; });
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.categoryFilter === category)));
    status.textContent = `${matches.length} ${matches.length === 1 ? 'option' : 'options'} found · Showing ${Math.min(matches.length, limit)}`;
    empty.hidden = matches.length !== 0;
    more.hidden = matches.length <= limit;
    more.textContent = `Show ${Math.min(12, matches.length - limit)} more options ↓`;
  }
  buttons.forEach(button => button.addEventListener('click', () => {
    category = button.dataset.categoryFilter; limit = 12;
    const hash = category === 'all' ? '#browse' : '#' + category;
    history.replaceState(null, '', hash);
    update();
  }));
  input.addEventListener('input', () => { limit = 12; update(); });
  more.addEventListener('click', () => {
    const previous = new Set(cards.filter(card => !card.hidden));
    limit += 12; update();
    const next = cards.find(card => !card.hidden && !previous.has(card));
    if (next) next.focus({ preventScroll: true });
  });
  document.querySelector('#workspace-reset').addEventListener('click', () => {
    input.value = ''; category = 'all'; limit = 12;
    history.replaceState(null, '', '#browse'); update(); input.focus();
  });
  function applyHash() {
    const candidate = location.hash.slice(1);
    if (buttons.some(button => button.dataset.categoryFilter === candidate)) { category = candidate; limit = 12; update(); }
  }
  addEventListener('hashchange', applyHash);
  applyHash(); update();
})();
