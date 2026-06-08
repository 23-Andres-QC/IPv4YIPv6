"""
Router FastAPI para detección de interfaces de red del sistema.
Endpoint:
  GET /api/interfaces
Compatible con FastAPI y Python 3.12.
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import InterfacesResponse
from app.services.interfaces_service import get_interfaces
from app.services import history_service

router = APIRouter(prefix="/api/interfaces", tags=["Interfaces"])


@router.get("", response_model=InterfacesResponse, summary="Detectar interfaces de red")
def list_interfaces():
    """
    Detecta y lista todas las interfaces de red del sistema operativo.
    Retorna: nombre, IPv4, IPv6, MAC, máscara y CIDR de cada interfaz.
    """
    try:
        ifaces = get_interfaces()
        history_service.add_entry(
            operation="Detectar Interfaces",
            input_data="Sistema",
            result_summary=f"Interfaces encontradas: {len(ifaces)}",
        )
        return InterfacesResponse(interfaces=ifaces, total=len(ifaces))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al detectar interfaces: {e}")
