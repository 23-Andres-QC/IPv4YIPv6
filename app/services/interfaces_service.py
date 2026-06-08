"""
Servicio de detección de interfaces de red del sistema.
Usa el módulo estándar `socket` e `ipaddress` + psutil si disponible.
Compatible con Python 3.12 en Windows y Linux.
"""

import ipaddress
import socket
from typing import List
from app.models.schemas import InterfaceInfo

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


def _cidr_from_netmask(netmask: str) -> int:
    """Convierte máscara a CIDR."""
    try:
        return ipaddress.IPv4Network(f"0.0.0.0/{netmask}", strict=False).prefixlen
    except Exception:
        return 0


def get_interfaces() -> List[InterfaceInfo]:
    """
    Detecta las interfaces de red del sistema operativo.
    Usa psutil si está disponible, si no usa socket básico.
    """
    interfaces: List[InterfaceInfo] = []

    if PSUTIL_AVAILABLE:
        stats = psutil.net_if_addrs()
        for iface_name, addrs in stats.items():
            ipv4_addr = None
            ipv6_addr = None
            mac_addr = None
            netmask = None
            cidr = None

            for addr in addrs:
                # AF_INET = IPv4
                if addr.family == socket.AF_INET:
                    ipv4_addr = addr.address
                    netmask = addr.netmask
                    if netmask:
                        try:
                            cidr = _cidr_from_netmask(netmask)
                        except Exception:
                            cidr = None
                # AF_INET6 = IPv6
                elif addr.family == socket.AF_INET6:
                    raw = addr.address
                    # Remover sufijo de scope id en Windows (%interface)
                    if "%" in raw:
                        raw = raw.split("%")[0]
                    ipv6_addr = raw
                # AF_LINK / AF_PACKET = MAC
                elif addr.family in (psutil.AF_LINK,):
                    mac_addr = addr.address

            interfaces.append(InterfaceInfo(
                name=iface_name,
                ipv4=ipv4_addr,
                ipv6=ipv6_addr,
                mac=mac_addr,
                netmask=netmask,
                cidr=cidr,
            ))
    else:
        # Fallback básico usando socket
        hostname = socket.gethostname()
        try:
            ipv4 = socket.gethostbyname(hostname)
        except Exception:
            ipv4 = "127.0.0.1"

        interfaces.append(InterfaceInfo(
            name="local",
            ipv4=ipv4,
            ipv6="::1",
            mac=None,
            netmask=None,
            cidr=None,
        ))

    return interfaces
