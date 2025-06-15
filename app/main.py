from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes import portfolios
from app import deps

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Middleware (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(portfolios.router)
