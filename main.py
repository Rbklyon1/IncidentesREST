from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Request, Response

from dao import ConexionDB, IncidenteDAO
from models import CrearIncidente, Salida, IncidenteSalida, IncidentesSalida


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


@app.get("/incidentes", tags=["Incidentes"], summary="Consultar todos los incidentes", response_model=IncidentesSalida)
async def consultaGeneral(request: Request) -> IncidentesSalida:
    incidente_dao = IncidenteDAO(request.app.cn.db)
    return incidente_dao.consultaGeneral()


@app.get("/incidentes/estatus/{estatus}", tags=["Incidentes"], summary="Consultar incidentes por estatus", response_model=IncidentesSalida)
async def consultaPorEstatus(request: Request, estatus: str) -> IncidentesSalida:
    incidente_dao = IncidenteDAO(request.app.cn.db)
    return incidente_dao.consultaPorEstatus(estatus)


@app.get("/incidentes/priorirdad/{priorirdad}", tags=["Incidentes"], summary="Consultar incidentes por prioridad", response_model=IncidentesSalida)
async def consultaPorPrioridad(request: Request, priorirdad: str) -> IncidentesSalida:
    incidente_dao = IncidenteDAO(request.app.cn.db)
    return incidente_dao.consultaPorPrioridad(priorirdad)


@app.get( "/incidentes/{idIncidente}", tags=["Busqueda ID"], summary="Buscar incidente por su id", response_model=IncidenteSalida)
async def buscarXId( request: Request, idIncidente: str ) -> IncidenteSalida:
    incidente_dao = IncidenteDAO(request.app.cn.db)
    salida = incidente_dao.consultaId(idIncidente)
    return salida




if __name__ == '__main__':
   uvicorn.run("main:app",reload=True)
