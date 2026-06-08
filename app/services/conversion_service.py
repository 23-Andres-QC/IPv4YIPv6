"""
Servicio de conversión IPv4 ↔ IPv6.
Implementa:
  - IPv4-Mapped (::ffff:x.x.x.x)
  - IPv4-Compatible (::x.x.x.x)
  - 6to4 (2002::/16)
  - Extracción IPv4 desde IPv6-Mapped
Compatible con Python 3.12.
"""

import ipaddress
from app.models.schemas import ConversionIPv4ToIPv6Response, ConversionIPv6ToIPv4Response


def ipv4_to_ipv6(ip: str) -> ConversionIPv4ToIPv6Response:
    """
    Convierte una dirección IPv4 a sus representaciones IPv6 equivalentes.
    """
    try:
        ipv4 = ipaddress.IPv4Address(ip)
    except ValueError:
        raise ValueError(f"Dirección IPv4 inválida: {ip}")

    # IPv4-Mapped: ::ffff:x.x.x.x
    ipv4_mapped = ipaddress.IPv6Address(f"::ffff:{ip}")

    # IPv4-Compatible: ::x.x.x.x  (obsoleto, RFC 4291)
    ipv4_compatible = ipaddress.IPv6Address(int(ipv4))

    # 6to4: 2002::/16 → 2002:xxyy:zzww::/48
    octets = ip.split(".")
    hex_part = "".join(f"{int(o):02x}" for o in octets)
    six_to_four = f"2002:{hex_part[:4]}:{hex_part[4:]}::"

    # Teredo (simplificado, solo prefix)
    teredo = f"2001:0000:{hex_part[:4]}:{hex_part[4:]}::"

    return ConversionIPv4ToIPv6Response(
        original_ipv4=ip,
        ipv4_mapped=str(ipv4_mapped),
        ipv4_compatible=str(ipv4_compatible),
        six_to_four=six_to_four,
        teredo=teredo,
    )


def ipv6_to_ipv4(ip: str) -> ConversionIPv6ToIPv4Response:
    """
    Intenta extraer una dirección IPv4 de una IPv6.
    Soporta: IPv4-Mapped, IPv4-Compatible, 6to4.
    """
    try:
        ipv6 = ipaddress.IPv6Address(ip)
    except ValueError:
        raise ValueError(f"Dirección IPv6 inválida: {ip}")

    compressed = ipv6.compressed.lower()

    # IPv4-Mapped: ::ffff:x.x.x.x
    if ipv6.ipv4_mapped is not None:
        return ConversionIPv6ToIPv4Response(
            original_ipv6=compressed,
            ipv4_address=str(ipv6.ipv4_mapped),
            conversion_type="IPv4-Mapped (::ffff:x.x.x.x)",
            success=True,
            message="Conversión exitosa desde IPv4-Mapped.",
        )

    # IPv4-Compatible: ::x.x.x.x (int < 2^32)
    int_val = int(ipv6)
    if int_val < 2**32 and int_val > 0:
        ipv4_addr = str(ipaddress.IPv4Address(int_val))
        return ConversionIPv6ToIPv4Response(
            original_ipv6=compressed,
            ipv4_address=ipv4_addr,
            conversion_type="IPv4-Compatible (::x.x.x.x)",
            success=True,
            message="Conversión exitosa desde IPv4-Compatible.",
        )

    # 6to4: empieza con 2002:
    if compressed.startswith("2002:"):
        parts = ipv6.exploded.split(":")
        hex_str = parts[1] + parts[2]  # 4 bytes
        try:
            octets = [str(int(hex_str[i:i+2], 16)) for i in range(0, 8, 2)]
            ipv4_addr = ".".join(octets)
            ipaddress.IPv4Address(ipv4_addr)  # validar
            return ConversionIPv6ToIPv4Response(
                original_ipv6=compressed,
                ipv4_address=ipv4_addr,
                conversion_type="6to4 (2002::/16)",
                success=True,
                message="Conversión exitosa desde 6to4.",
            )
        except Exception:
            pass

    return ConversionIPv6ToIPv4Response(
        original_ipv6=compressed,
        ipv4_address=None,
        conversion_type="No aplicable",
        success=False,
        message="Esta dirección IPv6 no contiene una representación IPv4 extraíble.",
    )
