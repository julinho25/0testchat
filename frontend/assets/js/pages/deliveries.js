import { api } from '../api.js';
import { setLoading, showToast } from '../components/ui.js';

export async function renderDeliveries() {
  const view = document.getElementById('view');
  view.innerHTML = `
    <div class="card">
      <h2>Entregas</h2>
      <div class="form-grid">
        <label>Status
          <select id="deliveryStatus">
            <option value="">Todos</option>
            <option value="pending">Pendente</option>
            <option value="routed">Roteirizado</option>
            <option value="on_route">Em rota</option>
            <option value="delivered">Entregue</option>
          </select>
        </label>
        <label>Pedido
          <input type="text" id="deliveryOrder" placeholder="Order ID" />
        </label>
      </div>
      <button class="btn primary" id="deliveryFilter">Buscar</button>
    </div>
    <div class="card">
      <table class="table" id="deliveryTable"></table>
    </div>
  `;

  document.getElementById('deliveryFilter').addEventListener('click', loadDeliveries);
  await loadDeliveries();

  async function loadDeliveries() {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        status: document.getElementById('deliveryStatus').value,
        order_id: document.getElementById('deliveryOrder').value,
        page: 1,
        pageSize: 20
      });
      const data = await api.listDeliveries(params.toString());
      const table = document.getElementById('deliveryTable');
      table.innerHTML = `
        <thead>
          <tr><th>Pedido</th><th>Cliente</th><th>Status</th><th>Peso</th><th>Receita</th></tr>
        </thead>
        <tbody>
          ${data.items.map(item => `
            <tr>
              <td>${item.order_id}</td>
              <td>${item.client_name}</td>
              <td><span class="badge">${item.status}</span></td>
              <td>${item.weight_kg}</td>
              <td>${item.revenue_expected}</td>
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
