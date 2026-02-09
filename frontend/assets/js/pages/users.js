import { setLoading, showToast } from '../components/ui.js';

export async function renderUsers() {
  const view = document.getElementById('view');
  view.innerHTML = `
    <div class="card">
      <h2>Usuários</h2>
      <p>Gerencie usuários administrativos e permissões no backend (Admin).</p>
    </div>
  `;
  try {
    setLoading(true);
  } catch (error) {
    showToast(error.message, 'error');
  } finally {
    setLoading(false);
  }
}
