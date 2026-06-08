"""
IP Manager — Agente Local de Red (Windows)
==========================================
Corre DIRECTAMENTE en Windows (fuera de Docker).
Expone las interfaces y el tráfico REAL del sistema operativo
para que el contenedor Docker pueda consultarlos.

Instalación (una sola vez, en terminal Windows):
    pip install fastapi uvicorn psutil

Ejecución:
    python local_agent.py

Queda escuchando en http://localhost:8001
Docker lo alcanza en http://host.docker.internal:8001
"""

import time
import socket
import ipaddress
from datetime import datetime
from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("[WARN] psutil no instalado. Instala con: pip install psutil")

# ─────────────────────────────────────────────
#  App FastAPI del agente
# ─────────────────────────────────────────────
agent = FastAPI(
    title="IP Manager — Local Agent",
    description="Agente local que expone interfaces y tráfico reales de Windows.",
    version="1.0.0",
    docs_url="/docs",
)

agent.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
#  Utilidades
# ─────────────────────────────────────────────

def _cidr_from_netmask(netmask: str) -> Optional[int]:
    try:
        return ipaddress.IPv4Network(f"0.0.0.0/{netmask}", strict=False).prefixlen
    except Exception:
        return None


def _human_bytes(n: float) -> str:
    if n < 1024:
        return f"{n:.0f} B"
    elif n < 1024 ** 2:
        return f"{n / 1024:.1f} KB"
    elif n < 1024 ** 3:
        return f"{n / 1024**2:.1f} MB"
    else:
        return f"{n / 1024**3:.2f} GB"


def _human_speed(kbps: float) -> str:
    if kbps < 1024:
        return f"{kbps:.1f} KB/s"
    elif kbps < 1024 ** 2:
        return f"{kbps / 1024:.2f} MB/s"
    else:
        return f"{kbps / 1024**2:.2f} GB/s"


# ─────────────────────────────────────────────
#  Endpoint: health
# ─────────────────────────────────────────────

@agent.get("/health")
def health():
    return {
        "status": "ok",
        "agent": "IP Manager Local Agent",
        "host": socket.gethostname(),
        "psutil": PSUTIL_AVAILABLE,
    }


# ─────────────────────────────────────────────
#  Endpoint: interfaces reales de Windows
# ─────────────────────────────────────────────

@agent.get("/interfaces")
def get_interfaces():
    """
    Retorna TODAS las interfaces de red del sistema Windows,
    incluyendo las desconectadas (sin IP asignada):
    Wi-Fi, Ethernet, Bluetooth, vEthernet, Loopback, etc.
    """
    if not PSUTIL_AVAILABLE:
        return {"error": "psutil no disponible", "interfaces": [], "total": 0}

    # net_if_stats() devuelve TODAS las interfaces aunque estén desconectadas
    stats  = psutil.net_if_stats()
    # net_if_addrs() solo tiene interfaces con al menos una dirección
    addrs  = psutil.net_if_addrs()
    io_all = psutil.net_io_counters(pernic=True)
    result = []

    # Iterar por stats para incluir también las que no tienen dirección
    for name in stats:
        addr_list = addrs.get(name, [])

        ipv4 = None
        ipv6 = None
        mac  = None
        netmask = None
        cidr = None

        for addr in addr_list:
            if addr.family == socket.AF_INET:
                ipv4    = addr.address
                netmask = addr.netmask
                cidr    = _cidr_from_netmask(netmask) if netmask else None
            elif addr.family == socket.AF_INET6:
                raw = addr.address
                if "%" in raw:
                    raw = raw.split("%")[0]
                # Guardar solo la primera IPv6 que no sea link-local si ya hay una mejor,
                # o la primera que encontremos
                if ipv6 is None:
                    ipv6 = raw
                elif raw.lower().startswith("2") or raw.lower().startswith("3"):
                    ipv6 = raw  # preferir global unicast
            elif hasattr(psutil, "AF_LINK") and addr.family == psutil.AF_LINK:
                mac = addr.address

        is_up = stats[name].isup
        speed = stats[name].speed  # Mbps (0 = desconocido o desconectado)
        io    = io_all.get(name)

        result.append({
            "name":             name,
            "ipv4":             ipv4,
            "ipv6":             ipv6,
            "mac":              mac,
            "netmask":          netmask,
            "cidr":             cidr,
            "is_up":            is_up,
            "speed_mbps":       speed,
            "bytes_sent":       io.bytes_sent if io else 0,
            "bytes_recv":       io.bytes_recv if io else 0,
            "total_sent_human": _human_bytes(io.bytes_sent) if io else "—",
            "total_recv_human": _human_bytes(io.bytes_recv) if io else "—",
        })

    # Ordenar: activas primero, luego por nombre
    result.sort(key=lambda x: (not x["is_up"], x["name"]))

    return {"interfaces": result, "total": len(result)}


# ─────────────────────────────────────────────
#  Endpoint: tráfico en tiempo real
# ─────────────────────────────────────────────

@agent.get("/traffic")
def get_traffic():
    """
    Captura ~1 segundo de tráfico real de todas las interfaces de Windows
    y calcula la velocidad actual de cada una.
    """
    if not PSUTIL_AVAILABLE:
        return {
            "error": "psutil no disponible",
            "interfaces": [],
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

    iface_stats = psutil.net_if_stats()

    snap1 = psutil.net_io_counters(pernic=True)
    t1    = time.monotonic()
    time.sleep(1.0)
    snap2 = psutil.net_io_counters(pernic=True)
    t2    = time.monotonic()
    interval = t2 - t1

    interfaces_out = []
    total_sent     = 0
    total_recv     = 0
    total_speed_send = 0.0
    total_speed_recv = 0.0

    for name, c2 in snap2.items():
        c1 = snap1.get(name)
        if c1 is None:
            continue

        delta_sent = max(0, c2.bytes_sent - c1.bytes_sent)
        delta_recv = max(0, c2.bytes_recv - c1.bytes_recv)
        speed_send = (delta_sent / 1024) / interval
        speed_recv = (delta_recv / 1024) / interval

        is_up = iface_stats[name].isup if name in iface_stats else True
        total_sent       += c2.bytes_sent
        total_recv       += c2.bytes_recv
        total_speed_send += speed_send
        total_speed_recv += speed_recv

        interfaces_out.append({
            "name":              name,
            "is_up":             is_up,
            "bytes_sent":        c2.bytes_sent,
            "bytes_recv":        c2.bytes_recv,
            "packets_sent":      c2.packets_sent,
            "packets_recv":      c2.packets_recv,
            "errin":             c2.errin,
            "errout":            c2.errout,
            "dropin":            c2.dropin,
            "dropout":           c2.dropout,
            "speed_send_kbps":   round(speed_send, 2),
            "speed_recv_kbps":   round(speed_recv, 2),
            "speed_send_human":  _human_speed(speed_send),
            "speed_recv_human":  _human_speed(speed_recv),
            "total_sent_human":  _human_bytes(c2.bytes_sent),
            "total_recv_human":  _human_bytes(c2.bytes_recv),
        })

    # Ordenar por tráfico
    interfaces_out.sort(
        key=lambda x: (x["speed_send_kbps"] + x["speed_recv_kbps"]),
        reverse=True,
    )

    return {
        "timestamp":              datetime.now().isoformat(timespec="seconds"),
        "interval_seconds":       round(interval, 3),
        "interfaces":             interfaces_out,
        "total_bytes_sent":       total_sent,
        "total_bytes_recv":       total_recv,
        "total_speed_send_human": _human_speed(total_speed_send),
        "total_speed_recv_human": _human_speed(total_speed_recv),
    }


# ─────────────────────────────────────────────
#  Punto de entrada
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  IP Manager — Agente Local de Red")
    print("  Escuchando en http://localhost:8001")
    print("  Docker lo alcanza en http://host.docker.internal:8001")
    print("  Docs: http://localhost:8001/docs")
    print("=" * 55)
    uvicorn.run(agent, host="0.0.0.0", port=8001, log_level="warning")
