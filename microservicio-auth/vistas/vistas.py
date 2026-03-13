import logging
from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from modelos import db, Usuario, UsuarioSchema
from passlib.context import CryptContext

logger = logging.getLogger("auth-service")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
usuario_schema = UsuarioSchema()

class VistaLogin(Resource):
    def post(self):
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return {"mensaje": "Usuario y contraseña requeridos"}, 400

        usuario = Usuario.query.filter(Usuario.username == username).first()

        if usuario and pwd_context.verify(password, usuario.password_hash):
            additional_claims = {"rol": usuario.rol, "pais": usuario.pais}
            token_de_acceso = create_access_token(identity=usuario.username, additional_claims=additional_claims)
            logger.info(f"LOGIN_OK | usuario={username} | rol={usuario.rol} | pais={usuario.pais}")
            return {"token": token_de_acceso}
        else:
            logger.warning(f"LOGIN_FAILED | usuario={username} | ip={request.remote_addr}")
            return {"mensaje": "Nombre de usuario o contraseña incorrectos"}, 401

class VistaSignUp(Resource):
    def post(self):
        data = request.json
        nuevo_usuario = Usuario(
            username=data["username"],
            password_hash=pwd_context.hash(data["password"]),
            rol=data["rol"],
            pais=data["pais"]
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        return usuario_schema.dump(nuevo_usuario)
