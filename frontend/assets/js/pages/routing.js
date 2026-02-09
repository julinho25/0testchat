import { api } from '../api.js';
import { setLoading, showToast } from '../components/ui.js';

export async function renderRouting() {
  const view = document.getElementById('view');
  view.innerHTML = `
    <div class="card">
      <h2>Roteirização</h2>
      <div class="form-grid">
        <label>Depósito
          <input type="text" id="routeDepot" placeholder="Depósito" />
        </label>
        <label>Data
          <input type="date" id="routeDate" />
        </label>
        <label>Turno
          <select id="routeShift">
            <option value="morning">Manhã</option>
            <option value="afternoon">Tarde</option>
            <option value="night">Noite</option>
          </select>
        </label>
      </div>
      <button class="btn primary" id="routeOptimize">Otimizar</button>
    </div>
    <div class="card">
      <h3>Status</h3>
      <div id="routeStatus">Nenhum job em execução.</div>
    </div>
    <div class="card">
      <h3>Mapa</h3>
      <div id="routeMap" style="height: 360px;"></div>
    </div>
  `;

  const map = L.map('routeMap').setView([-23.5505, -46.6333], 11);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(map);

  document.getElementById('routeOptimize').addEventListener('click', async () => {
    try {
      setLoading(true);
      const payload = {
        depot_id: document.getElementById('routeDepot').value,
        route_date: document.getElementById('routeDate').value,
        shift: document.getElementById('routeShift').value,
        delivery_ids: [],
        vehicle_ids: [],
        config: {
          fuel_price: 6.0,
          savings_method: 'baseline'
        }
      };
      const job = await api.createRouteJob(payload);
      pollJob(job.id);
    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setLoading(false);
    }
  });

  async function pollJob(jobId) {
    const statusEl = document.getElementById('routeStatus');
    statusEl.textContent = 'Job em execução...';
    const interval = setInterval(async () => {
      const job = await api.getRouteJob(jobId);
      statusEl.textContent = `Status: ${job.status}`;
      if (job.status === 'done' || job.status === 'failed') {
        clearInterval(interval);
        if (job.status === 'done') {
          const result = await api.getRouteResult(jobId);
          statusEl.textContent = `Concluído: ${result.routes.length} rotas geradas.`;
          result.routes.forEach(route => {
            if (route.polyline_geojson) {
              L.geoJSON(route.polyline_geojson, { color: '#2563eb' }).addTo(map);
            }
          });
        }
      }
    }, 2000);
  }
}
