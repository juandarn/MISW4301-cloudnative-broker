from enum import Enum
from db import db
import datetime
import uuid

class EstadoUsuario(Enum):
    POR_VERIFICAR = "POR_VERIFICAR"
    NO_VERIFICADO = "NO_VERIFICADO"
    VERIFICADO = "VERIFICADO"


class UsuarioModel(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.String(), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(), nullable=False, unique=True)
    email = db.Column(db.String(), nullable=False, unique=True)
    phoneNumber = db.Column(db.String())
    dni = db.Column(db.String())
    fullName = db.Column(db.String())
    password = db.Column(db.String(), nullable=False)
    salt = db.Column(db.String())
    token = db.Column(db.String(), nullable=True)
    status = db.Column(db.Enum(EstadoUsuario), nullable=True, default=EstadoUsuario.POR_VERIFICAR)
    expireAt = db.Column(db.DateTime(), nullable=True)
    createdAt = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    updatedAt = db.Column(db.DateTime(), default=datetime.datetime.utcnow)

    @property
    def status_value(self):
        return self.status.value if self.status else None
