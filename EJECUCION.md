# EJECUCION.md — Guía Completa de Instalación y Ejecución

> **IP Manager** — Proyecto Final Redes · Python 3.12 + FastAPI + Docker

---

## Tabla de contenidos

1. [Requisitos previos](#1-requisitos-previos)
2. [Instalación local (sin Docker)](#2-instalación-local-sin-docker)
3. [Ejecución con Docker](#3-ejecución-con-docker)
4. [Ejecución con Docker Compose](#4-ejecución-con-docker-compose)
5. [Agente local Windows (interfaces de red)](#5-agente-local-windows-interfaces-de-red)
6. [Verificación de la aplicación](#6-verificación-de-la-aplicación)
7. [Variables de entorno](#7-variables-de-entorno)
8. [Comandos útiles](#8-comandos-útiles)
9. [Solución de problemas](#9-solución-de-problemas)

---

## 1. Requisitos previos

### Para instalación local

| Herramienta | Versión mínima | Verificar con        |
|-------------|----------------|----------------------|
| Python      | 3.12           | `python --version`   |
| pip         | 23+            | `pip --version`      |

### Para Docker

| Herramienta      | Versión mínima | Verificar con              |
|------------------|----------------|----------------------------|
| Docker Engine    | 24.0           | `docker --version`         |
| Docker Compose   | v2.0           | `docker compose version`   |

### Para la sección Red Local (Windows)

Instalar `psutil`, `fastapi` y `uvicorn` directamente en Windows (fuera de Docker):

```bash
pip install fastapi uvicorn psutil
```

---

## 2. Instalación local (sin Docker)

### Paso 1 — Clonar o descomprimir el proyecto

```bash
cd ProyectoFinal
```

---

### Paso 2 — Crear el entorno virtual Python

```bash
python -m venv venv
```

**¿Qué hace este comando?**
- `python -m venv` invoca el módulo `venv` de Python
- `venv` es el nombre del directorio donde se creará el entorno
- Se crean carpetas: `venv/Scripts/` (Windows) o `venv/bin/` (Linux/Mac)

---

### Paso 3 — Activar el entorno virtual

#### En Windows (Command Prompt / PowerShell)

```cmd
venv\Scripts\activate
```

#### En Windows (Git Bash)

```bash
source venv/Scripts/activate
```

#### En Linux / macOS

```bash
source venv/bin/activate
```

**¿Cómo saber si el entorno está activo?**
El prompt del terminal mostrará el nombre del entorno entre paréntesis:

```
(venv) C:\Users\usuario\ProyectoFinal>
```

**Para desactivar el entorno:**

```bash
deactivate
```

---

### Paso 4 — Instalar dependencias

```bash
pip install -r requirements.txt
```

**¿Qué instala este comando?**

| Paquete             | Versión   | Uso                                                  |
|---------------------|-----------|------------------------------------------------------|
| `fastapi`           | 0.115.5   | Framework web principal                              |
| `uvicorn[standard]` | 0.32.1    | Servidor ASGI para correr FastAPI                    |
| `pydantic`          | 2.10.3    | Validación de datos y serialización                  |
| `jinja2`            | 3.1.4     | Motor de plantillas HTML                             |
| `python-multipart`  | 0.0.20    | Soporte para formularios multipart                   |
| `psutil`            | 6.1.0     | Lectura de interfaces de red (usado por agente local)|
| `httpx`             | 0.28.1    | Cliente HTTP para proxy al agente local              |

---

### Paso 5 — Ejecutar el servidor de desarrollo

```bash
uvicorn app.main:app --reload
```

**Explicación de los parámetros:**

| Parámetro       | Descripción                                                        |
|-----------------|--------------------------------------------------------------------|
| `app.main`      | Módulo Python a importar (carpeta `app`, archivo `main.py`)        |
| `app`           | Nombre de la instancia FastAPI dentro de `main.py`                 |
| `--reload`      | Reinicia el servidor automáticamente al detectar cambios en código |

**Salida esperada:**

```
INFO:     Will watch for changes in these directories: ['...\ProyectoFinal']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Application startup complete.
```

---

### Ejecutar en un puerto diferente

```bash
uvicorn app.main:app --reload --port 8080
```

### Ejecutar accesible desde otros dispositivos en la red

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> Usar `--host 0.0.0.0` expone la aplicación a toda la red local. Usar solo en entornos de desarrollo.

---

## 3. Ejecución con Docker

### Paso 1 — Construir la imagen

```bash
docker build -t ip-manager .
```

**Explicación:**

| Parte           | Descripción                                                                    |
|-----------------|--------------------------------------------------------------------------------|
| `docker build`  | Comando para construir una imagen Docker                                       |
| `-t ip-manager` | Asigna el nombre/etiqueta `ip-manager` a la imagen (`-t` = tag)               |
| `.`             | El contexto de construcción es el directorio actual (donde está el Dockerfile) |

**¿Qué ocurre internamente?**

1. Docker lee el `Dockerfile` línea por línea
2. **Etapa 1 (builder)**: instala las dependencias Python en `/build/packages`
3. **Etapa 2 (runtime)**: copia solo los paquetes y el código fuente
4. La imagen final **no incluye pip ni herramientas de compilación**, haciéndola más pequeña y segura

---

### Paso 2 — Ejecutar el contenedor

```bash
docker run -p 8000:8000 ip-manager
```

#### Ejecutar en segundo plano (detached mode)

```bash
docker run -d -p 8000:8000 --name ip-manager-app ip-manager
```

#### Ver logs del contenedor en ejecución

```bash
docker logs ip-manager-app
docker logs -f ip-manager-app   # -f = seguir en tiempo real
```

#### Detener y eliminar el contenedor

```bash
docker stop ip-manager-app
docker rm ip-manager-app
```

---

## 4. Ejecución con Docker Compose

### Iniciar todos los servicios

```bash
docker compose up -d
```

**¿Qué hace `docker compose up`?**

1. Lee `docker-compose.yml`
2. Si la imagen no existe, la construye automáticamente con `docker build`
3. Crea la red `ip-network` (bridge)
4. Crea e inicia el contenedor `ip-manager`
5. Configura el healthcheck (verifica `/health` cada 30 segundos)
6. Monta los volúmenes de código fuente (útil para desarrollo)

---

### Ver estado de los servicios

```bash
docker compose ps
```

**Salida esperada:**

```
NAME          IMAGE             COMMAND              SERVICE     STATUS
ip-manager    ip-manager:latest "python -m uvicor…"  ip-manager  Up X minutes (healthy)
```

---

### Ver logs en tiempo real

```bash
docker compose logs -f
docker compose logs -f ip-manager
```

---

### Reconstruir la imagen (después de cambios en el código)

```bash
docker compose up -d --build
```

---

### Detener los servicios

```bash
docker compose down
```

**¿Qué hace?**
- Detiene todos los contenedores en ejecución
- Elimina los contenedores creados
- Elimina la red `ip-network`
- **No elimina** la imagen ni los volúmenes

---

### Detener y eliminar todo (incluyendo volúmenes e imagen)

```bash
docker compose down -v --rmi all
```

---

## 5. Agente local Windows (interfaces de red)

### ¿Por qué es necesario?

Docker Desktop en Windows corre en una **máquina virtual Linux** (WSL2). Dentro del contenedor, `psutil` solo ve las interfaces virtuales (`lo`, `eth0`). Para mostrar las interfaces **reales** de Windows (Wi-Fi, Ethernet, Bluetooth, etc.) se necesita el agente local.

### Arquitectura

```
  Docker Container          Windows Host
  ──────────────────         ─────────────────────────────
  FastAPI                    local_agent.py (puerto 8001)
  local_router.py   ──────►  /interfaces → psutil reales
  httpx GET                  /traffic    → psutil reales
  host.docker.internal:8001
```

### Paso 1 — Instalar dependencias (una sola vez)

Abrir una terminal de Windows (CMD, PowerShell o Git Bash) **fuera de Docker**:

```bash
pip install fastapi uvicorn psutil
```

### Paso 2 — Ejecutar el agente local

```bash
python local_agent.py
```

**Salida esperada:**

```
=======================================================
  IP Manager — Agente Local de Red
  Escuchando en http://localhost:8001
  Docker lo alcanza en http://host.docker.internal:8001
  Docs: http://localhost:8001/docs
=======================================================
```

### Paso 3 — Verificar que funciona

Abrir en el navegador: `http://localhost:8001/health`

Respuesta esperada:
```json
{
  "status": "ok",
  "agent": "IP Manager Local Agent",
  "host": "NOMBRE-DE-TU-PC",
  "psutil": true
}
```

### Paso 4 — Usar en la interfaz web

Con `local_agent.py` corriendo y la aplicación Docker activa, en `http://localhost:8000`:

1. Ir a la sección **Red Local (Windows)**
2. Presionar **Actualizar**
3. Se muestran **todas** las interfaces del sistema, incluyendo las desconectadas
4. Hacer **click en cualquier dirección IP** → se llena automáticamente el formulario IPv4 o IPv6 y se calcula

### ¿Qué muestra cada interfaz?

| Campo            | Descripción                                          |
|------------------|------------------------------------------------------|
| Nombre           | Nombre de la interfaz (Wi-Fi, Ethernet, etc.)        |
| IPv4             | Dirección IPv4 asignada (si tiene)                   |
| IPv6             | Dirección IPv6 asignada (si tiene)                   |
| MAC              | Dirección física del adaptador                       |
| Estado           | Activa (verde) o Inactiva (gris)                     |
| Total enviado    | Bytes totales enviados desde el último reinicio      |
| Total recibido   | Bytes totales recibidos desde el último reinicio     |
| Velocidad        | Mbps reportados por el adaptador (0 = desconectado)  |

> **Nota**: Las interfaces sin dirección IP asignada también aparecen (con estado "Inactiva"). Esto es posible porque el agente itera sobre `psutil.net_if_stats()` que devuelve **todas** las interfaces del sistema.

---

## 6. Verificación de la aplicación

### Interfaz web

```
http://localhost:8000
```

---

### Health check

```bash
curl http://localhost:8000/health
```

Respuesta esperada:
```json
{"status": "ok", "version": "1.0.0", "app": "IP Manager"}
```

---

### Swagger UI (documentación interactiva)

```
http://localhost:8000/docs
```

Desde aquí puedes **probar todos los endpoints** directamente en el navegador sin necesidad de curl o Postman.

---

### ReDoc (documentación alternativa)

```
http://localhost:8000/redoc
```

---

### Prueba rápida de la API con curl

#### Calcular subred IPv4

```bash
curl -X POST http://localhost:8000/api/ipv4/calculate \
  -H "Content-Type: application/json" \
  -d '{"ip": "192.168.1.0", "cidr": 24}'
```

#### Calcular subred IPv4 con máscara decimal

```bash
curl -X POST http://localhost:8000/api/ipv4/calculate \
  -H "Content-Type: application/json" \
  -d '{"ip": "10.0.0.0", "mask": "255.0.0.0"}'
```

#### Calcular IPv6

```bash
curl -X POST http://localhost:8000/api/ipv6/calculate \
  -H "Content-Type: application/json" \
  -d '{"ip": "2001:db8::", "prefix": 32}'
```

#### Calcular IPv6 con prefijo incluido en la IP

```bash
curl -X POST http://localhost:8000/api/ipv6/calculate \
  -H "Content-Type: application/json" \
  -d '{"ip": "fe80::1/64"}'
```

#### Convertir IPv4 → IPv6

```bash
curl -X POST http://localhost:8000/api/convert/ipv4-to-ipv6 \
  -H "Content-Type: application/json" \
  -d '{"ip": "192.168.1.1"}'
```

#### Extraer IPv4 desde IPv6-Mapped

```bash
curl -X POST http://localhost:8000/api/convert/ipv6-to-ipv4 \
  -H "Content-Type: application/json" \
  -d '{"ip": "::ffff:192.168.1.1"}'
```

#### Ver interfaces de Windows (requiere agente local)

```bash
curl http://localhost:8000/api/local/interfaces
```

#### Ver historial de consultas

```bash
curl http://localhost:8000/api/history
```

#### Limpiar historial

```bash
curl -X DELETE http://localhost:8000/api/history
```

---

## 7. Variables de entorno

La aplicación acepta las siguientes variables de entorno (opcionales):

| Variable           | Defecto   | Descripción                       |
|--------------------|-----------|-----------------------------------|
| `HOST`             | `0.0.0.0` | Dirección de escucha del servidor |
| `PORT`             | `8000`    | Puerto del servidor               |
| `PYTHONUNBUFFERED` | `1`       | Salida sin buffer (recomendado)   |

Para usarlas al correr con Docker:

```bash
docker run -p 8080:8080 -e PORT=8080 ip-manager
```

---

## 8. Comandos útiles

```bash
# ─── Instalación local ────────────────────────────────
python -m venv venv                    # Crear entorno virtual
venv\Scripts\activate                  # Activar (Windows CMD/PowerShell)
source venv/Scripts/activate           # Activar (Windows Git Bash)
source venv/bin/activate               # Activar (Linux/Mac)
pip install -r requirements.txt        # Instalar dependencias
uvicorn app.main:app --reload          # Iniciar servidor de desarrollo
uvicorn app.main:app --host 0.0.0.0   # Iniciar accesible en red local
deactivate                             # Desactivar entorno virtual

# ─── Agente local Windows ─────────────────────────────
pip install fastapi uvicorn psutil     # Instalar dependencias del agente
python local_agent.py                  # Iniciar agente en puerto 8001

# ─── Docker ───────────────────────────────────────────
docker build -t ip-manager .           # Construir imagen
docker run -p 8000:8000 ip-manager     # Ejecutar contenedor
docker run -d -p 8000:8000 ip-manager  # Ejecutar en segundo plano
docker images                          # Listar imágenes
docker ps                              # Ver contenedores activos
docker stop <id>                       # Detener contenedor
docker rm <id>                         # Eliminar contenedor
docker rmi ip-manager                  # Eliminar imagen

# ─── Docker Compose ───────────────────────────────────
docker compose up -d                   # Iniciar servicios
docker compose up -d --build           # Reconstruir e iniciar
docker compose down                    # Detener y eliminar contenedores
docker compose ps                      # Estado de los servicios
docker compose logs -f                 # Ver logs en tiempo real
docker compose restart ip-manager      # Reiniciar servicio
docker compose down -v --rmi all       # Limpieza total
```

---

## 9. Solución de problemas

### Error: `ModuleNotFoundError: No module named 'fastapi'`

**Causa**: El entorno virtual no está activado o las dependencias no se instalaron.

**Solución**:
```bash
source venv/bin/activate         # Linux/Mac
venv\Scripts\activate            # Windows
pip install -r requirements.txt
```

---

### Error: `Address already in use` (puerto 8000 ocupado)

**Causa**: Otro proceso está usando el puerto 8000.

**Solución**:
```bash
# Usar un puerto diferente
uvicorn app.main:app --reload --port 8001

# O en Docker:
docker run -p 8001:8000 ip-manager
```

---

### Error de Docker: `Cannot connect to the Docker daemon`

**Causa**: Docker Desktop no está corriendo.

**Solución**: Abrir Docker Desktop y esperar a que inicie completamente.

---

### Sección Red Local muestra "Agente desconectado"

**Causa**: `local_agent.py` no está corriendo en Windows.

**Solución**:
```bash
# En una terminal de Windows (fuera de Docker):
python local_agent.py
```

Verificar que el agente responde:
```bash
curl http://localhost:8001/health
```

---

### El agente corre pero Docker no lo alcanza

**Causa**: `host.docker.internal` no resuelve correctamente (raro en Docker Desktop para Windows).

**Solución**: Verificar que Docker Desktop está actualizado. En versiones recientes de Docker Desktop para Windows, `host.docker.internal` está disponible por defecto.

```bash
# Desde dentro del contenedor, probar:
docker exec ip-manager python -c "import socket; print(socket.gethostbyname('host.docker.internal'))"
```

---

### Las interfaces de Red Local muestran solo algunas interfaces

**Causa**: En versiones anteriores del agente, se usaba `net_if_addrs()` que omite interfaces sin IP.

**Solución**: Asegurarse de estar usando la versión actual de `local_agent.py` que itera sobre `net_if_stats()`. Reiniciar el agente:
```bash
# Detener el agente (Ctrl+C en su terminal)
python local_agent.py
```

---

### Error: `exec format error` en Docker

**Causa**: La imagen fue construida para una arquitectura diferente (ej: ARM vs x86).

**Solución**:
```bash
docker build --platform linux/amd64 -t ip-manager .
```

---

### IPv6 inválido con "IPv6 o prefijo inválido"

**Causa posible**: La dirección IPv6 tiene caracteres extra o espacios.

**Ejemplos válidos**:
```
::1
fe80::1
2001:db8::
2001:db8::/32        ← prefijo incluido en el campo IP, también válido
::ffff:192.168.1.1
```

---

### Limpiar caché de Docker y reconstruir desde cero

```bash
docker compose down -v --rmi all
docker builder prune -f
docker compose up -d --build
```

---

*Documento de ejecución — IP Manager · Proyecto Final Redes · Ciclo 08*
