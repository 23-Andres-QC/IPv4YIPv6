"""
Router FastAPI para operaciones IPv4.
Endpoints:
  POST /api/ipv4/calculate
  GET  /api/ipv4/info/{ip}
Compatible con FastAPI y Python 3.12.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models.schemas import IPv4Request, IPv4Response
from app.services.ipv4_service import calculate_ipv4
from app.services import history_service

router = APIRouter(prefix="/api/ipv4", tags=["IPv4"])


@router.post("/calculate", response_model=IPv4Response, summary="Calcular subred IPv4")
def calculate_subnet(request: IPv4Request):
    """
    Calcula todos los parámetros de una subred IPv4.

    - **ip**: Dirección IPv4 base (ej: 192.168.1.0)
    - **mask**: Máscara decimal opcional (ej: 255.255.255.0)
    - **cidr**: Prefijo CIDR opcional (ej: 24)

    Si no se provee ni máscara ni CIDR, se usa /32.
    """
    if request.mask is None and request.cidr is None:
        request = request.model_copy(update={"cidr": 32})
    try:
        result = calculate_ipv4(request.ip, request.mask, request.cidr)
        history_service.add_entry(
            operation="IPv4 Calculate",
            input_data=f"{request.ip}/{request.cidr or request.mask}",
            result_summary=f"Red: {result.network_address}/{result.cidr}, Hosts: {result.usable_hosts}",
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/info/{ip}", response_model=IPv4Response, summary="Info rápida de IPv4")
def quick_info(
    ip: str,
    cidr: Optional[int] = Query(None, ge=0, le=32, description="Prefijo CIDR"),
):
    """
    Obtiene información de una dirección IPv4 con prefijo CIDR opcional.
    Si no se provee CIDR se usa /32.
    """
    try:
        result = calculate_ipv4(ip, cidr=cidr if cidr is not None else 32)
        history_service.add_entry(
            operation="IPv4 Info",
            input_data=f"{ip}/{cidr or 32}",
            result_summary=f"Tipo: {result.classification}, Red: {result.network_address}",
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
