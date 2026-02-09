const API_BASE = import.meta.env?.VITE_API_URL || 'http://localhost:8000';

const getTokens = () => JSON.parse(localStorage.getItem('tokens') || '{}');
const setTokens = (tokens) => localStorage.setItem('tokens', JSON.stringify(tokens));
const clearTokens = () => localStorage.removeItem('tokens');

async function request(path, options = {}) {
  const { accessToken } = getTokens();
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers
  });
  if (response.status === 401) {
    clearTokens();
    window.location.reload();
  }
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: 'Erro inesperado' }));
    throw new Error(payload.detail || 'Erro inesperado');
  }
  return response.json();
}

export const api = {
  login: async (email, password) => {
    const data = await request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    setTokens(data);
    return data;
  },
  refresh: async () => request('/auth/refresh', { method: 'POST' }),
  logout: async () => {
    clearTokens();
  },
  me: async () => request('/users/me'),
  listVehicles: async (params = '') => request(`/vehicles?${params}`),
  listClients: async (params = '') => request(`/clients?${params}`),
  listDeliveries: async (params = '') => request(`/deliveries?${params}`),
  listFinance: async (params = '') => request(`/finance/dashboard?${params}`),
  createRouteJob: async (payload) => request('/routing/jobs', {
    method: 'POST',
    body: JSON.stringify(payload)
  }),
  getRouteJob: async (id) => request(`/routing/jobs/${id}`),
  getRouteResult: async (id) => request(`/routing/jobs/${id}/result`)
};

export const authStore = {
  getTokens,
  setTokens,
  clearTokens
};
