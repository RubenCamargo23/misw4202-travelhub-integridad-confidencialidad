import os
import hmac
import hashlib
import logging
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt
from modelos import db, AuditLog, AuditLogSchema
from datetime import datetime

logger = logging.getLogger("audit-service")
audit_log_schema = AuditLogSchema()

HMAC_KEY = os.getenv("HMAC_KEY", "default-hmac-key").encode()

def calculate_hmac(usuario, accion, entidad_id, timestamp_str):
    message = f"{usuario}|{accion}|{entidad_id}|{timestamp_str}".encode()
    return hmac.new(HMAC_KEY, message, hashlib.sha256).hexdigest()

class VistaAudit(Resource):
    def post(self):
        data = request.json
        timestamp = datetime.utcnow()
        timestamp_str = timestamp.isoformat()

        hmac_hash = calculate_hmac(data["usuario"], data["accion"], data["entidad_id"], timestamp_str)

        nuevo_log = AuditLog(
            usuario=data["usuario"],
            accion=data["accion"],
            entidad_id=data["entidad_id"],
            timestamp=timestamp,
            hmac_hash=hmac_hash
        )
        db.session.add(nuevo_log)
        db.session.commit()
        logger.info(f"AUDIT_RECORDED | id={nuevo_log.id} | usuario={data['usuario']} | accion={data['accion']} | entidad_id={data['entidad_id']} | hmac={hmac_hash[:16]}...")
        return {"id": nuevo_log.id}, 201

class VistaAuditVerify(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        if claims.get("rol") != "admin":
            logger.warning(f"AUDIT_VERIFY_DENIED | usuario={claims.get('sub')} | rol={claims.get('rol')}")
            return {"mensaje": "Acceso denegado"}, 403

        logs = AuditLog.query.all()
        resultados = []
        for log in logs:
            calculado = calculate_hmac(log.usuario, log.accion, log.entidad_id, log.timestamp.isoformat())
            es_valido = hmac.compare_digest(calculado, log.hmac_hash)
            if not es_valido:
                logger.error(f"HMAC_TAMPERED | id={log.id} | usuario={log.usuario} | accion={log.accion}")
            resultados.append({
                "id": log.id,
                "usuario": log.usuario,
                "accion": log.accion,
                "entidad_id": log.entidad_id,
                "verified": es_valido
            })
        logger.info(f"AUDIT_VERIFY | solicitado_por={claims.get('sub')} | total={len(logs)} | todos_validos={all(r['verified'] for r in resultados)}")
        return resultados
