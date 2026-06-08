"""
Router FastAPI para historial de consultas en memoria.
Endpoints:
  GET    /api/history
  DELETE /api/history
Compatible con FastAPI y Python 3.12.
"""

from fastapi import APIRouter
from app.models.schemas import HistoryResponse
from app.services import history_service

router = APIRouter(prefix="/api/history", tags=["Historial"])


@router.get("", response_model=HistoryResponse, summary="Obtener historial de consultas")
def get_history():
    """
    Retorna el historial completo de consultas realizadas durante la sesión.
    El historial se almacena en memoria y se pierde al reiniciar el servidor.
    """
    return history_service.get_history()


@router.delete("", summary="Limpiar historial")
def clear_history():
    """
    Elimina todas las entradas del historial en memoria.
    """
    return history_service.clear_history()
