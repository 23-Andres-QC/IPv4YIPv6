# IP Manager — Documentación Completa

> **Proyecto Final · Curso de Redes · Ciclo 08**
> Aplicación web para gestión completa de direcciones IPv4 e IPv6, construida con FastAPI, Python 3.12, Docker y Bootstrap 5.

---

## Tabla de contenidos

1. [Introducción](#1-introducción)
2. [Objetivos](#2-objetivos)
3. [Arquitectura del sistema](#3-arquitectura-del-sistema)
4. [Explicación de IPv4](#4-explicación-de-ipv4)
5. [Explicación de IPv6](#5-explicación-de-ipv6)
6. [Diferencias IPv4 vs IPv6](#6-diferencias-ipv4-vs-ipv6)
7. [Conversión IPv4 ↔ IPv6](#7-conversión-ipv4--ipv6)
8. [Explicación de Docker](#8-explicación-de-docker)
9. [Explicación de FastAPI](#9-explicación-de-fastapi)
10. [Explicación de cada módulo](#10-explicación-de-cada-módulo)
11. [Diagrama de flujo en ASCII](#11-diagrama-de-flujo-en-ascii)
12. [Lógica de cálculo — detalles técnicos](#12-lógica-de-cálculo--detalles-técnicos)
13. [Casos de uso](#13-casos-de-uso)
14. [Capturas sugeridas](#14-capturas-sugeridas)
15. [Posibles mejoras](#15-posibles-mejoras)
16. [Estructura de carpetas](#16-estructura-de-carpetas)
17. [Endpoints de la API](#17-endpoints-de-la-api)

---

## 1. Introducción

**IP Manager** es una aplicación web full-stack que permite realizar operaciones avanzadas sobre direcciones IP de los protocolos IPv4 e IPv6. Fue desarrollada como proyecto final del curso de **Redes de Computadoras** con el objetivo de consolidar los conocimientos sobre direccionamiento, subnetting, y la transición entre protocolos de red.

La aplicación expone una **API REST** documentada automáticamente con Swagger UI, y una **interfaz web** moderna construida con Bootstrap 5 que es completamente responsive (funciona en PC, tablet y celular).

### ¿Qué puede hacer IP Manager?

| Funcionalidad                        | Descripción                                                    |
|--------------------------------------|----------------------------------------------------------------|
| Cálculo de subredes IPv4             | Máscara, wildcard, red, broadcast, primer/último host, clase   |
| Información de redes IPv6            | Expansión, compresión, tipo, alcance, prefijo                  |
| Conversión IPv4 → IPv6 (API)         | Mapped, compatible, 6to4, Teredo                               |
| Conversión IPv6 → IPv4 (API)         | Extracción de IPv4 desde formatos especiales                   |
| Interfaces de red reales (Windows)   | Detecta Wi-Fi, Ethernet, Bluetooth, etc. via agente local      |
| Clasificación automática de IP       | Pública, privada, loopback, multicast, reservada               |
| Historial de consultas               | En memoria, accesible via `GET /api/history`                   |
| Exportación a JSON                   | Cualquier resultado descargable como archivo `.json`           |

---

## 2. Objetivos

### Objetivos generales

- Desarrollar una aplicación web funcional que implemente los conceptos fundamentales del curso de redes.
- Integrar tecnologías modernas de desarrollo backend (FastAPI), contenedorización (Docker) y frontend (Bootstrap 5).

### Objetivos específicos

1. **Implementar el cálculo completo de subredes IPv4**: dirección de red, broadcast, rango de hosts, máscara en binario, wildcard y clase de red.
2. **Implementar el análisis de direcciones IPv6**: expansión, compresión, tipo de dirección, alcance y total de hosts.
3. **Implementar la conversión bidireccional IPv4 ↔ IPv6** usando los estándares RFC 4291 (IPv4-Mapped, IPv4-Compatible) y RFC 3056 (6to4).
4. **Clasificar automáticamente** cualquier dirección IP en: Pública, Privada, Loopback, Multicast o Reservada.
5. **Detectar las interfaces de red reales** del sistema operativo Windows mediante un agente local.
6. **Dockerizar** la aplicación para facilitar su despliegue en cualquier entorno.
7. **Documentar la API** automáticamente con Swagger UI y ReDoc.
8. **Mantener un historial de consultas** en memoria accesible mediante un endpoint REST.

---

## 3. Arquitectura del sistema

IP Manager sigue una arquitectura de **3 capas** con un componente adicional para la detección de red real en Windows:

```
┌─────────────────────────────────────────────────────────┐
│                  CAPA DE PRESENTACIÓN                   │
│           Bootstrap 5 + Fetch API (Frontend)            │
│     templates/index.html + static/css + static/js      │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTP / JSON
┌─────────────────────────▼───────────────────────────────┐
│                  CAPA DE APLICACIÓN                     │
│                FastAPI (app/main.py)                    │
│    Routers: IPv4 · IPv6 · Conversión · Red Local        │
│             Historial · Exportación                     │
└─────────────────────────┬───────────────────────────────┘
                          │ llamadas a funciones / httpx
          ┌───────────────┴──────────────┐
          │                              │
┌─────────▼──────────┐      ┌────────────▼────────────────┐
│   CAPA DE LÓGICA   │      │  AGENTE LOCAL (Windows)     │
│   app/services/    │      │  local_agent.py             │
│  ipv4 · ipv6 ·    │      │  Puerto 8001                │
│  conversión ·      │      │  psutil: interfaces reales  │
│  historial         │      │  (Wi-Fi, Ethernet, etc.)    │
└────────────────────┘      └─────────────────────────────┘
```

### Tecnologías utilizadas

| Capa            | Tecnología              | Versión   |
|-----------------|-------------------------|-----------|
| Backend         | FastAPI                 | 0.115.5   |
| Runtime         | Python                  | 3.12      |
| Servidor        | Uvicorn                 | 0.32.1    |
| Validación      | Pydantic v2             | 2.10.3    |
| Templates       | Jinja2                  | 3.1.4     |
| Frontend        | Bootstrap               | 5.3.3     |
| Íconos          | Bootstrap Icons         | 1.11.3    |
| Red del host    | psutil                  | 6.1.0     |
| Proxy HTTP      | httpx                   | 0.28.1    |
| Contenedor      | Docker                  | 24+       |
| Compose         | Docker Compose          | v2        |

---

## 4. Explicación de IPv4

### 4.1 ¿Qué es IPv4?

El **Protocolo de Internet versión 4 (IPv4)**, definido en el RFC 791 (1981), es el protocolo de capa de red más ampliamente utilizado en Internet. Una dirección IPv4 es un número de **32 bits** representado en **notación decimal punteada**: cuatro octetos separados por puntos, cada uno con un valor de 0 a 255.

```
  Ejemplo:    192.168.1.100
  En bits: 11000000.10101000.00000001.01100100
```

### 4.2 Clases de direcciones IPv4

| Clase | Rango del primer octeto | Uso            | Máscara defecto         |
|-------|------------------------|----------------|-------------------------|
| A     | 1 – 126                | Redes grandes  | /8  (255.0.0.0)         |
| B     | 128 – 191              | Redes medianas | /16 (255.255.0.0)       |
| C     | 192 – 223              | Redes pequeñas | /24 (255.255.255.0)     |
| D     | 224 – 239              | Multicast      | —                       |
| E     | 240 – 255              | Experimental   | —                       |
| —     | 127.x.x.x              | Loopback       | —                       |

### 4.3 Rangos privados (RFC 1918)

Las siguientes direcciones **no son enrutables en Internet** y se usan en redes internas:

| Rango                         | CIDR           | Clase |
|-------------------------------|----------------|-------|
| 10.0.0.0 – 10.255.255.255     | 10.0.0.0/8     | A     |
| 172.16.0.0 – 172.31.255.255   | 172.16.0.0/12  | B     |
| 192.168.0.0 – 192.168.255.255 | 192.168.0.0/16 | C     |

### 4.4 Subnetting (División en subredes)

El subnetting permite dividir una red grande en subredes más pequeñas usando una **máscara de subred**.

```
Red:       192.168.1.0/24
Máscara:   255.255.255.0
Wildcard:  0.0.0.255
Red:       192.168.1.0
Broadcast: 192.168.1.255
Hosts:     192.168.1.1 – 192.168.1.254 (254 hosts)
```

**Fórmulas clave:**

```
Total de direcciones = 2^(32 - prefijo)
Hosts utilizables    = 2^(32 - prefijo) - 2
Dirección de red     = IP AND máscara
Broadcast            = IP OR wildcard
Wildcard             = NOT máscara (inversión de bits)
```

**Casos especiales:**

| Prefijo | Total | Hosts usables | Nota                                        |
|---------|-------|---------------|---------------------------------------------|
| /32     | 1     | 0             | Host único (ruta de host)                   |
| /31     | 2     | 2             | Punto a punto RFC 3021 (ambas son usables)  |
| /30     | 4     | 2             | Mínima subred tradicional                   |
| /0      | 2^32  | 2^32 - 2      | Toda la tabla de rutas                      |

### 4.5 Notación CIDR

El CIDR (Classless Inter-Domain Routing, RFC 4632) permite especificar la máscara como el número de bits de red:

```
192.168.1.0/24   → máscara 255.255.255.0
10.0.0.0/8       → máscara 255.0.0.0
172.16.0.0/12    → máscara 255.240.0.0
```

---

## 5. Explicación de IPv6

### 5.1 ¿Qué es IPv6?

El **Protocolo de Internet versión 6 (IPv6)**, definido en el RFC 8200 (2017), fue diseñado para resolver el agotamiento de direcciones de IPv4. Una dirección IPv6 tiene **128 bits**, representados como 8 grupos de 4 dígitos hexadecimales separados por `:`.

```
  Completa:   2001:0db8:0000:0000:0000:0000:0000:0001
  Comprimida: 2001:db8::1
```

### 5.2 Tipos de direcciones IPv6

| Tipo             | Prefijo        | Descripción                                    |
|------------------|----------------|------------------------------------------------|
| Global Unicast   | 2000::/3       | Equivalente a IPs públicas de IPv4             |
| Link-Local       | fe80::/10      | Solo para comunicación en el mismo enlace      |
| ULA (Privada)    | fc00::/7       | Equivalente a IPs privadas de IPv4             |
| Multicast        | ff00::/8       | Envío a múltiples destinatarios                |
| Loopback         | ::1/128        | Equivalente a 127.0.0.1 en IPv4                |
| No especificada  | ::/128         | Dirección no asignada                          |
| IPv4-Mapped      | ::ffff:0:0/96  | Representación de IPv4 en IPv6                 |
| Documentación    | 2001:db8::/32  | Solo para ejemplos (RFC 3849), no enrutable    |

### 5.3 Reglas de compresión IPv6

1. Se pueden omitir los ceros a la izquierda de cada grupo.
2. Un grupo continuo de grupos `0000` puede reemplazarse con `::` (solo una vez).

```
2001:0db8:0000:0000:0000:0000:0000:0001
→  2001:db8::1
```

### 5.4 Tamaño del espacio de direcciones

```
IPv6 total: 2^128 = 340,282,366,920,938,463,463,374,607,431,768,211,456 direcciones
           ≈ 3.4 × 10^38 direcciones

Para comparar:
IPv4 total: 2^32  = 4,294,967,296 ≈ 4.3 × 10^9 direcciones
```

---

## 6. Diferencias IPv4 vs IPv6

| Característica          | IPv4                         | IPv6                                  |
|-------------------------|------------------------------|---------------------------------------|
| Longitud de dirección   | 32 bits                      | 128 bits                              |
| Notación                | Decimal punteada (4 octetos) | Hexadecimal con colones (8 grupos)    |
| Total de direcciones    | ~4.3 mil millones            | ~3.4 × 10^38                          |
| Configuración           | Manual o DHCP                | Autoconfiguración (SLAAC) o DHCPv6    |
| Seguridad               | Opcional (IPsec)             | IPsec integrado                       |
| Fragmentación           | En enrutadores y hosts       | Solo en el host origen                |
| Checksum de cabecera    | Sí                           | No (delegado a capa de transporte)    |
| Broadcast               | Sí                           | No (reemplazado por multicast)        |
| NAT                     | Muy común                    | No necesario (IPs globales únicas)    |
| DNS inverso             | in-addr.arpa                 | ip6.arpa                              |
| Longitud de cabecera    | Variable (20–60 bytes)       | Fija (40 bytes)                       |
| Soporte en redes        | Universalmente soportado     | Creciendo (>45% del tráfico global)   |
| ARP                     | Usa ARP                      | Usa NDP (Neighbor Discovery)          |
| QoS                     | ToS (Type of Service)        | Flow Label (20 bits)                  |

---

## 7. Conversión IPv4 ↔ IPv6

### 7.1 IPv4-Mapped (RFC 4291)

Es la forma más común de representar una dirección IPv4 dentro del espacio IPv6.

```
Formato:  ::ffff:x.x.x.x
Ejemplo:  192.168.1.1  →  ::ffff:192.168.1.1
                      →  ::ffff:c0a8:0101
```

Permite que sistemas **dual-stack** manejen conexiones IPv4 a través de sockets IPv6.

### 7.2 IPv4-Compatible (RFC 4291 - obsoleto)

```
Formato:  ::x.x.x.x
Ejemplo:  192.168.1.1  →  ::192.168.1.1
                      →  ::c0a8:0101
```

Declarado obsoleto en RFC 4291 pero aún aparece en documentación histórica.

### 7.3 6to4 (RFC 3056)

Permite el tunelado automático de tráfico IPv6 sobre infraestructura IPv4 usando el prefijo `2002::/16`.

```
Formato:  2002:AABB:CCDD::/48
Ejemplo:  192.168.1.1  →  c0a8:0101 (hex de los 4 octetos)
                      →  2002:c0a8:0101::/48
```

### 7.4 Teredo (RFC 4380)

Permite la tunelización a través de NAT usando el prefijo `2001::/32`.

```
Prefijo Teredo:  2001:0000::/32
Ejemplo:  192.168.1.1  →  2001:0000:c0a8:0101::/32
```

> **Nota**: La implementación de Teredo en IP Manager es una representación simplificada del prefijo. El protocolo Teredo real requiere un servidor de relay y codifica también el puerto y la dirección del servidor en la dirección.

### 7.5 Extracción IPv4 desde IPv6

La API detecta automáticamente el tipo de dirección IPv6 e intenta extraer la IPv4 embebida:

1. **IPv4-Mapped** (`::ffff:x.x.x.x`) → extrae los últimos 32 bits usando `ipv6.ipv4_mapped`
2. **IPv4-Compatible** (`::x.x.x.x`) → convierte el entero a IPv4 si el valor es < 2^32
3. **6to4** (`2002:xxyy:zzww::`) → extrae bytes 2-3 y 4-5 del prefijo expandido

---

## 8. Explicación de Docker

### 8.1 ¿Qué es Docker?

**Docker** es una plataforma de contenedores que permite empaquetar una aplicación junto con todas sus dependencias en una unidad portátil llamada **imagen**. Los contenedores Docker son:

- **Portátiles**: funcionan igual en cualquier sistema operativo con Docker instalado.
- **Aislados**: no interfieren con otras aplicaciones del sistema.
- **Reproducibles**: siempre producen el mismo entorno de ejecución.
- **Ligeros**: comparten el kernel del sistema operativo host.

### 8.2 Conceptos clave

| Concepto      | Descripción                                                     |
|---------------|-----------------------------------------------------------------|
| `Dockerfile`  | Archivo de instrucciones para construir una imagen              |
| `Image`       | Plantilla inmutable del contenedor                              |
| `Container`   | Instancia en ejecución de una imagen                            |
| `Volume`      | Almacenamiento persistente fuera del contenedor                 |
| `Network`     | Red virtual entre contenedores                                  |
| `Registry`    | Repositorio de imágenes (ej: Docker Hub)                        |
| `Compose`     | Herramienta para definir aplicaciones multi-contenedor          |

### 8.3 El Dockerfile de IP Manager

```dockerfile
# Etapa 1: instalar dependencias
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --target=/build/packages -r requirements.txt

# Etapa 2: imagen final mínima
FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=builder /build/packages /app/packages
COPY app/       ./app/
COPY static/    ./static/
COPY templates/ ./templates/
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Se usa una **multi-stage build** para que la imagen final no incluya herramientas de compilación, reduciendo el tamaño y la superficie de ataque.

### 8.4 Docker Compose

```yaml
services:
  ip-manager:
    build: .
    image: ip-manager:latest
    container_name: ip-manager
    ports:
      - "8000:8000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "..."]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 8.5 Limitación de Docker con interfaces de red

Docker Desktop en Windows corre en una **máquina virtual Linux** (WSL2 o Hyper-V). Por eso, dentro del contenedor solo son visibles las interfaces virtuales `lo` (loopback) y `eth0` (interfaz del contenedor), **no** la Wi-Fi ni la Ethernet reales de Windows.

Para mostrar las interfaces reales se usa `local_agent.py`, un proceso Python que corre **directamente en Windows** y es alcanzado desde Docker via `host.docker.internal:8001`.

```
  Docker Container (Linux VM)
       │
       │  GET http://host.docker.internal:8001/interfaces
       ▼
  local_agent.py (Windows, puerto 8001)
       │
       │  psutil.net_if_stats()  ← TODAS las interfaces (incluso desconectadas)
       │  psutil.net_if_addrs()  ← Direcciones asignadas
       ▼
  Wi-Fi · Ethernet · Bluetooth · vEthernet · Loopback ...
```

---

## 9. Explicación de FastAPI

### 9.1 ¿Qué es FastAPI?

**FastAPI** es un framework web moderno para Python que permite construir APIs REST de alto rendimiento. Sus características principales son:

- **Alto rendimiento**: basado en Starlette y Pydantic, comparable a Node.js y Go.
- **Tipado estático**: usa las type hints de Python 3.10+ para validar datos automáticamente.
- **Documentación automática**: genera Swagger UI y ReDoc sin configuración adicional.
- **Asíncrono**: soporta `async/await` de forma nativa.
- **Validación automática**: Pydantic valida todos los datos de entrada y salida.

### 9.2 Estructura de una aplicación FastAPI

```python
from fastapi import FastAPI

app = FastAPI(title="Mi API")

@app.get("/items/{id}")
async def get_item(id: int):
    return {"id": id, "name": "Ejemplo"}
```

FastAPI infiere automáticamente:
- El tipo de `id` es `int` → valida que sea un entero
- Si la petición envía `"abc"` → retorna un error 422 automáticamente

### 9.3 Routers en FastAPI

Los **APIRouter** permiten organizar los endpoints en módulos separados:

```python
# En app/routers/ipv4_router.py
from fastapi import APIRouter
router = APIRouter(prefix="/api/ipv4", tags=["IPv4"])

@router.post("/calculate")
def calculate(request: IPv4Request):
    ...

# En app/main.py
app.include_router(ipv4_router.router)
```

### 9.4 Pydantic v2

**Pydantic** define los esquemas de datos con validación automática:

```python
from pydantic import BaseModel, Field

class IPv4Request(BaseModel):
    ip: str = Field(..., example="192.168.1.0")
    cidr: int = Field(None, ge=0, le=32)
```

- `...` → campo obligatorio
- `ge=0, le=32` → validación de rango (0 ≤ valor ≤ 32)
- Si el valor no pasa la validación → FastAPI retorna HTTP 422

### 9.5 Jinja2 Templates

FastAPI sirve el frontend HTML usando Jinja2:

```python
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
```

---

## 10. Explicación de cada módulo

### `app/main.py`
Punto de entrada de la aplicación. Crea la instancia de FastAPI, configura el middleware CORS, monta los archivos estáticos, incluye todos los routers y define las rutas de la interfaz web. Registra los routers: `ipv4`, `ipv6`, `conversion`, `history`, `export` y `local`.

### `app/models/schemas.py`
Define todos los modelos Pydantic para validación de datos de entrada (Request) y salida (Response):
- `IPv4Request`, `IPv4Response`
- `IPv6Request`, `IPv6Response`
- `ConversionRequest`, `ConversionIPv4ToIPv6Response`, `ConversionIPv6ToIPv4Response`
- `InterfaceInfo`, `InterfacesResponse`
- `HistoryEntry`, `HistoryResponse`
- `ExportRequest`

### `app/services/ipv4_service.py`
Contiene toda la lógica de cálculo IPv4:
- `mask_to_cidr()`: convierte máscara decimal a CIDR usando `ipaddress.IPv4Network`
- `cidr_to_mask()`: convierte CIDR a máscara decimal
- `get_wildcard()`: calcula la wildcard mask (hostmask)
- `get_ip_class()`: determina la clase (A, B, C, D, E) por el primer octeto
- `classify_ip()`: clasifica en Pública/Privada/Loopback/Multicast/Reservada usando las propiedades de `IPv4Address`
- `ip_to_binary()`: convierte IP a representación binaria (4 octetos de 8 bits)
- `calculate_ipv4()`: función principal; usa aritmética directa sobre `IPv4Network` para calcular primer/último host sin materializar la lista completa de hosts (evita problemas de memoria en redes /0 o /1). Maneja `/32` (host único) y `/31` (punto a punto RFC 3021) como casos especiales.

### `app/services/ipv6_service.py`
Contiene la lógica de análisis IPv6:
- `expand_ipv6()`: expande la forma comprimida a 8 grupos de 4 hex
- `compress_ipv6()`: comprime la forma expandida
- `get_ipv6_scope()`: determina el alcance (loopback, link-local, multicast, site-local, ULA, global)
- `classify_ipv6()`: clasifica el tipo (Loopback, Multicast, Link-Local, Privada ULA, Global Unicast)
- `total_addresses_str()`: calcula el total de direcciones en el prefijo; usa aritmética entera nativa (no float) para mantener precisión exacta en prefijos pequeños como /0 (2^128 direcciones)
- `calculate_ipv6()`: función principal; acepta la IP con o sin prefijo incluido (ej: `2001:db8::/64` se separa automáticamente)

### `app/services/conversion_service.py`
Implementa la conversión entre protocolos:
- `ipv4_to_ipv6()`: genera IPv4-Mapped (`::ffff:`), IPv4-Compatible (`::`) usando aritmética entera, 6to4 (`2002::`) y Teredo simplificado (`2001::`)
- `ipv6_to_ipv4()`: extrae IPv4 de IPv6-Mapped (propiedad `.ipv4_mapped`), compatible (entero < 2^32) y 6to4 (bytes 1-2 del prefijo expandido)

### `app/services/history_service.py`
Gestiona el historial de consultas en memoria:
- Lista global `_history` con máximo 200 entradas (elimina la más antigua al superar el límite)
- `add_entry()`: agrega entrada con ID auto-incremental y timestamp ISO
- `get_history()`: retorna todo el historial como `HistoryResponse`
- `clear_history()`: vacía la lista y resetea el contador

### `app/routers/`
Cada archivo define un `APIRouter` con los endpoints de su dominio:
- `ipv4_router.py`: `POST /api/ipv4/calculate`, `GET /api/ipv4/info/{ip}`
- `ipv6_router.py`: `POST /api/ipv6/calculate`, `GET /api/ipv6/info/{ip}`
- `conversion_router.py`: `POST /api/convert/ipv4-to-ipv6`, `POST /api/convert/ipv6-to-ipv4`
- `local_router.py`: proxy a `http://host.docker.internal:8001` → `GET /api/local/status`, `/api/local/interfaces`, `/api/local/traffic`
- `history_router.py`: `GET /api/history`, `DELETE /api/history`
- `export_router.py`: `POST /api/export/json`

### `local_agent.py`
Proceso FastAPI independiente que corre **directamente en Windows** (puerto 8001). Usa `psutil.net_if_stats()` para obtener **todas** las interfaces (incluyendo las desconectadas sin IP) y `psutil.net_if_addrs()` para obtener las direcciones asignadas. Expone `/health`, `/interfaces` y `/traffic`.

### `templates/index.html`
Interfaz web SPA (Single Page Application) con Bootstrap 5. Incluye 4 secciones: **IPv4**, **IPv6**, **Red Local (Windows)** e **Historial**. Completamente responsive (PC/tablet/celular).

### `static/css/style.css`
Estilos personalizados que complementan Bootstrap. Define variables CSS, tarjetas de resumen con 8 clases de gradientes (`card-gradient-blue/green/teal/purple/orange/red/cyan/indigo`), tipografía monoespaciada para IPs, y media queries.

### `static/js/app.js`
Lógica JavaScript del frontend. Usa Fetch API para comunicarse con el backend. Maneja formularios, construye tablas y tarjetas dinámicamente, gestiona toasts de notificación, exportación JSON, y carga de interfaces locales con click-to-calculate.

---

## 11. Diagrama de flujo en ASCII

```
USUARIO (Browser)
     │
     │  HTTP GET /
     ▼
┌────────────────────────────┐
│     FastAPI (main.py)      │
│   Jinja2 → index.html      │
└──────────┬─────────────────┘
           │
           │  El usuario llena el formulario
           │  y presiona "Calcular IPv4"
           ▼
     JavaScript (app.js)
     fetch("POST /api/ipv4/calculate", payload)
           │
           ▼
┌──────────────────────────────────────┐
│         FastAPI Router               │
│    app/routers/ipv4_router.py        │
│                                      │
│  1. Recibe IPv4Request (Pydantic)    │
│  2. Valida ip, mask, cidr            │
│  3. Llama calculate_ipv4()           │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│         IPv4 Service                 │
│   app/services/ipv4_service.py       │
│                                      │
│  ┌─────────────────────────────────┐ │
│  │ Resolución de prefijo:          │ │
│  │  si cidr → usar cidr            │ │
│  │  si mask → mask_to_cidr(mask)   │ │
│  │  else    → error                │ │
│  └─────────────────────────────────┘ │
│  ┌─────────────────────────────────┐ │
│  │ Construcción de la red:         │ │
│  │  IPv4Network(ip/cidr,           │ │
│  │             strict=False)       │ │
│  └─────────────────────────────────┘ │
│  ┌─────────────────────────────────┐ │
│  │ Cálculo sin lista de hosts:     │ │
│  │  /32 → host único               │ │
│  │  /31 → RFC 3021 (2 usables)     │ │
│  │  else → net+1 / broadcast-1     │ │
│  └─────────────────────────────────┘ │
└──────────────────┬───────────────────┘
                   │  IPv4Response (JSON)
                   ▼
┌──────────────────────────────────────┐
│         history_service              │
│  add_entry("IPv4 Calculate", ...)    │
└──────────────────┬───────────────────┘
                   │  HTTP 200 JSON
                   ▼
     JavaScript (app.js)
     buildIPv4SummaryCards(data)
     buildIPv4Table(data)
     → Renderiza tarjetas y tabla en el DOM
           │
           ▼
USUARIO ve los resultados
```

---

```
FLUJO DE INTERFACES LOCALES (Windows)

  Browser → click "Actualizar" (sección Red Local)
       │
       │  fetch GET /api/local/interfaces
       ▼
  FastAPI local_router.py
       │
       │  httpx GET http://host.docker.internal:8001/interfaces
       ▼
  local_agent.py (Windows, puerto 8001)
       │
       │  psutil.net_if_stats()  ← TODAS (incluso desconectadas)
       │  psutil.net_if_addrs()  ← IPs asignadas (lookup)
       ▼
  Lista de interfaces ordenada: activas primero
       │
       │  JSON response
       ▼
  Browser muestra tarjetas de interfaces
  Click en IP → auto-llena formulario IPv4 o IPv6
             → dispara cálculo automáticamente
```

---

```
CLASIFICACIÓN AUTOMÁTICA DE IP

  IP ingresada
       │
       ├── is_loopback?  → Loopback  (127.x.x.x / ::1)
       ├── is_multicast? → Multicast (224.x.x.x / ff00::/8)
       ├── is_private?   → Privada   (RFC 1918 + link-local en Python 3.11+)
       ├── is_reserved?  → Reservada (240.x.x.x)
       └── is_global?    → Pública   (resto enrutable)
```

---

## 12. Lógica de cálculo — detalles técnicos

### 12.1 Cálculo IPv4 sin materializar hosts

Una implementación naive haría `list(network.hosts())` para obtener primer y último host. Esto sería un **memory bomb** para prefijos pequeños:

| Prefijo | Hosts a listar     | Memoria aproximada |
|---------|--------------------|--------------------|
| /24     | 254                | < 1 MB             |
| /8      | 16.7 millones      | ~1 GB              |
| /1      | 2.1 mil millones   | ~140 GB            |

La implementación correcta usa aritmética directa sobre objetos `IPv4Address`:

```python
# Correcto — O(1), sin importar el tamaño de la red
first_host = str(network.network_address + 1)
last_host  = str(network.broadcast_address - 1)
```

### 12.2 Precisión en total de direcciones IPv6

Para un prefijo `/0` el total de direcciones es `2^128`, un número de 39 dígitos. Usar formato float (`.2e`) perdería precisión. La implementación usa enteros nativos de Python:

```python
total = 2 ** bits          # Python int es de precisión arbitraria
return f"{total:,}"        # Formato entero con separadores de miles
```

### 12.3 Detección de interfaces — todas vs conectadas

`psutil.net_if_addrs()` solo retorna interfaces que tienen al menos una dirección. `psutil.net_if_stats()` retorna **todas** las interfaces del sistema, incluyendo adaptadores desconectados.

```python
# Incorrecto — omite interfaces sin IP
for name, addr_list in psutil.net_if_addrs().items():
    ...

# Correcto — incluye todas
for name in psutil.net_if_stats():
    addr_list = psutil.net_if_addrs().get(name, [])
    ...
```

### 12.4 IPv6 con prefijo incluido en el campo IP

El servicio acepta tanto `"2001:db8::"` con prefijo separado, como `"2001:db8::/64"` en el mismo campo:

```python
if "/" in ip:
    parts = ip.split("/", 1)
    ip = parts[0].strip()           # "2001:db8::"
    if prefix is None:
        prefix = int(parts[1])      # 64
```

---

## 13. Casos de uso

### Caso 1: Administrador de red planificando subnetting

```
El administrador necesita dividir 192.168.10.0/24 en subredes /26.

1. Ingresa: IP=192.168.10.0, CIDR=26
2. La app calcula:
   - Red:       192.168.10.0
   - Broadcast: 192.168.10.63
   - Hosts:     62 utilizables (192.168.10.1 – 192.168.10.62)
   - Máscara:   255.255.255.192
   - Wildcard:  0.0.0.63
3. Exporta el resultado a JSON para su documentación.
```

### Caso 2: Ingeniería de red — análisis de dirección IPv6

```
El equipo necesita analizar la dirección fe80::1/64.

1. Ingresa: IP=fe80::1 con prefijo 64 (o directamente fe80::1/64)
2. La app retorna:
   - Forma expandida: fe80:0000:0000:0000:0000:0000:0000:0001
   - Comprimida:      fe80::1
   - Tipo:            Link-Local
   - Alcance:         Link-Local (fe80::/10)
   - Total dir.:      18,446,744,073,709,551,616 (~10^19)
```

### Caso 3: Verificación de tipo de IP recibida

```
Un sistema de seguridad necesita saber si 203.0.113.5 es pública o privada.

1. Ingresa: IP=203.0.113.5, CIDR=32
2. La app retorna:
   - Clasificación: Pública
   - is_private: false
   - is_reserved: false
   - ip_class: C
3. El sistema de seguridad aplica las reglas correspondientes a IPs públicas.
```

### Caso 4: Inventario de interfaces de red del equipo Windows

```
Un ingeniero necesita documentar las interfaces de su PC Windows.

1. Ejecuta: python local_agent.py  (fuera de Docker)
2. En la web presiona "Actualizar" en la sección Red Local
3. La app muestra TODAS las interfaces:
   - Wi-Fi:        192.168.1.100/24, fe80::xxxx, activa
   - Ethernet:     sin IP, desconectada
   - Loopback:     127.0.0.1/8, ::1/128, activa
   - vEthernet:    172.27.x.x/20 (Docker), activa
4. Hace click en 192.168.1.100 → se abre calculadora IPv4 automáticamente
```

---

## 14. Capturas sugeridas

Para la presentación del proyecto se sugiere capturar las siguientes pantallas:

1. **Página principal** (hero banner con navegación)
2. **Formulario IPv4** con datos ingresados (192.168.1.0/24)
3. **Resultado IPv4** mostrando las 8 tarjetas de resumen y la tabla completa
4. **Resultado IPv4 en modo móvil** (diseño de 2 columnas en celular)
5. **Formulario IPv6** con `2001:db8::/32` o `fe80::1/64`
6. **Resultado IPv6** con forma expandida, tipo y total de direcciones
7. **Sección Red Local** mostrando todas las interfaces (activas e inactivas)
8. **Click en IP** de interfaz → calculadora IPv4 auto-completada
9. **Historial de consultas** con múltiples entradas
10. **Swagger UI** en `/docs` mostrando todos los endpoints
11. **Exportación JSON** (navegador descargando el archivo)

---

## 15. Posibles mejoras

### A corto plazo

1. **Persistencia del historial**: guardar en SQLite o Redis para que sobreviva reinicios.
2. **VLSM (Variable Length Subnet Masking)**: calcular múltiples subredes de diferente tamaño.
3. **Calculadora de subnetting**: dado un bloque, calcular cuántas subredes /n caben.
4. **Comparador de subredes**: determinar si una IP pertenece a una subred dada.

### A mediano plazo

5. **Geolocalización de IPs públicas**: integrar ip-api.com para mostrar país y ASN.
6. **Cálculo de rutas resumidas**: dado un conjunto de subredes, calcular el supernet.
7. **Modo oscuro**: toggle light/dark en el frontend.
8. **Exportación a CSV**: además del JSON actual.
9. **Gráfico de tráfico en tiempo real**: integrar Chart.js para visualizar KB/s por interfaz.

### A largo plazo

10. **CLI tool**: versión de línea de comandos con `typer`.
11. **Integración con IPAM**: conectar con herramientas como phpIPAM o NetBox.
12. **Soporte IPv6 ULA generation**: generar prefijos ULA aleatorios (fc00::/7).
13. **Visualización gráfica de subredes**: diagrama interactivo con D3.js.

---

## 16. Estructura de carpetas

```
ProyectoFinal/
├── app/
│   ├── __init__.py
│   ├── main.py                    ← Aplicación FastAPI principal
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py             ← Modelos Pydantic (Request/Response)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── ipv4_router.py         ← Endpoints IPv4
│   │   ├── ipv6_router.py         ← Endpoints IPv6
│   │   ├── conversion_router.py   ← Endpoints de conversión (API)
│   │   ├── local_router.py        ← Proxy al agente local Windows
│   │   ├── history_router.py      ← Endpoint de historial
│   │   └── export_router.py       ← Endpoint de exportación JSON
│   └── services/
│       ├── __init__.py
│       ├── ipv4_service.py        ← Lógica de cálculo IPv4
│       ├── ipv6_service.py        ← Lógica de análisis IPv6
│       ├── conversion_service.py  ← Lógica de conversión IPv4↔IPv6
│       └── history_service.py     ← Gestión del historial en memoria
├── static/
│   ├── css/
│   │   └── style.css              ← Estilos personalizados
│   └── js/
│       └── app.js                 ← Lógica JavaScript del frontend
├── templates/
│   └── index.html                 ← Plantilla HTML con Bootstrap 5
├── local_agent.py                 ← Agente local Windows (puerto 8001)
├── Dockerfile                     ← Imagen Docker multi-stage
├── docker-compose.yml             ← Definición de servicios Docker
├── .dockerignore                  ← Archivos excluidos de la imagen
├── requirements.txt               ← Dependencias Python
├── README.md                      ← Esta documentación
└── EJECUCION.md                   ← Guía de instalación y ejecución
```

---

## 17. Endpoints de la API

| Método | Endpoint                        | Descripción                           |
|--------|---------------------------------|---------------------------------------|
| GET    | `/`                             | Interfaz web principal                |
| GET    | `/health`                       | Health check del servidor             |
| POST   | `/api/ipv4/calculate`           | Calcula subred IPv4                   |
| GET    | `/api/ipv4/info/{ip}`           | Info rápida de una IP                 |
| POST   | `/api/ipv6/calculate`           | Calcula red IPv6                      |
| GET    | `/api/ipv6/info/{ip}`           | Info rápida de IPv6                   |
| POST   | `/api/convert/ipv4-to-ipv6`     | Convierte IPv4 → IPv6 (4 formatos)    |
| POST   | `/api/convert/ipv6-to-ipv4`     | Extrae IPv4 de IPv6                   |
| GET    | `/api/local/status`             | Verifica si el agente local está activo |
| GET    | `/api/local/interfaces`         | Interfaces reales de Windows          |
| GET    | `/api/local/traffic`            | Tráfico en tiempo real de Windows     |
| GET    | `/api/history`                  | Historial de consultas                |
| DELETE | `/api/history`                  | Limpia el historial                   |
| POST   | `/api/export/json`              | Exporta datos a JSON descargable      |
| GET    | `/docs`                         | Swagger UI (documentación API)        |
| GET    | `/redoc`                        | ReDoc (documentación alternativa)     |

---

*Documentación generada para el Proyecto Final del Curso de Redes — Ciclo 08.*
