from datetime import datetime

from bson import ObjectId
from pymongo import MongoClient

from models import CrearIncidente, IncidenteSalida, IncidentesSalida, Salida, EditarIncidente, RegistroAtencion, EvidenciasSalida

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
        self.incidentes = self.db.incidentes
        self.view = self.db.IncidentesView
        self.eventos = self.db.client[EVENTOS_DATABASE][EVENTOS_COLLECTION]
        self.eventos_view = self.db.client[EVENTOS_DATABASE].eventosView
        self.usuarios = self.db.client[USUARIOS_DATABASE].UsuariosView


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

            result=self.incidentes.insert_one(data)
            return Salida(codigo=201, mensaje="Incidente registrado exitosamente")
        except Exception as ex:
            return Salida(codigo=500, mensaje=f"Error: {ex}")

    def editar_incidente(self, idIncidente, incidente: EditarIncidente):
        respuesta = self.consultaId(idIncidente)
        salida = Salida(codigo=0, mensaje="")

        if respuesta.codigo == 200 and respuesta.incidentes != None:

            estatusActual = respuesta.incidentes["estatus"]

            if estatusActual == "Reportado" or estatusActual == "Cancelado":
                data = incidente.model_dump(exclude_unset=True)

                if data.keys():
                    result = self.incidentes.update_one(
                        {"_id": ObjectId(idIncidente)},
                        {"$set": data}
                    )

                    if result.modified_count > 0:
                        salida.codigo = 200
                        salida.mensaje = f"El incidente con id: {idIncidente}, ha sido editado con exito"
                    else:
                        salida.codigo = 500
                        salida.mensaje = "No se pudo editar el incidente"
                
                else:
                    salida.codigo = 400
                    salida.mensaje = "No se proporcionaron los valores a editar"
            else:
                salida.codigo = 404
                salida.mensaje = "El incidente solo se puede editar si está en Reportado o Cancelado"

        else:
            salida.codigo = 404
            salida.mensaje = f"El incidente con id: {idIncidente} no se encontró en la BD"

        return salida    

    def borrar_incidente(self, idIncidente):
        respuesta = self.consultaId(idIncidente)
        salida = Salida (codigo = 0, mensaje = "")
        
        if respuesta.codigo==200 and respuesta.incidentes!=None:
            
            result = self.incidentes.delete_one({"_id":ObjectId(idIncidente)})
            if result.deleted_count > 0:
                salida.codigo = 200
                salida.mensaje= "El incidente se ha eliminado con éxito"
            else:
                salida.codigo = 404
                salida.mensaje = f"No se pudo eliminar el incidente con id: {idIncidente}"
        else: 
            salida.codigo = 500
            salida.mensaje = f"El incidente con id {idIncidente} no se encontró en la BD"
        return salida
    
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

    def cambio_estatus(self, idIncidente, estatus) -> Salida:
        respuesta = self.consultaId(idIncidente)
        salida = Salida(codigo=0, mensaje="")
        
        if respuesta.codigo==200 and respuesta.incidentes!= None:
            estatusActual = respuesta.incidentes["estatus"]
            
            
            if estatusActual == "Reportado" and estatus == "Cancelado":
                result = self.incidentes.update_one({"_id":ObjectId(idIncidente)}, {"$set":{"estatus":estatus}})
                if result.modified_count > 0:
                    salida.codigo = 200
                    salida.mensaje = "El cambio de estatus ha sido exitoso"
                else: 
                    salida.codigo=500
                    salida.mensaje ="No se pudo cambiar el estatus del incidente"
            else:
                salida.codigo = 404
                salida.mensaje = "El cambio de estatus solo es permitido de Reportado a Cancelado"
                
            if estatusActual == "En Atencion" and estatus == "Atendido":
                result = self.incidentes.update_one({"_id":ObjectId(idIncidente)}, {"$set":{"estatus":estatus}})
                
                if result.modified_count > 0:
                    salida.codigo = 200
                    salida.mensaje = "El cambio de estatus ha sido exitoso"
                else: 
                    salida.codigo=500
                    salida.mensaje ="No se pudo cambiar el estatus del incidente"
            else:
                salida.codigo = 404
                salida.mensaje = "El cambio de estatus solo es permitido de En Atencion a Atendido"        
        else: 
            salida.codigo = 404
            salida.mensaje = f"El incidente con id: {idIncidente}, no existe"
        
        return salida            
    
    def registro_atencion(self, idIncidente, atencion: RegistroAtencion) -> Salida:
        respuesta = self.consultaId(idIncidente)
        salida = Salida(codigo=0, mensaje="")

        if respuesta.codigo == 200 and respuesta.incidentes != None:

            incidente = respuesta.incidentes
            estatusActual = incidente["estatus"]

            if estatusActual == "Reportado":
                if atencion.estatus == "En Atencion":

                    usuario = self._buscar_usuario(atencion.atendidoPor.idUsuario)

                    if usuario != None:

                        fechaIncidente = incidente["fechaIncidente"]

                        if atencion.fechaAtencion.date() >= fechaIncidente.date():

                            data = atencion.model_dump(exclude_unset=True)

                            result = self.incidentes.update_one(
                                {"_id": ObjectId(idIncidente)},
                                {"$set": data}
                            )

                            if result.modified_count > 0:
                                salida.codigo = 200
                                salida.mensaje = "La atención del incidente se registró correctamente"
                            else:
                                salida.codigo = 500
                                salida.mensaje = "No se pudo registrar la atención del incidente"
                        else:
                            salida.codigo = 400
                            salida.mensaje = "La fecha de atención no puede ser menor que la fecha del incidente"
                    else:
                        salida.codigo = 404
                        salida.mensaje = "El usuario que atiende el incidente no existe"
                else:
                    salida.codigo = 400
                    salida.mensaje = "El nuevo estatus debe ser En Atencion o Atendido"
            else:
                salida.codigo = 400
                salida.mensaje = "El incidente debe estar en estatus Reportado para registrar atención"

        else:
            salida.codigo = 404
            salida.mensaje = f"El incidente con id {idIncidente} no existe"

        return salida
    
    def consulta_evidencias(self, idIncidente):
        salida = EvidenciasSalida(codigo=0, mensaje="", incidente=None)

        if ObjectId.is_valid(idIncidente):

            incidente = self.incidentes.find_one(
                {"_id": ObjectId(idIncidente)}
            )

            if incidente != None:

                data = {
                    "nombre": incidente["nombre"],
                    "evidencias": incidente.get("evidencias", [])
                }

                salida.codigo = 200
                salida.mensaje = "Consulta de evidencias exitosa"
                salida.incidente = data

            else:
                salida.codigo = 404
                salida.mensaje = "El incidente no existe"

        else:
            salida.codigo = 404
            salida.mensaje = "El id del incidente no es válido"

        return salida       

EventoDAO = IncidenteDAO
