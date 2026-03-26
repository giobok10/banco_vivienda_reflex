import random
from dataclasses import dataclass
from datetime import datetime

import reflex as rx
from sqlalchemy import text

from .models import Cliente, Cuenta, Pago, Prestamo, Rol, Usuario
from .security import hash_password, verify_password

ROLE_ADMIN = 1
ROLE_COLABORADOR = 2
ROLE_CLIENTE = 3


@dataclass
class ClienteSnapshot:
    nombre: str
    cuentas: list[Cuenta]
    prestamos: list[Prestamo]
    pagos: list[Pago]


def get_usuario_by_username(session, username: str) -> Usuario | None:
    return session.exec(Usuario.select().where(Usuario.username == username)).first()


def login_user(session, username: str, password: str) -> Usuario | None:
    user = get_usuario_by_username(session, username)
    if not user:
        return None
    if ":" in user.password_hash and verify_password(password, user.password_hash):
        return user
    # Compatibilidad temporal para usuarios viejos en texto plano.
    if user.password_hash == password:
        user.password_hash = hash_password(password)
        session.add(user)
        session.commit()
        return user
    return None


def get_cliente_by_usuario_id(session, id_usuario: int) -> Cliente | None:
    return session.exec(Cliente.select().where(Cliente.id_usuario == id_usuario)).first()


def get_cliente_by_dpi(session, dpi: str) -> Cliente | None:
    return session.exec(Cliente.select().where(Cliente.dpi == dpi)).first()


def get_cliente_snapshot(session, cliente: Cliente) -> ClienteSnapshot:
    cuentas = session.exec(Cuenta.select().where(Cuenta.id_cliente == cliente.id_cliente)).all()
    prestamos = session.exec(Prestamo.select().where(Prestamo.id_cliente == cliente.id_cliente)).all()
    pagos = session.exec(
        Pago.select().where(
            Pago.id_prestamo.in_([p.id_prestamo for p in prestamos])  # type: ignore[attr-defined]
        )
    ).all() if prestamos else []
    return ClienteSnapshot(
        nombre=f"{cliente.nombres} {cliente.apellidos}",
        cuentas=cuentas,
        prestamos=prestamos,
        pagos=pagos,
    )


def create_usuario_y_cliente(
    session,
    username: str,
    password: str,
    id_rol: int,
    dpi: str,
    nombres: str,
    apellidos: str,
) -> None:
    if len(username) < 4:
        raise ValueError("El usuario debe tener al menos 4 caracteres.")
    if len(password) < 8:
        raise ValueError("La clave debe tener al menos 8 caracteres.")
    if not dpi.isdigit() or len(dpi) != 13:
        raise ValueError("El DPI debe tener 13 digitos numericos.")

    existing = get_usuario_by_username(session, username)
    if existing:
        raise ValueError("El usuario ya existe.")

    if get_cliente_by_dpi(session, dpi):
        raise ValueError("El DPI ya existe.")

    nuevo_usuario = Usuario(
        username=username,
        password_hash=hash_password(password),
        id_rol=id_rol,
    )
    session.add(nuevo_usuario)
    session.commit()
    session.refresh(nuevo_usuario)

    if id_rol == ROLE_CLIENTE:
        nuevo_cliente = Cliente(
            id_usuario=nuevo_usuario.id_usuario,
            dpi=dpi,
            nombres=nombres,
            apellidos=apellidos,
        )
        session.add(nuevo_cliente)
        session.commit()


def abrir_cuenta(session, cliente: Cliente, tipo_cuenta: str = "Ahorro", saldo_inicial: float = 500.0) -> None:
    numero = f"4550{random.randint(100000, 999999)}"
    cuenta = Cuenta(
        id_cliente=cliente.id_cliente,
        numero_cuenta=numero,
        tipo_cuenta=tipo_cuenta,
        saldo=saldo_inicial,
    )
    session.add(cuenta)
    session.commit()


def crear_prestamo(
    session,
    cliente: Cliente,
    monto: float = 5000.0,
    tasa_interes: float = 10.0,
    plazo_meses: int = 12,
) -> None:
    prestamo = Prestamo(
        id_cliente=cliente.id_cliente,
        monto_aprobado=monto,
        saldo_pendiente=monto,
        tasa_interes=tasa_interes,
        plazo_meses=plazo_meses,
        estado="Activo",
    )
    session.add(prestamo)
    session.commit()


def registrar_pago(session, prestamo: Prestamo, monto: float) -> None:
    if monto <= 0:
        raise ValueError("Monto invalido.")
    if monto > prestamo.saldo_pendiente:
        raise ValueError("El monto excede el saldo pendiente.")

    cuentas = session.exec(
        Cuenta.select()
        .where(Cuenta.id_cliente == prestamo.id_cliente)
        .order_by(Cuenta.saldo.desc())
    ).all()

    if not cuentas:
        raise ValueError("El cliente no tiene cuentas para debitar.")

    saldo_total = sum(float(c.saldo) for c in cuentas)
    if saldo_total < monto:
        raise ValueError("Fondos insuficientes.")

    restante = monto
    for cuenta in cuentas:
        if restante <= 0:
            break
        saldo_actual = float(cuenta.saldo)
        debito = min(saldo_actual, restante)
        cuenta.saldo = saldo_actual - debito
        restante -= debito
        session.add(cuenta)

    prestamo.saldo_pendiente = float(prestamo.saldo_pendiente) - monto
    if prestamo.saldo_pendiente <= 0:
        prestamo.saldo_pendiente = 0
        prestamo.estado = "Pagado"
    session.add(prestamo)

    pago = Pago(
        id_prestamo=prestamo.id_prestamo,
        monto=monto,
        fecha_pago=datetime.utcnow(),
    )
    session.add(pago)
    session.commit()


def obtener_usuarios(session) -> list[Usuario]:
    return session.exec(Usuario.select()).all()


def obtener_roles(session) -> list[Rol]:
    return session.exec(Rol.select()).all()


def registrar_bitacora(session, id_usuario: int | None, accion: str) -> None:
    session.execute(
        text("INSERT INTO bitacora (id_usuario, accion) VALUES (:id_usuario, :accion)"),
        {"id_usuario": id_usuario, "accion": accion},
    )
    session.commit()
