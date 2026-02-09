export function showToast(message, type = 'info') {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.remove('hidden');
  toast.style.background = type === 'error' ? '#ef4444' : '#0f172a';
  setTimeout(() => toast.classList.add('hidden'), 3000);
}

export function setLoading(visible) {
  const loader = document.getElementById('loader');
  loader.classList.toggle('hidden', !visible);
}

export function createCard(title, value, subtitle = '') {
  const card = document.createElement('div');
  card.className = 'card';
  card.innerHTML = `
    <div class="muted">${title}</div>
    <div class="kpi-value">${value}</div>
    <div class="muted">${subtitle}</div>
  `;
  return card;
}
