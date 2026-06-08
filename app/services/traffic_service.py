"""
Servicio de monitoreo de tráfico de red en tiempo real.
Usa psutil.net_io_counters(pernic=True) para obtener estadísticas
por interfaz y calcula velocidades comparando snapshots consecutivos.
Compatible con Python 3.12 y Docker (no requiere privilegios root).
"""

import time
from datetime import datetime
from typing import Dict, Optional
import socket

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from app.models.schemas import InterfaceTraffic, TrafficResponse

# ─────────────────────────────────────────────
#  Snapshot anterior (en memoria de proceso)
# ─────────────────────────────────────────────
_prev_snapshot: Optional[Dict] = None
_prev_time: float = 0.0


def _human_bytes(n: float) -> str:
    """Convierte bytes a string legible: B, KB, MB, GB."""
    if n < 1024:
        return f"{n:.0f} B"
    elif n < 1024 ** 2:
        return f"{n / 1024:.1f} KB"
    elif n < 1024 ** 3:
        return f"{n / 1024**2:.1f} MB"
    else:
        return f"{n / 1024**3:.2f} GB"


def _human_speed(kbps: float) -> str:
    """Convierte KB/s a string legible: KB/s, MB/s, GB/s."""
    if kbps < 1024:
        return f"{kbps:.1f} KB/s"
    elif kbps < 1024 ** 2:
        return f"{kbps / 1024:.2f} MB/s"
    else:
        return f"{kbps / 1024**2:.2f} GB/s"


def get_traffic_stats() -> TrafficResponse:
    """
    Toma dos snapshots de contadores de red separados por ~1 segundo
    y calcula la velocidad actual de cada interfaz.

    Campos retornados por interfaz:
      - bytes_sent / bytes_recv       → total acumulado desde el arranque
      - packets_sent / packets_recv   → paquetes acumulados
      - errin / errout                → errores de red
      - dropin / dropout              → paquetes descartados
      - speed_send_kbps               → velocidad de envío calculada
      - speed_recv_kbps               → velocidad de recepción calculada
    """
    global _prev_snapshot, _prev_time

    if not PSUTIL_AVAILABLE:
        return TrafficResponse(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            interval_seconds=0,
            interfaces=[],
            total_bytes_sent=0,
            total_bytes_recv=0,
            total_speed_send_human="N/A",
            total_speed_recv_human="N/A",
        )

    # ── Obtener estado de interfaces (up/down) ──
    iface_stats = psutil.net_if_stats()

    # ── Primer snapshot ──
    snap1 = psutil.net_io_counters(pernic=True)
    t1 = time.monotonic()

    # ── Esperar intervalo de medición ──
    time.sleep(1.0)

    # ── Segundo snapshot ──
    snap2 = psutil.net_io_counters(pernic=True)
    t2 = time.monotonic()
    interval = t2 - t1  # segundos reales transcurridos

    # ── Calcular métricas por interfaz ──
    interfaces_out: list[InterfaceTraffic] = []
    total_sent = 0
    total_recv = 0
    total_speed_send = 0.0
    total_speed_recv = 0.0

    for name, c2 in snap2.items():
        c1 = snap1.get(name)
        if c1 is None:
            continue

        # Bytes delta en el intervalo
        delta_sent = max(0, c2.bytes_sent - c1.bytes_sent)
        delta_recv = max(0, c2.bytes_recv - c1.bytes_recv)

        # Velocidad en KB/s
        speed_send = (delta_sent / 1024) / interval
        speed_recv = (delta_recv / 1024) / interval

        # Estado de la interfaz
        is_up = iface_stats[name].isup if name in iface_stats else True

        total_sent += c2.bytes_sent
        total_recv += c2.bytes_recv
        total_speed_send += speed_send
        total_speed_recv += speed_recv

        interfaces_out.append(InterfaceTraffic(
            name=name,
            bytes_sent=c2.bytes_sent,
            bytes_recv=c2.bytes_recv,
            packets_sent=c2.packets_sent,
            packets_recv=c2.packets_recv,
            errin=c2.errin,
            errout=c2.errout,
            dropin=c2.dropin,
            dropout=c2.dropout,
            speed_send_kbps=round(speed_send, 2),
            speed_recv_kbps=round(speed_recv, 2),
            speed_send_human=_human_speed(speed_send),
            speed_recv_human=_human_speed(speed_recv),
            total_sent_human=_human_bytes(c2.bytes_sent),
            total_recv_human=_human_bytes(c2.bytes_recv),
            is_up=is_up,
        ))

    # Ordenar: primero las que tienen tráfico activo
    interfaces_out.sort(
        key=lambda x: (x.speed_send_kbps + x.speed_recv_kbps),
        reverse=True
    )

    return TrafficResponse(
        timestamp=datetime.now().isoformat(timespec="seconds"),
        interval_seconds=round(interval, 3),
        interfaces=interfaces_out,
        total_bytes_sent=total_sent,
        total_bytes_recv=total_recv,
        total_speed_send_human=_human_speed(total_speed_send),
        total_speed_recv_human=_human_speed(total_speed_recv),
    )
