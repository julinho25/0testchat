const routes = {};
let onChange = () => {};

export function registerRoute(path, renderer, title) {
  routes[path] = { renderer, title };
}

export function setOnChange(handler) {
  onChange = handler;
}

export function navigate(path) {
  window.history.pushState({}, '', path);
  renderRoute();
}

export function renderRoute() {
  const path = window.location.pathname || '/';
  const route = routes[path] || routes['/'];
  if (!route) return;
  onChange(route);
  route.renderer();
}

window.addEventListener('popstate', renderRoute);
