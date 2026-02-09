import { api } from '../api.js';
import { createCard, setLoading, showToast } from '../components/ui.js';

export async function renderDashboard() {
  const view = document.getElementById('view');
  view.innerHTML = `
    <div class="card">
      <h2>Dashboard Financeiro</h2>
      <div class="form-grid">
        <label>Mês
          <input type="month" id="dashMonth" />
        </label>
        <label>Cliente
          <input type="text" id="dashClient" placeholder="Nome ou ID" />
        </label>
        <label>Base/Depósito
          <input type="text" id="dashDepot" placeholder="Depósito" />
        </label>
        <label>Método de economia
          <select id="dashMethod">
            <option value="baseline">Custo otimizado vs baseline</option>
            <option value="real">Previsto vs real</option>
          </select>
        </label>
      </div>
      <button class="btn primary" id="dashFilter">Aplicar filtros</button>
    </div>
    <div class="cards-grid" id="dashKpis"></div>
    <div class="card">
      <canvas id="dashChart" height="120"></canvas>
    </div>
    <div class="card">
      <h3>Top clientes</h3>
      <table class="table" id="dashTopTable"></table>
    </div>
  `;

  const monthInput = document.getElementById('dashMonth');
  monthInput.value = new Date().toISOString().slice(0, 7);

  document.getElementById('dashFilter').addEventListener('click', () => loadDashboard());

  await loadDashboard();

  async function loadDashboard() {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        month: monthInput.value,
        client: document.getElementById('dashClient').value,
        depot: document.getElementById('dashDepot').value,
        method: document.getElementById('dashMethod').value
      });
      const data = await api.listFinance(params.toString());
      const kpis = document.getElementById('dashKpis');
      kpis.innerHTML = '';
      kpis.append(
        createCard('Valor gasto', data.kpis.cost_total, 'No mês'),
        createCard('Valor a receber', data.kpis.to_receive, 'Em aberto'),
        createCard('Recebido mês', data.kpis.received_month, 'Pagamentos no mês'),
        createCard('Economia', data.kpis.savings, 'Método selecionado')
      );

      const topTable = document.getElementById('dashTopTable');
      topTable.innerHTML = `
        <thead>
          <tr><th>Cliente</th><th>Faturamento</th><th>Custo</th></tr>
        </thead>
        <tbody>
          ${data.top_clients.map(row => `
            <tr>
              <td>${row.client}</td>
              <td>${row.revenue}</td>
              <td>${row.cost}</td>
            </tr>
          `).join('')}
        </tbody>
      `;

      const ctx = document.getElementById('dashChart').getContext('2d');
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.daily.map(item => item.day),
          datasets: [
            {
              label: 'Custos',
              data: data.daily.map(item => item.cost),
              borderColor: '#ef4444',
              backgroundColor: 'rgba(239, 68, 68, 0.2)'
            },
            {
              label: 'Recebimentos',
              data: data.daily.map(item => item.received),
              borderColor: '#10b981',
              backgroundColor: 'rgba(16, 185, 129, 0.2)'
            }
          ]
        }
      });
    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setLoading(false);
    }
  }
}
