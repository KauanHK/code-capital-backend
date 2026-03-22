from fastapi import FastAPI

from app.config import settings
from app.routers import categories, clients, services, transactions

app = FastAPI(title=settings.API_TITLE, version=settings.API_VERSION)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(categories.router)
app.include_router(services.router)
app.include_router(clients.router)
app.include_router(transactions.router)
