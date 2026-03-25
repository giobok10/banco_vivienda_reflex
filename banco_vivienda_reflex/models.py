import reflex as rx
from typing import Optional
from sqlmodel import Field

class Usuario(rx.Model, table=True):
    __tablename__ = "usuarios"
    id_usuario: Optional[int] = Field(default=None, primary_key=True)
    username: str
    password_hash: str
    id_rol: int

class Cliente(rx.Model, table=True):
    __tablename__ = "clientes"
    id_cliente: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int
    dpi: str
    nombres: str
    apellidos: str

class Cuenta(rx.Model, table=True):
    __tablename__ = "cuentas"
    id_cuenta: Optional[int] = Field(default=None, primary_key=True)
    id_cliente: int
    numero_cuenta: str
    tipo_cuenta: str
    saldo: float

class Prestamo(rx.Model, table=True):
    __tablename__ = "prestamos"
    id_prestamo: Optional[int] = Field(default=None, primary_key=True)
    id_cliente: int
    monto_aprobado: float
    saldo_pendiente: float
    tasa_interes: float
    plazo_meses: int
    estado: str