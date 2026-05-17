from datetime import datetime

from bson import ObjectId
from pymongo import MongoClient

from models import CrearIncidente, IncidenteSalida, IncidentesSalida, Salida

DATABASEURL = "mongodb://localhost:27017/"
DATABASE = "IncidentesDB"
EVENTOS_DATABASE = "EventosDB"
EVENTOS_COLLECTION = "eventos"
USUARIOS_DATABASE = "UsuariosDB"
USUARIOS_COLLECTION = "usuarios"


class ConexionDB:
    _cliente = None
    _db = None

    def __init__(self):
        try:
            self._cliente = MongoClient(DATABASEURL)
            self._db = self._cliente[DATABASE]
            print(f"Conectado con la BD: {DATABASE}")
        except Exception as ex:
            print(f"Error al conectar con la BD a causa de: {ex}")

    def cerrar(self):
        try:
            if self._cliente is not None:
                self._cliente.close()
            print(f"Conexion cerrada con la BD: {DATABASE}")
        except Exception as ex:
            print(f"Error al cerrar la conexion con la BD a causa de: {ex}")

    @property
    def db(self):
        return self._db


class IncidenteDAO:
    def __init__(self, db):
        self.db = db
        self.incidentes = self.db.Incidentes
        self.view = self.db.IncidentesView
        self.eventos = self.db.client[EVENTOS_DATABASE][EVENTOS_COLLECTION]
        self.eventos_view = self.db.client[EVENTOS_DATABASE].eventosView
        self.usuarios = self.db.client[USUARIOS_DATABASE][USUARIOS_COLLECTION]


    def _crear_filtro_id(self, campo_id: str, valor_id: str):
        filtros = [{campo_id: valor_id}]
        if ObjectId.is_valid(valor_id):
            filtros.append({"_id": ObjectId(valor_id)})
        return {"$or": filtros}

    def _buscar_evento(self, id_evento: str):
        filtro = self._crear_filtro_id("idEvento", id_evento)
        return (
            self.eventos.find_one(filtro)
            or self.eventos_view.find_one({"idEvento": id_evento})
        )

    def _buscar_usuario(self, id_usuario: str):
        filtro = self._crear_filtro_id("idUsuario", id_usuario)
        return self.usuarios.find_one(filtro)

    def registrar_incidente(self, incidente: CrearIncidente) -> Salida:
        try:
            evento = self._buscar_evento(incidente.evento.idEvento)
            if evento is None:
                return Salida(codigo=404, mensaje="El evento no existe")

            usuario = self._buscar_usuario(incidente.reportadoPor.idUsuario)
            if usuario is None:
                return Salida(
                    codigo=404,
                    mensaje="El usuario que reporta no existe",
                )

            data = incidente.model_dump(
                by_alias=False,
                exclude={"fechaIncidente", "estatus"},
            )
            data["fechaIncidente"] = datetime.now()
            data["estatus"] = "Reportado"

            self.incidentes.insert_one(data)
            return Salida(codigo=201, mensaje="Incidente registrado exitosamente")
        except Exception as ex:
            return Salida(codigo=500, mensaje=f"Error: {ex}")


    def consultaId(self, idIncidente: str) -> IncidenteSalida:
        salida = IncidenteSalida(codigo=0, mensaje="", incidentes=None)
        try:
            incidente = self.view.find_one({"idIncidente": idIncidente})
            if incidente is None:
                salida.codigo = 404
                salida.mensaje = "El incidente no existe"
                return salida

            salida.codigo = 200
            salida.mensaje = "Incidente encontrado"
            salida.incidentes = incidente
        except Exception as ex:
            salida.codigo = 500
            salida.mensaje = f"Error: {ex}"
        return salida

    def consultaGeneral(self) -> IncidentesSalida:
        salida = IncidentesSalida(codigo=200, mensaje="", incidentes=[])
        try:
            salida.codigo = 200
            salida.mensaje = "Listado de incidentes"
            salida.incidentes = list(self.view.find())
        except Exception as ex:
            salida.codigo = 404
            salida.mensaje = f"Error al consultar los incidentes, {ex}"
        return salida

    def consultaPorEstatus(self, estatus: str) -> IncidentesSalida:
        salida = IncidentesSalida(codigo=0, mensaje="", incidentes=[])
        estatus_permitidos = ["Reportado", "En Atención", "Atendido", "Cancelado"]
        if estatus not in estatus_permitidos:
            salida = IncidentesSalida( codigo=404, mensaje="El estatus no es un valor permitido", incidentes=None )
        else:
            try:
                salida.codigo = 200
                salida.mensaje = "Listado de incidentes"
                salida.incidentes = list(self.view.find({"estatus": estatus}))
            except Exception as ex:
                salida.codigo = 500
                salida.mensaje = f"Error al consultar los incidentes: {ex}"
        return salida

    def consultaPorPrioridad(self, prioridad: str) -> IncidentesSalida:
        salida = IncidentesSalida(codigo=0, mensaje="", incidentes=[])
        prioridades_permitidas = ["Urgente", "Normal", "Baja"]
        if prioridad not in prioridades_permitidas:
            salida = IncidentesSalida(
                codigo=404,
                mensaje="La prioridad no es un valor permitido",
                incidentes=None,
            )
        else:
            try:
                salida.codigo = 200
                salida.mensaje = "Listado de incidentes"
                salida.incidentes = list(self.view.find({"prioridad": prioridad}))
            except Exception as ex:
                salida.codigo = 500
                salida.mensaje = f"Error al consultar los incidentes: {ex}"
        return salida


EventoDAO = IncidenteDAO
