import { api } from '../api.js';
import { setLoading, showToast } from '../components/ui.js';

export async function renderFinance() {
  const view = document.getElementById('view');
  view.innerHTML = `
    <div class="card">
      <h2>Financeiro</h2>
      <div class="form-grid">
        <label>Mês
          <input type="month" id="financeMonth" />
        </label>
        <label>Status
          <select id="financeStatus">
            <option value="">Todos</option>
            <option value="open">Em aberto</option>
            <option value="paid">Pago</option>
          </select>
        </label>
      </div>
      <button class="btn primary" id="financeFilter">Buscar</button>
    </div>
    <div class="card">
      <table class="table" id="financeTable"></table>
    </div>
  `;

  const monthInput = document.getElementById('financeMonth');
  monthInput.value = new Date().toISOString().slice(0, 7);

  document.getElementById('financeFilter').addEventListener('click', loadFinance);
  await loadFinance();

  async function loadFinance() {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        month: monthInput.value,
        status: document.getElementById('financeStatus').value,
        page: 1,
        pageSize: 20
      });
      const data = await api.listFinance(params.toString());
      const table = document.getElementById('financeTable');
      table.innerHTML = `
        <thead>
          <tr><th>Cliente</th><th>Valor</th><th>Status</th><th>Vencimento</th></tr>
        </thead>
        <tbody>
          ${data.invoices.map(inv => `
            <tr>
              <td>${inv.client}</td>
              <td>${inv.amount}</td>
              <td><span class="badge">${inv.status}</span></td>
              <td>${inv.due_date}</td>
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
