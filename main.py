from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Request, Response

from dao import ConexionDB, IncidenteDAO
from models import CrearIncidente, Salida, IncidenteSalida, IncidentesSalida, EditarIncidente, RegistroAtencion, EvidenciasSalida


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.cn = ConexionDB()
    yield
    app.cn.cerrar()


app = FastAPI(lifespan=lifespan)


@app.get("/", tags=["Inicio"], summary="Home")
def home():
    return "Bienvenido a la api de Incidentes"


@app.post("/incidentes", tags=["Incidentes"], summary="Agregar Incidentes", response_model=Salida)
async def crear_incidente( request: Request, incidente: CrearIncidente) -> Salida:
    incidente_dao = IncidenteDAO(request.app.cn.db)
    salida = incidente_dao.registrar_incidente(incidente)
    return salida

@app.put("/incidentes/{idIncidente}", tags=["Incidentes"], summary="Editar incidente", response_model=Salida)
def editarincidente(request:Request, idIncidente:str, incidente:EditarIncidente)-> Salida:
    incidente_dao = IncidenteDAO(request.app.cn.db)
    return incidente_dao.editar_incidente(idIncidente, incidente)

@app.delete("/incidentes/borrar/{idIncidente}", tags= ["Incidentes"], summary="Borrar incidente", response_model=Salida)
def borrarIncidente(request:Request, idIncidente:str) -> Salida:
    incidente_dao= IncidenteDAO(request.app.cn.db)
    return incidente_dao.borrar_incidente(idIncidente)

@app.get( "/incidentes/{idIncidente}", tags=["Incidentes"], summary="Buscar incidente por su id", response_model=IncidenteSalida)
async def buscarXId( request: Request, idIncidente: str ) -> IncidenteSalida:
    incidente_dao = IncidenteDAO(request.app.cn.db)
    salida = incidente_dao.consultaId(idIncidente)
    return salida

@app.get("/incidentes", tags=["Incidentes"], summary="Consultar todos los incidentes", response_model=IncidentesSalida)
async def consultaGeneral(request: Request) -> IncidentesSalida:
    incidente_dao = IncidenteDAO(request.app.cn.db)
    return incidente_dao.consultaGeneral()

@app.get("/incidentes/estatus/{estatus}", tags=["Incidentes"], summary="Consultar incidentes por estatus", response_model=IncidentesSalida)
async def consultaPorEstatus(request: Request, estatus: str) -> IncidentesSalida:
    incidente_dao = IncidenteDAO(request.app.cn.db)
    return incidente_dao.consultaPorEstatus(estatus)

@app.get("/incidentes/prioridad/{prioridad}", tags=["Incidentes"], summary="Consultar incidentes por prioridad", response_model=IncidentesSalida)
async def consultaPorPrioridad(request: Request, prioridad: str) -> IncidentesSalida:
    incidente_dao = IncidenteDAO(request.app.cn.db)
    return incidente_dao.consultaPorPrioridad(prioridad)

@app.put("/incidentes/estatus/{idIncidente}", tags=["Incidentes"], summary="Cambio de Estatus", response_model=Salida)
def cambioEstatus(request: Request, idIncidente: str, estatus: str) -> Salida:
    incidente_dao = IncidenteDAO(request.app.cn.db)
    return incidente_dao.cambio_estatus(idIncidente, estatus)

@app.put("/incidentes/atencion/{idIncidente}", tags=["Incidentes"], summary="Registro de atención", response_model=Salida)
def registroAtencion(request: Request, idIncidente: str, atencion: RegistroAtencion) -> Salida:
    incidente_dao = IncidenteDAO(request.app.cn.db)
    return incidente_dao.registro_atencion(idIncidente, atencion)

@app.get("/incidentes/evidencias/{idIncidente}", tags=["Incidentes"], summary="Consulta de Evidencias", response_model=EvidenciasSalida)
def consultaEvidencias(request: Request, idIncidente: str) -> EvidenciasSalida:
    incidente_dao = IncidenteDAO(request.app.cn.db)
    return incidente_dao.consulta_evidencias(idIncidente)

if __name__ == '__main__':
   uvicorn.run("main:app",reload=True)
