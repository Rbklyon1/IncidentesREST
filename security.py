from fastapi.security import HTTPBasic,HTTPBasicCredentials
from fastapi import Depends,HTTPException,status
from dao import Conexion,UsuarioDAO
from models import Usuario

security=HTTPBasic()
def getUser(credenciales:HTTPBasicCredentials=Depends(security)):
    cn=Conexion(credenciales.username,credenciales.password)
    usuarioDAO=UsuarioDAO(cn.db)
    usuario=usuarioDAO.autenticar(credenciales.username,credenciales.password)
    cn.cerrar()
    return usuario

class RoleChecker:
    def __init__(self,roles:list):
        self.roles_permitidos=roles
    def __call__(self, user:Usuario=Depends(getUser)):
        if user is None or user.rol not in self.roles_permitidos:
            raise HTTPException(status.HTTP_403_FORBIDDEN,detail="Sin autorizacion.")
        return user