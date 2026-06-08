"""
Modelos Pydantic para validación de datos de entrada y salida.
Compatibles con Python 3.12 y FastAPI.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ─────────────────────────────────────────────
#  Modelos de Request
# ─────────────────────────────────────────────

class IPv4Request(BaseModel):
    ip: str = Field(..., example="192.168.1.0", description="Dirección IPv4 base")
    mask: Optional[str] = Field(None, example="255.255.255.0", description="Máscara en notación decimal")
    cidr: Optional[int] = Field(None, ge=0, le=32, example=24, description="Prefijo CIDR")

    model_config = {
        "json_schema_extra": {
            "example": {
                "ip": "192.168.1.0",
                "mask": "255.255.255.0",
                "cidr": 24
            }
        }
    }


class IPv6Request(BaseModel):
    ip: str = Field(..., example="2001:db8::", description="Dirección IPv6")
    prefix: Optional[int] = Field(None, ge=0, le=128, example=64, description="Longitud del prefijo")

    model_config = {
        "json_schema_extra": {
            "example": {
                "ip": "2001:db8::",
                "prefix": 64
            }
        }
    }


class ConversionRequest(BaseModel):
    ip: str = Field(..., example="192.168.1.1", description="Dirección IP a convertir")

    model_config = {
        "json_schema_extra": {
            "example": {
                "ip": "192.168.1.1"
            }
        }
    }


# ─────────────────────────────────────────────
#  Modelos de Response
# ─────────────────────────────────────────────

class IPv4Response(BaseModel):
    ip: str
    cidr: int
    mask: str
    wildcard: str
    network_address: str
    broadcast_address: str
    first_host: str
    last_host: str
    total_hosts: int
    usable_hosts: int
    ip_class: str
    ip_type: str
    binary_mask: str
    network_binary: str
    is_private: bool
    is_loopback: bool
    is_multicast: bool
    is_reserved: bool
    classification: str


class IPv6Response(BaseModel):
    ip: str
    expanded: str
    compressed: str
    prefix: int
    network_address: str
    total_addresses: str
    ip_type: str
    is_loopback: bool
    is_multicast: bool
    is_link_local: bool
    is_private: bool
    scope: str


class ConversionIPv4ToIPv6Response(BaseModel):
    original_ipv4: str
    ipv4_mapped: str
    ipv4_compatible: str
    six_to_four: str
    teredo: Optional[str] = None


class ConversionIPv6ToIPv4Response(BaseModel):
    original_ipv6: str
    ipv4_address: Optional[str] = None
    conversion_type: str
    success: bool
    message: str


class InterfaceInfo(BaseModel):
    name: str
    ipv4: Optional[str] = None
    ipv6: Optional[str] = None
    mac: Optional[str] = None
    netmask: Optional[str] = None
    cidr: Optional[int] = None


class InterfacesResponse(BaseModel):
    interfaces: List[InterfaceInfo]
    total: int


# ─────────────────────────────────────────────
#  Modelo de Historial
# ─────────────────────────────────────────────

class HistoryEntry(BaseModel):
    id: int
    timestamp: str
    operation: str
    input: str
    result_summary: str


class HistoryResponse(BaseModel):
    total: int
    entries: List[HistoryEntry]


# ─────────────────────────────────────────────
#  Modelos de Tráfico de Red
# ─────────────────────────────────────────────

class InterfaceTraffic(BaseModel):
    name: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errin: int
    errout: int
    dropin: int
    dropout: int
    speed_send_kbps: float
    speed_recv_kbps: float
    speed_send_human: str
    speed_recv_human: str
    total_sent_human: str
    total_recv_human: str
    is_up: bool


class TrafficResponse(BaseModel):
    timestamp: str
    interval_seconds: float
    interfaces: List[InterfaceTraffic]
    total_bytes_sent: int
    total_bytes_recv: int
    total_speed_send_human: str
    total_speed_recv_human: str


# ─────────────────────────────────────────────
#  Modelo de Export JSON
# ─────────────────────────────────────────────

class ExportRequest(BaseModel):
    data: dict
    filename: Optional[str] = Field(None, example="resultado_ip")
