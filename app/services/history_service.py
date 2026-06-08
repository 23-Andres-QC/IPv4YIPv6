"""
Servicio de historial de consultas en memoria (en proceso).
Almacena las últimas N operaciones realizadas durante la sesión.
Compatible con Python 3.12.
"""

from datetime import datetime
from typing import List
from app.models.schemas import HistoryEntry, HistoryResponse

# Almacenamiento en memoria (lista global de la sesión)
_history: List[dict] = []
_counter: int = 0
MAX_HISTORY = 200


def add_entry(operation: str, input_data: str, result_summary: str) -> None:
    """Agrega una entrada al historial."""
    global _counter
    _counter += 1
    entry = {
        "id": _counter,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "operation": operation,
        "input": input_data,
        "result_summary": result_summary,
    }
    _history.append(entry)
    # Mantener solo las últimas MAX_HISTORY entradas
    if len(_history) > MAX_HISTORY:
        _history.pop(0)


def get_history() -> HistoryResponse:
    """Retorna todo el historial de consultas."""
    entries = [
        HistoryEntry(
            id=e["id"],
            timestamp=e["timestamp"],
            operation=e["operation"],
            input=e["input"],
            result_summary=e["result_summary"],
        )
        for e in _history
    ]
    return HistoryResponse(total=len(entries), entries=entries)


def clear_history() -> dict:
    """Limpia el historial en memoria."""
    global _history, _counter
    _history = []
    _counter = 0
    return {"message": "Historial limpiado correctamente."}
