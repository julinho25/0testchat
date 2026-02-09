import { api } from '../api.js';
import { setLoading, showToast } from '../components/ui.js';

export async function renderFleet() {
  const view = document.getElementById('view');
  view.innerHTML = `
    <div class="card">
      <h2>Frota</h2>
      <div class="form-grid">
        <label>Status
          <select id="fleetStatus">
            <option value="">Todos</option>
            <option value="active">Ativo</option>
            <option value="maintenance">Manutenção</option>
            <option value="inactive">Inativo</option>
          </select>
        </label>
        <label>Tipo
          <input type="text" id="fleetType" placeholder="VAN, TRUCK..." />
        </label>
        <label>Tag
          <input type="text" id="fleetTag" placeholder="zona restrita" />
        </label>
      </div>
      <button class="btn primary" id="fleetFilter">Buscar</button>
    </div>
    <div class="card">
      <h3>Lista</h3>
      <table class="table" id="fleetTable"></table>
    </div>
  `;

  document.getElementById('fleetFilter').addEventListener('click', loadFleet);
  await loadFleet();

  async function loadFleet() {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        status: document.getElementById('fleetStatus').value,
        type: document.getElementById('fleetType').value,
        tag: document.getElementById('fleetTag').value,
        page: 1,
        pageSize: 20
      });
      const data = await api.listVehicles(params.toString());
      const table = document.getElementById('fleetTable');
      table.innerHTML = `
        <thead>
          <tr><th>Placa</th><th>Tipo</th><th>Status</th><th>Capacidade (kg)</th><th>Tags</th></tr>
        </thead>
        <tbody>
          ${data.items.map(vehicle => `
            <tr>
              <td>${vehicle.plate}</td>
              <td>${vehicle.vehicle_type}</td>
              <td><span class="badge">${vehicle.status}</span></td>
              <td>${vehicle.capacity_kg}</td>
              <td>${vehicle.tags?.join(', ') || '-'}</td>
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
