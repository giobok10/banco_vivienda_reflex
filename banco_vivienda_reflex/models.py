import reflex as rx
from datetime import datetime
from typing import Optional
from sqlmodel import Field


@rx.ModelRegistry.register
class Usuario(rx.Model, table=True):
    __tablename__ = "usuarios"
    id_usuario: Optional[int] = Field(default=None, primary_key=True)
    username: str
    password_hash: str
    id_rol: int
    created_at: Optional[datetime] = None


@rx.ModelRegistry.register
class Rol(rx.Model, table=True):
    __tablename__ = "roles"
    id_rol: Optional[int] = Field(default=None, primary_key=True)
    nombre: str

@rx.ModelRegistry.register
class Cliente(rx.Model, table=True):
    __tablename__ = "clientes"
    id_cliente: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int
    dpi: str
    nombres: str
    apellidos: str

@rx.ModelRegistry.register
class Cuenta(rx.Model, table=True):
    __tablename__ = "cuentas"
    id_cuenta: Optional[int] = Field(default=None, primary_key=True)
    id_cliente: int
    numero_cuenta: str
    tipo_cuenta: str
    saldo: float

@rx.ModelRegistry.register
class Prestamo(rx.Model, table=True):
    __tablename__ = "prestamos"
    id_prestamo: Optional[int] = Field(default=None, primary_key=True)
    id_cliente: int
    monto_aprobado: float
    saldo_pendiente: float
    tasa_interes: float
    plazo_meses: int
    estado: str


@rx.ModelRegistry.register
class Pago(rx.Model, table=True):
    __tablename__ = "pagos"
    id_pago: Optional[int] = Field(default=None, primary_key=True)
    id_prestamo: int
    monto: float
    fecha_pago: Optional[datetime] = None


@rx.ModelRegistry.register
class Telefono(rx.Model, table=True):
    __tablename__ = "telefonos"
    id_telefono: Optional[int] = Field(default=None, primary_key=True)
    id_cliente: int
    numero: str


@rx.ModelRegistry.register
class Direccion(rx.Model, table=True):
    __tablename__ = "direcciones"
    id_direccion: Optional[int] = Field(default=None, primary_key=True)
    id_cliente: int
    direccion: str


@rx.ModelRegistry.register
class Bitacora(rx.Model, table=True):
    __tablename__ = "bitacora"
    id_log: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: Optional[int] = None
    accion: str
    fecha: Optional[datetime] = None