import { api } from '../api.js';
import { setLoading, showToast } from '../components/ui.js';

export async function renderClients() {
  const view = document.getElementById('view');
  view.innerHTML = `
    <div class="card">
      <h2>Clientes</h2>
      <div class="form-grid">
        <label>Busca
          <input type="text" id="clientSearch" placeholder="Nome, CPF/CNPJ" />
        </label>
      </div>
      <button class="btn primary" id="clientFilter">Buscar</button>
    </div>
    <div class="card">
      <table class="table" id="clientTable"></table>
    </div>
  `;

  document.getElementById('clientFilter').addEventListener('click', loadClients);
  await loadClients();

  async function loadClients() {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        search: document.getElementById('clientSearch').value,
        page: 1,
        pageSize: 20
      });
      const data = await api.listClients(params.toString());
      const table = document.getElementById('clientTable');
      table.innerHTML = `
        <thead>
          <tr><th>Nome</th><th>Email</th><th>Telefone</th><th>Endereços</th></tr>
        </thead>
        <tbody>
          ${data.items.map(client => `
            <tr>
              <td>${client.name}</td>
              <td>${client.email || '-'}</td>
              <td>${client.phone || '-'}</td>
              <td>${client.address_count}</td>
            </tr>
          `).join('')}
        </tbody>
      `;
    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setLoading(false);
    }
  }
}
