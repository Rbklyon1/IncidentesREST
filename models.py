from datetime import datetime
from typing import Any, Dict, List
from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class UsuarioRef(BaseModel):
    idUsuario: str


class EventoRef(BaseModel):
    idEvento: str


class Incidente(BaseModel):
    _id : str
    nombre: str
    fechaIncidente: datetime
    descripcion: str
    estatus: str
    prioridad: str
    tipoIncidente: str
    reportadoPor: UsuarioRef
    evento: EventoRef


class CrearIncidente(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    nombre: str
    descripcion: str = Field(
        validation_alias=AliasChoices("descripcion", "descripci\u00f3n")
    )
    prioridad: str
    tipoIncidente: str
    reportadoPor: UsuarioRef
    evento: EventoRef


class Salida(BaseModel):
    codigo: int
    mensaje: str


class IncidenteSalida(Salida):
    incidentes: Dict[str, Any] | None = None


class IncidentesSalida(Salida):
    incidentes: List[Dict[str, Any]] | None = None
