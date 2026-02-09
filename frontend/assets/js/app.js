import { api, authStore } from './api.js';
import { registerRoute, renderRoute, navigate, setOnChange } from './router.js';
import { renderDashboard } from './pages/dashboard.js';
import { renderFleet } from './pages/fleet.js';
import { renderClients } from './pages/clients.js';
import { renderDeliveries } from './pages/deliveries.js';
import { renderRouting } from './pages/routing.js';
import { renderFinance } from './pages/finance.js';
import { renderUsers } from './pages/users.js';
import { showToast } from './components/ui.js';

const menuConfig = [
  { path: '/', label: 'Dashboard', roles: ['Admin', 'Financeiro', 'Operacao', 'Leitura'] },
  { path: '/frota', label: 'Frota', roles: ['Admin', 'Operacao'] },
  { path: '/clientes', label: 'Clientes', roles: ['Admin', 'Operacao'] },
  { path: '/entregas', label: 'Entregas', roles: ['Admin', 'Operacao'] },
  { path: '/roteirizacao', label: 'Roteirização', roles: ['Admin', 'Operacao'] },
  { path: '/financeiro', label: 'Financeiro', roles: ['Admin', 'Financeiro'] },
  { path: '/usuarios', label: 'Usuários', roles: ['Admin'] }
];

registerRoute('/', renderDashboard, 'Dashboard');
registerRoute('/frota', renderFleet, 'Frota');
registerRoute('/clientes', renderClients, 'Clientes');
registerRoute('/entregas', renderDeliveries, 'Entregas');
registerRoute('/roteirizacao', renderRouting, 'Roteirização');
registerRoute('/financeiro', renderFinance, 'Financeiro');
registerRoute('/usuarios', renderUsers, 'Usuários');

const authEl = document.getElementById('auth');
const appEl = document.getElementById('app');
const menuEl = document.getElementById('menu');
const pageTitle = document.getElementById('pageTitle');
const userChip = document.getElementById('userChip');

function setAuthScreen(visible) {
  authEl.classList.toggle('hidden', !visible);
  appEl.classList.toggle('hidden', visible);
}

async function bootstrap() {
  try {
    const tokens = authStore.getTokens();
    if (!tokens.accessToken) {
      setAuthScreen(true);
      return;
    }
    const me = await api.me();
    userChip.textContent = `${me.name} · ${me.role}`;
    renderMenu(me.role);
    setAuthScreen(false);
    renderRoute();
  } catch (error) {
    authStore.clearTokens();
    setAuthScreen(true);
  }
}

function renderMenu(role) {
  menuEl.innerHTML = '';
  menuConfig.filter(item => item.roles.includes(role)).forEach(item => {
    const link = document.createElement('a');
    link.href = item.path;
    link.textContent = item.label;
    link.className = 'menu-item';
    link.addEventListener('click', (event) => {
      event.preventDefault();
      navigate(item.path);
    });
    menuEl.appendChild(link);
  });
}

setOnChange((route) => {
  pageTitle.textContent = route.title;
  document.querySelectorAll('.menu-item').forEach(link => {
    link.classList.toggle('active', link.getAttribute('href') === window.location.pathname);
  });
});

const loginForm = document.getElementById('loginForm');
loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(loginForm);
  const email = formData.get('email');
  const password = formData.get('password');
  try {
    await api.login(email, password);
    await bootstrap();
  } catch (error) {
    document.getElementById('loginError').textContent = error.message;
  }
});

const logoutBtn = document.getElementById('logoutBtn');
logoutBtn.addEventListener('click', async () => {
  await api.logout();
  showToast('Sessão encerrada');
  window.location.reload();
});

const toggleSidebar = document.getElementById('toggleSidebar');
toggleSidebar.addEventListener('click', () => {
  document.getElementById('sidebar').classList.toggle('open');
});

bootstrap();
