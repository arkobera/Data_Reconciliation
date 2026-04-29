from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.reconcile import router as reconcile_router

app = FastAPI(
    title="Month-End Reconciliation API",
    description="Explains why payment platform transactions and bank settlements drift apart.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reconcile_router)
