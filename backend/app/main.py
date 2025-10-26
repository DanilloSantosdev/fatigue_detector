"""
FastAPI - Sistema de Detecção de Fadiga
Backend principal da aplicação
"""
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from .database import init_db
from .api import vehicles, alerts, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação"""
    # Startup
    print("🚀 Iniciando Sistema de Detecção de Fadiga...")
    
    # Criar diretório de uploads se não existir
    uploads_dir = Path(__file__).parent.parent.parent / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    print(f"📁 Diretório de uploads: {uploads_dir}")
    
    # Inicializar banco de dados
    try:
        await init_db()
        print("✅ Backend iniciado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        raise
    
    yield
    
    # Shutdown
    print("👋 Encerrando sistema...")


# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema de Detecção de Fadiga",
    description="API para gerenciamento de alertas de fadiga em veículos",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar diretório de uploads como estático
uploads_dir = Path(__file__).parent.parent.parent / "uploads"
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Incluir rotas
app.include_router(vehicles.router)
app.include_router(alerts.router)
app.include_router(reports.router)


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Sistema de Detecção de Fadiga - API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para exceções não tratadas"""
    print(f"❌ Erro não tratado: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor",
            "error": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload
    )

