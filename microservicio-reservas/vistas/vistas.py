import os
import logging
import requests
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt
from modelos import db, Reserva, ReservaSchema
from cryptography.fernet import Fernet

logger = logging.getLogger("reservas-service")
reserva_schema = ReservaSchema()

FERNET_KEY = os.getenv("FERNET_KEY", "default-fernet-key").encode()
cipher_suite = Fernet(FERNET_KEY)

AUDIT_SERVICE_URL = os.getenv("AUDIT_SERVICE_URL", "http://localhost:8001/audit")

def encrypt_field(value: str) -> str:
    return cipher_suite.encrypt(value.encode()).decode()

def decrypt_field(value: str) -> str:
    return cipher_suite.decrypt(value.encode()).decode()

def log_audit(usuario: str, accion: str, entidad_id: str):
    try:
        requests.post(AUDIT_SERVICE_URL, json={
            "usuario": usuario,
            "accion": accion,
            "entidad_id": entidad_id
        }, timeout=1)
    except:
        pass

class VistaReservas(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        pais = claims.get("pais")
        usuario = claims.get("sub")
        reservas = Reserva.query.filter(Reserva.pais == pais).all()
        logger.info(f"GET_RESERVAS | usuario={usuario} | pais={pais} | total={len(reservas)}")
        return [
            {
                "id": r.id,
                "pais": r.pais,
                "estado": r.estado,
                "email": decrypt_field(r.email_cifrado),
                "telefono": decrypt_field(r.telefono_cifrado)
            } for r in reservas
        ]

    def post(self):
        data = request.json
        nueva_reserva = Reserva(
            pais=data["pais"],
            estado=data["estado"],
            email_cifrado=encrypt_field(data["email"]),
            telefono_cifrado=encrypt_field(data["telefono"])
        )
        db.session.add(nueva_reserva)
        db.session.commit()
        logger.info(f"RESERVA_CREATED | id={nueva_reserva.id} | pais={nueva_reserva.pais} | estado={nueva_reserva.estado}")
        return {"id": nueva_reserva.id}, 201

class VistaReserva(Resource):
    @jwt_required()
    def get(self, id_reserva):
        claims = get_jwt()
        usuario = claims.get("sub")
        res = Reserva.query.get_or_404(id_reserva)

        if claims.get("pais") != res.pais:
            logger.warning(f"ABAC_DENIED | usuario={usuario} | pais_usuario={claims.get('pais')} | pais_reserva={res.pais} | reserva_id={id_reserva}")
            log_audit(usuario, "UNAUTHORIZED_ACCESS_ATTEMPT", str(id_reserva))
            return {"mensaje": "Acceso denegado: pais no coincide"}, 403

        logger.info(f"GET_RESERVA_OK | usuario={usuario} | reserva_id={id_reserva} | pais={res.pais}")
        return {
            "id": res.id,
            "pais": res.pais,
            "estado": res.estado,
            "email": decrypt_field(res.email_cifrado),
            "telefono": decrypt_field(res.telefono_cifrado)
        }

    @jwt_required()
    def put(self, id_reserva):
        claims = get_jwt()
        usuario = claims.get("sub")
        res = Reserva.query.get_or_404(id_reserva)

        if claims.get("pais") != res.pais:
            logger.warning(f"ABAC_DENIED | usuario={usuario} | pais_usuario={claims.get('pais')} | pais_reserva={res.pais} | reserva_id={id_reserva}")
            log_audit(usuario, "UNAUTHORIZED_UPDATE_ATTEMPT", str(id_reserva))
            return {"mensaje": "Acceso denegado: pais no coincide"}, 403

        if res.estado == "CONFIRMED":
            logger.warning(f"IMMUTABILITY_BLOCKED | usuario={usuario} | reserva_id={id_reserva} | estado=CONFIRMED")
            log_audit(usuario, "ILLEGAL_MUTATION_ATTEMPT", str(id_reserva))
            return {"mensaje": "No se puede modificar una reserva CONFIRMADA"}, 403

        data = request.json
        if "email" in data: res.email_cifrado = encrypt_field(data["email"])
        if "telefono" in data: res.telefono_cifrado = encrypt_field(data["telefono"])
        if "estado" in data: res.estado = data["estado"]
        db.session.commit()
        logger.info(f"RESERVA_UPDATED | usuario={usuario} | reserva_id={id_reserva}")
        return {"mensaje": "Actualizada exitosamente"}
