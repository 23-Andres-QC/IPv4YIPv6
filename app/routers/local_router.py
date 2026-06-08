"""
Router FastAPI — Proxy al Agente Local de Windows.
Llama a http://host.docker.internal:8001 para obtener
las interfaces y el tráfico REALES del sistema operativo host.

host.docker.internal es la dirección especial que Docker Desktop
usa para alcanzar la máquina Windows donde corre el contenedor.

Endpoints:
  GET /api/local/status      → verifica si el agente local está activo
  GET /api/local/interfaces  → interfaces reales de Windows
  GET /api/local/traffic     → tráfico en tiempo real de Windows
"""

import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/local", tags=["Red Local (Windows)"])

# Dirección del agente local desde dentro del contenedor Docker
AGENT_URL = "http://host.docker.internal:8001"
TIMEOUT   = 15.0  # segundos (tráfico tarda ~1 seg + margen)


def _agent_get(path: str) -> dict:
    """Realiza GET al agente local y retorna el JSON."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            resp = client.get(f"{AGENT_URL}{path}")
            resp.raise_for_status()
            return resp.json()
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail=(
                "El agente local no está corriendo. "
                "Ejecuta en Windows: python local_agent.py"
            ),
        )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Timeout al contactar el agente local.")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error en agente local: {e}")


@router.get("/status", summary="Verificar agente local")
def local_status():
    """
    Verifica si el agente local está corriendo en Windows.
    Retorna información del host: nombre, SO, psutil disponible.
    """
    return _agent_get("/health")


@router.get("/interfaces", summary="Interfaces reales de Windows")
def local_interfaces():
    """
    Retorna todas las interfaces de red reales del sistema Windows:
    Wi-Fi, Ethernet, Bluetooth, vEthernet, Loopback, etc.

    **Requiere** que `local_agent.py` esté corriendo en Windows.
    """
    return _agent_get("/interfaces")


@router.get("/traffic", summary="Tráfico real de Windows en tiempo real")
def local_traffic():
    """
    Captura ~1 segundo de tráfico de cada interfaz Windows real
    y calcula la velocidad actual (KB/s o MB/s).

    **Requiere** que `local_agent.py` esté corriendo en Windows.
    """
    return _agent_get("/traffic")
