from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, users, vehicles, clients, deliveries, routing, finance, audit

app = FastAPI(title="LogiFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] ,
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"] ,
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(vehicles.router)
app.include_router(clients.router)
app.include_router(deliveries.router)
app.include_router(routing.router)
app.include_router(finance.router)
app.include_router(audit.router)

@app.get("/")
def root():
    return {"status": "ok"}
