from datetime import datetime
from typing import Any, Dict, List, Literal
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


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
    prioridad: Literal["Urgente", "Normal", "Baja"]
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

class EditarIncidente(BaseModel):
    nombre:str |None = None 
    descripcion:str |None = None
    prioridad: Literal["Urgente", "Normal", "Baja"] |None = None
    tipoIncidente: str |None = None

class Evidencia(BaseModel):
    urlImagen: str


class AtendidoPor(BaseModel):
    idUsuario: str
    nombre: str


class RegistroAtencion(BaseModel):
    estatus: Literal["En Atencion", "Atendido"]
    fechaAtencion: datetime
    atendidoPor: AtendidoPor
    evidencias: list[Evidencia]
    
class EvidenciasSalida(Salida):
    incidente: Dict[str, Any] | None = None