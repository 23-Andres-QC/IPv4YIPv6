"""
Router FastAPI para monitoreo de tráfico de red en tiempo real.
Endpoint:
  GET /api/traffic   → snapshot de 1 segundo con velocidad por interfaz
Compatible con FastAPI y Python 3.12.
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import TrafficResponse
from app.services.traffic_service import get_traffic_stats
from app.services import history_service

router = APIRouter(prefix="/api/traffic", tags=["Tráfico de Red"])


@router.get(
    "",
    response_model=TrafficResponse,
    summary="Monitoreo de tráfico de red en tiempo real",
)
def traffic_stats():
    """
    Captura el tráfico de red durante ~1 segundo y calcula:

    - **bytes_sent / bytes_recv**: total acumulado por interfaz desde el arranque
    - **speed_send_kbps / speed_recv_kbps**: velocidad actual de envío/recepción
    - **packets_sent / packets_recv**: paquetes enviados y recibidos
    - **errin / errout**: errores de entrada/salida
    - **dropin / dropout**: paquetes descartados
    - **is_up**: estado de la interfaz (activa/inactiva)

    Llama a este endpoint de forma periódica (ej: cada 2 segundos) para
    obtener monitoreo continuo en tiempo real.
    """
    try:
        result = get_traffic_stats()
        history_service.add_entry(
            operation="Traffic Monitor",
            input_data="Sistema",
            result_summary=(
                f"Interfaces: {len(result.interfaces)} · "
                f"↑{result.total_speed_send_human} ↓{result.total_speed_recv_human}"
            ),
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener tráfico: {e}")
