"""
Router FastAPI para exportar resultados a JSON.
Endpoint:
  POST /api/export/json
Compatible con FastAPI y Python 3.12.
"""

import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, Response
from app.models.schemas import ExportRequest

router = APIRouter(prefix="/api/export", tags=["Exportar"])


@router.post("/json", summary="Exportar resultado a JSON")
def export_to_json(request: ExportRequest):
    """
    Recibe un objeto de datos y lo retorna como archivo JSON descargable.

    - **data**: Diccionario con los datos a exportar.
    - **filename**: Nombre del archivo sin extensión (opcional, defecto: 'resultado').
    """
    try:
        filename = (request.filename or "resultado").replace(" ", "_")
        json_bytes = json.dumps(request.data, indent=2, ensure_ascii=False).encode("utf-8")
        return Response(
            content=json_bytes,
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}.json"',
                "Content-Length": str(len(json_bytes)),
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar: {e}")
