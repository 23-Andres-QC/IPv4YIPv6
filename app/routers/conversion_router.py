"""
Router FastAPI para conversión IPv4 ↔ IPv6.
Endpoints:
  POST /api/convert/ipv4-to-ipv6
  POST /api/convert/ipv6-to-ipv4
Compatible con FastAPI y Python 3.12.
"""

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    ConversionRequest,
    ConversionIPv4ToIPv6Response,
    ConversionIPv6ToIPv4Response,
)
from app.services.conversion_service import ipv4_to_ipv6, ipv6_to_ipv4
from app.services import history_service

router = APIRouter(prefix="/api/convert", tags=["Conversión"])


@router.post(
    "/ipv4-to-ipv6",
    response_model=ConversionIPv4ToIPv6Response,
    summary="Convertir IPv4 → IPv6",
)
def convert_ipv4_to_ipv6(request: ConversionRequest):
    """
    Convierte una dirección IPv4 a sus representaciones IPv6.
    Retorna: IPv4-Mapped, IPv4-Compatible, 6to4 y Teredo.
    """
    try:
        result = ipv4_to_ipv6(request.ip)
        history_service.add_entry(
            operation="IPv4 → IPv6",
            input_data=request.ip,
            result_summary=f"Mapped: {result.ipv4_mapped}, 6to4: {result.six_to_four}",
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/ipv6-to-ipv4",
    response_model=ConversionIPv6ToIPv4Response,
    summary="Convertir IPv6 → IPv4",
)
def convert_ipv6_to_ipv4(request: ConversionRequest):
    """
    Intenta extraer una dirección IPv4 de una IPv6.
    Soporta: IPv4-Mapped (::ffff:), IPv4-Compatible (::), 6to4 (2002::).
    """
    try:
        result = ipv6_to_ipv4(request.ip)
        history_service.add_entry(
            operation="IPv6 → IPv4",
            input_data=request.ip,
            result_summary=f"Éxito: {result.success}, IPv4: {result.ipv4_address or 'N/A'}",
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
