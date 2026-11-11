(() => {
  const input = document.querySelector('#guide-search');
  const buttons = [...document.querySelectorAll('[data-filter]')];
  const cards = [...document.querySelectorAll('[data-guide]')];
  let category = 'all';
  function filter() {
    const query = input.value.toLowerCase().trim();
    let visible = 0;
    for (const card of cards) {
      const matches = (category === 'all' || card.dataset.category === category) && card.textContent.toLowerCase().includes(query);
      card.hidden = !matches;
      if (matches) visible++;
    }
    document.querySelector('#result-count').textContent = `${visible} of ${cards.length} guides`;
    document.querySelector('#no-results').hidden = visible !== 0;
  }
  input.addEventListener('input', filter);
  for (const button of buttons) button.addEventListener('click', () => {
    category = button.dataset.filter;
    for (const item of buttons) item.setAttribute('aria-pressed', String(item === button));
    filter();
  });
})();
