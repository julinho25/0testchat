# LogiFlow MVP

Sistema web para operação logística com roteirização inteligente, controle financeiro e gestão operacional.

## Stack
- Front-end: HTML + CSS + JS (vanilla), Chart.js, Leaflet, SheetJS.
- Back-end: FastAPI + SQLAlchemy + Alembic.
- Banco: PostgreSQL.
- Background jobs: Celery + Redis.
- Roteirização: OR-Tools.
- OSRM: self-hosted via Docker.

## Como rodar

1. Gere os dados do OSRM (veja `osrm/README.md`).
2. Suba os serviços:

```bash
docker-compose -f infra/docker-compose.yml up --build
```

3. Rode as migrations e seed:

```bash
docker-compose -f infra/docker-compose.yml exec api alembic upgrade head

docker-compose -f infra/docker-compose.yml exec api python -m seed.seed
```

## Acessos
- Front-end: http://localhost:8080
- API + Swagger: http://localhost:8000/docs

Usuário padrão:
- email: `admin@logiflow.com`
- senha: `admin123`

## Importação
- Frota: `/vehicles/import` com CSV (campos: `plate,vehicle_type,capacity_kg,status,tags`).
- Entregas: `/deliveries/import` com CSV (campos: `order_id,client,lat,lng,weight_kg,volume_m3,revenue_expected`).

## Roteirização
1. Acesse a página **Roteirização**.
2. Selecione base/data/turno e clique em **Otimizar**.
3. O front faz polling a cada 2s em `/routing/jobs/{id}` até finalizar.

## Configurações de custos
- Preço do combustível e método de economia são enviados no payload de criação do job em `config`.
- Custo fixo mensal é rateado por dia no worker (`fixed_cost_value`).

## Limitações e próximos passos
- Geocoding usa Nominatim (limites de requisições). Em produção, plugue um provedor dedicado.
- VRP atual utiliza amostra pequena de entregas. Expandir para multi-vehicle e restrições completas.
- Export PDF simplificado: em produção, usar serviço dedicado.

## Checklist do MVP
- [x] Autenticação JWT + RBAC
- [x] CRUD principais e paginação
- [x] Roteirização em background com OR-Tools
- [x] OSRM para matriz real
- [x] Dashboard financeiro e KPIs
- [x] Importação CSV
- [x] Docker Compose completo

## Teste rápido
```bash
curl http://localhost:8000/
```

## Script utilitário: auto clique em números

Foi adicionado um script utilitário em `frontend/assets/js/autoClickNumbers.js` para automatizar cliques em números renderizados em uma `div`.

Uso básico no console do navegador:

```js
const stop = startAutoClickNumbers({
  containerSelector: '.sua-div-com-numeros',
  numberSelector: '.item-numero', // opcional
  numbersToClick: [12, 28, 35],
  intervalMs: 450,
  debug: true,
});

// quando quiser parar
stop();
```

Dica: descubra os seletores corretos com o inspetor do navegador.

## Bot em Python: auto clique em números

Também foi adicionado um bot em Python: `tools/auto_click_bot.py`.

### Instalação

```bash
pip install selenium webdriver-manager
```

### Execução

```bash
python tools/auto_click_bot.py \
  --url "https://bravo.bet.br/cassino-ao-vivo/roleta-brasileira/play" \
  --container ".racetrack-table" \
  --item ".table-cell" \
  --numbers 12 28 35 \
  --interval 0.45 \
  --debug
```

Observações:
- Ajuste `--container` e `--item` conforme os seletores reais da página.
- Interrompa com `Ctrl+C`.
