"""
Router FastAPI para operaciones IPv6.
Endpoints:
  POST /api/ipv6/calculate
  GET  /api/ipv6/info/{ip}
Compatible con FastAPI y Python 3.12.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models.schemas import IPv6Request, IPv6Response
from app.services.ipv6_service import calculate_ipv6
from app.services import history_service

router = APIRouter(prefix="/api/ipv6", tags=["IPv6"])


@router.post("/calculate", response_model=IPv6Response, summary="Calcular red IPv6")
def calculate_network(request: IPv6Request):
    """
    Calcula los parámetros de una dirección/red IPv6.

    - **ip**: Dirección IPv6 (ej: 2001:db8::)
    - **prefix**: Longitud del prefijo (ej: 64). Defecto: 128
    """
    try:
        result = calculate_ipv6(request.ip, request.prefix)
        history_service.add_entry(
            operation="IPv6 Calculate",
            input_data=f"{request.ip}/{request.prefix or 128}",
            result_summary=f"Tipo: {result.ip_type}, Alcance: {result.scope}",
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/info/{ip}", response_model=IPv6Response, summary="Info rápida de IPv6")
def quick_info(
    ip: str,
    prefix: Optional[int] = Query(None, ge=0, le=128, description="Longitud del prefijo"),
):
    """
    Obtiene información de una dirección IPv6.
    Si no se provee prefix se usa /128.
    """
    try:
        result = calculate_ipv6(ip, prefix)
        history_service.add_entry(
            operation="IPv6 Info",
            input_data=f"{ip}/{prefix or 128}",
            result_summary=f"Tipo: {result.ip_type}, Comprimida: {result.compressed}",
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
