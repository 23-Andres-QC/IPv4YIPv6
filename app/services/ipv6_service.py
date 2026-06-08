"""
Servicio de cálculo IPv6.
Incluye: expansión, compresión, tipo de dirección, alcance.
Compatible con Python 3.12.
"""

import ipaddress
from typing import Optional
from app.models.schemas import IPv6Response


def expand_ipv6(ip: str) -> str:
    """Expande una dirección IPv6 a su forma completa (8 grupos de 4 hex)."""
    return ipaddress.IPv6Address(ip).exploded


def compress_ipv6(ip: str) -> str:
    """Comprime una dirección IPv6 a su forma abreviada."""
    return ipaddress.IPv6Address(ip).compressed


def get_ipv6_scope(ip_obj: ipaddress.IPv6Address) -> str:
    """Determina el alcance de la dirección IPv6."""
    if ip_obj.is_loopback:
        return "Loopback (::1)"
    if ip_obj.is_link_local:
        return "Link-Local (fe80::/10)"
    if ip_obj.is_multicast:
        return "Multicast (ff00::/8)"
    if ip_obj.is_site_local:
        return "Site-Local (fec0::/10)"
    if ip_obj.is_private:
        return "Privada (ULA fc00::/7)"
    if ip_obj.is_global:
        return "Global Unicast"
    return "Especial"


def classify_ipv6(ip_obj: ipaddress.IPv6Address) -> str:
    """Clasifica la IPv6."""
    if ip_obj.is_loopback:
        return "Loopback"
    if ip_obj.is_multicast:
        return "Multicast"
    if ip_obj.is_link_local:
        return "Link-Local"
    if ip_obj.is_private:
        return "Privada (ULA)"
    if ip_obj.is_global:
        return "Global Unicast"
    return "Especial"


def total_addresses_str(prefix: int) -> str:
    """Retorna el total de direcciones como string (entero exacto con separadores)."""
    bits  = 128 - prefix
    total = 2 ** bits
    # Usar :, sobre el entero nativo (no float) para evitar pérdida de precisión
    if total >= 10 ** 15:
        # Para números enormes mostrar notación científica aproximada como referencia
        import math
        exp = int(math.log10(total))
        return f"{total:,} (~10^{exp})"
    return f"{total:,}"


def calculate_ipv6(ip: str, prefix: Optional[int] = None) -> IPv6Response:
    """
    Calcula los datos principales de una dirección/red IPv6.
    Acepta la IP con o sin prefijo incluido (ej: '2001:db8::/64').
    """
    # Separar IP y prefijo si vienen juntos (ej: "2001:db8::/64")
    if "/" in ip:
        parts = ip.split("/", 1)
        ip = parts[0].strip()
        if prefix is None:
            try:
                prefix = int(parts[1].strip())
            except ValueError:
                pass

    if prefix is None:
        prefix = 128

    try:
        network = ipaddress.IPv6Network(f"{ip}/{prefix}", strict=False)
        ip_obj = ipaddress.IPv6Address(ip)
    except ValueError as e:
        raise ValueError(f"IPv6 o prefijo inválido: {e}")

    return IPv6Response(
        ip=ip,
        expanded=ip_obj.exploded,
        compressed=ip_obj.compressed,
        prefix=prefix,
        network_address=str(network.network_address),
        total_addresses=total_addresses_str(prefix),
        ip_type=classify_ipv6(ip_obj),
        is_loopback=ip_obj.is_loopback,
        is_multicast=ip_obj.is_multicast,
        is_link_local=ip_obj.is_link_local,
        is_private=ip_obj.is_private,
        scope=get_ipv6_scope(ip_obj),
    )
