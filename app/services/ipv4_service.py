"""
Servicio de cálculo IPv4.
Incluye: subneteo, clasificación, validación, conversión binaria.
Compatible con Python 3.12.
"""

import ipaddress
import socket
from typing import Optional
from app.models.schemas import IPv4Response


def mask_to_cidr(mask: str) -> int:
    """Convierte una máscara decimal (255.255.255.0) a prefijo CIDR (24)."""
    try:
        return ipaddress.IPv4Network(f"0.0.0.0/{mask}", strict=False).prefixlen
    except Exception:
        raise ValueError(f"Máscara inválida: {mask}")


def cidr_to_mask(cidr: int) -> str:
    """Convierte prefijo CIDR a máscara decimal."""
    net = ipaddress.IPv4Network(f"0.0.0.0/{cidr}", strict=False)
    return str(net.netmask)


def get_wildcard(mask: str) -> str:
    """Calcula la wildcard mask (inversa de la máscara de subred)."""
    net = ipaddress.IPv4Network(f"0.0.0.0/{mask}", strict=False)
    return str(net.hostmask)


def get_ip_class(ip: str) -> str:
    """Determina la clase de la dirección IP (A, B, C, D, E)."""
    first_octet = int(ip.split(".")[0])
    if 1 <= first_octet <= 126:
        return "A"
    elif first_octet == 127:
        return "Loopback (127.x.x.x)"
    elif 128 <= first_octet <= 191:
        return "B"
    elif 192 <= first_octet <= 223:
        return "C"
    elif 224 <= first_octet <= 239:
        return "D (Multicast)"
    elif 240 <= first_octet <= 255:
        return "E (Experimental/Reservada)"
    return "Desconocida"


def classify_ip(ip_obj: ipaddress.IPv4Address) -> str:
    """Clasifica la IP en: Pública, Privada, Loopback, Multicast, Reservada."""
    if ip_obj.is_loopback:
        return "Loopback"
    if ip_obj.is_multicast:
        return "Multicast"
    if ip_obj.is_private:
        return "Privada"
    if ip_obj.is_reserved:
        return "Reservada"
    if ip_obj.is_global:
        return "Pública"
    return "Especial"


def ip_to_binary(ip: str) -> str:
    """Convierte una dirección IPv4 a su representación binaria."""
    parts = ip.split(".")
    return ".".join(f"{int(p):08b}" for p in parts)


def calculate_ipv4(ip: str, mask: Optional[str] = None, cidr: Optional[int] = None) -> IPv4Response:
    """
    Calcula todos los datos de una subred IPv4.
    Acepta máscara decimal o prefijo CIDR.
    """
    # Resolver CIDR
    if cidr is not None:
        prefix = cidr
    elif mask is not None:
        prefix = mask_to_cidr(mask)
    else:
        raise ValueError("Se requiere máscara o CIDR.")

    # Construir la red
    try:
        network = ipaddress.IPv4Network(f"{ip}/{prefix}", strict=False)
    except ValueError as e:
        raise ValueError(f"IP o prefijo inválido: {e}")

    ip_obj = ipaddress.IPv4Address(ip)
    net_mask = str(network.netmask)

    total = network.num_addresses

    # Calcular primer/último host sin materializar la lista completa (evita memory bomb en /0-/1)
    if total == 1:
        # /32 — host único, sin broadcast ni host usable separados
        first_host = str(network.network_address)
        last_host  = str(network.network_address)
        usable     = 0
    elif total == 2:
        # /31 — punto a punto (RFC 3021), ambas direcciones son usables
        first_host = str(network.network_address)
        last_host  = str(network.broadcast_address)
        usable     = 2
    else:
        first_host = str(network.network_address + 1)
        last_host  = str(network.broadcast_address - 1)
        usable     = total - 2

    return IPv4Response(
        ip=ip,
        cidr=prefix,
        mask=net_mask,
        wildcard=str(network.hostmask),
        network_address=str(network.network_address),
        broadcast_address=str(network.broadcast_address),
        first_host=first_host,
        last_host=last_host,
        total_hosts=total,
        usable_hosts=usable,
        ip_class=get_ip_class(ip),
        ip_type=classify_ip(ip_obj),
        binary_mask=ip_to_binary(net_mask),
        network_binary=ip_to_binary(str(network.network_address)),
        is_private=ip_obj.is_private,
        is_loopback=ip_obj.is_loopback,
        is_multicast=ip_obj.is_multicast,
        is_reserved=ip_obj.is_reserved,
        classification=classify_ip(ip_obj),
    )
