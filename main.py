from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Request, Depends

from dao import ConexionDB, IncidenteDAO
from models import CrearIncidente, Salida, IncidenteSalida, IncidentesSalida, EditarIncidente, RegistroAtencion, EvidenciasSalida, Usuario
from security import RoleChecker

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.extension import _rate_limit_exceeded_handler

app = FastAPI()

# Limitador por IP
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

full_roles = RoleChecker(["Organizador", "Supervisor", "Participante"])
restricted_roles = RoleChecker(["Organizador", "Supervisor"])
supervisor_role = RoleChecker(["Supervisor"])


@app.get("/", tags=["Inicio"], summary="Home")
def home():
    return "Bienvenido a la api de Incidentes"


@app.post("/incidentes", tags=["Incidentes"], summary="Agregar Incidentes", response_model=Salida)
@limiter.limit("5/minute")
async def crear_incidente( request: Request, incidente: CrearIncidente, user:Usuario =Depends(full_roles)) -> Salida:
    cn = ConexionDB(user.username, user.password)
    incidente_dao = IncidenteDAO(cn.db)
    salida = incidente_dao.registrar_incidente(incidente)
    cn.cerrar()
    return salida

@app.put("/incidentes/{idIncidente}", tags=["Incidentes"], summary="Editar incidente", response_model=Salida)
@limiter.limit("5/minute")
def editarincidente(request:Request, idIncidente:str, incidente:EditarIncidente, user:Usuario = Depends(restricted_roles))-> Salida:
    cn = ConexionDB(user.username, user.password)
    incidente_dao = IncidenteDAO(cn.db)
    salida =  incidente_dao.editar_incidente(idIncidente, incidente)
    cn.cerrar()
    return salida

@app.delete("/incidentes/borrar/{idIncidente}", tags= ["Incidentes"], summary="Borrar incidente", response_model=Salida)
@limiter.limit("5/minute")
def borrarIncidente(request:Request, idIncidente:str, user:Usuario = Depends (supervisor_role)) -> Salida:
    cn = ConexionDB(user.username, user.password)
    incidente_dao= IncidenteDAO(cn.db)
    salida = incidente_dao.borrar_incidente(idIncidente)
    cn.cerrar()
    return salida

@app.get( "/incidentes/{idIncidente}", tags=["Incidentes"], summary="Buscar incidente por su id", response_model=IncidenteSalida)
@limiter.limit("5/minute")
async def buscarXId( request: Request, idIncidente: str, user:Usuario = Depends (full_roles)) -> IncidenteSalida:
    cn = ConexionDB(user.username, user.password)
    incidente_dao = IncidenteDAO(cn.db)
    salida = incidente_dao.consultaId(idIncidente)
    cn.cerrar()
    return salida

@app.get("/incidentes", tags=["Incidentes"], summary="Consultar todos los incidentes", response_model=IncidentesSalida)
@limiter.limit("5/minute")
async def consultaGeneral(request: Request, user:Usuario = Depends (full_roles)) -> IncidentesSalida:
    cn = ConexionDB(user.username, user.password)
    incidente_dao = IncidenteDAO(cn.db)
    salida = incidente_dao.consultaGeneral()
    cn.cerrar()
    return salida

@app.get("/incidentes/estatus/{estatus}", tags=["Incidentes"], summary="Consultar incidentes por estatus", response_model=IncidentesSalida)
@limiter.limit("5/minute")
async def consultaPorEstatus(request: Request, estatus: str, user:Usuario = Depends (full_roles)) -> IncidentesSalida:
    cn = ConexionDB(user.username, user.password)
    incidente_dao = IncidenteDAO(cn.db)
    salida = incidente_dao.consultaPorEstatus(estatus)
    cn.cerrar()
    return salida
    
@app.get("/incidentes/prioridad/{prioridad}", tags=["Incidentes"], summary="Consultar incidentes por prioridad", response_model=IncidentesSalida)
@limiter.limit("5/minute")
async def consultaPorPrioridad(request: Request, prioridad: str, user:Usuario = Depends (full_roles)) -> IncidentesSalida:
    cn = ConexionDB(user.username, user.password)
    incidente_dao = IncidenteDAO(cn.db)
    salida = incidente_dao.consultaPorPrioridad(prioridad)
    cn.cerrar()
    return salida

@app.put("/incidentes/estatus/{idIncidente}", tags=["Incidentes"], summary="Cambio de Estatus", response_model=Salida)
@limiter.limit("5/minute")
def cambioEstatus(request: Request, idIncidente: str, estatus: str, user:Usuario = Depends (restricted_roles)) -> Salida:
    cn = ConexionDB(user.username, user.password)
    incidente_dao = IncidenteDAO(cn.db)
    salida = incidente_dao.cambio_estatus(idIncidente, estatus)
    cn.cerrar()
    return salida

@app.put("/incidentes/atencion/{idIncidente}", tags=["Incidentes"], summary="Registro de atención", response_model=Salida)
@limiter.limit("5/minute")
def registroAtencion(request: Request, idIncidente: str, atencion: RegistroAtencion, user:Usuario = Depends (restricted_roles)) -> Salida:
    cn = ConexionDB(user.username, user.password)
    incidente_dao = IncidenteDAO(cn.db)
    salida = incidente_dao.registro_atencion(idIncidente, atencion)
    cn.cerrar()
    return salida

@app.get("/incidentes/evidencias/{idIncidente}", tags=["Incidentes"], summary="Consulta de Evidencias", response_model=EvidenciasSalida)
@limiter.limit("5/minute")
def consultaEvidencias(request: Request, idIncidente: str, user:Usuario = Depends (full_roles)) -> EvidenciasSalida:
    cn = ConexionDB(user.username, user.password)
    incidente_dao = IncidenteDAO(cn.db)
    salida = incidente_dao.consulta_evidencias(idIncidente)
    cn.cerrar()
    return salida

if __name__ == '__main__':
   uvicorn.run("main:app",reload=True)
