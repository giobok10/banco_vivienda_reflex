import reflex as rx

from .models import Cuenta, Pago, Prestamo, Usuario
from .services import (
    ROLE_ADMIN,
    ROLE_CLIENTE,
    create_usuario_y_cliente,
    crear_prestamo,
    get_cliente_by_dpi,
    get_cliente_by_usuario_id,
    get_cliente_snapshot,
    get_usuario_by_username,
    login_user,
    obtener_usuarios,
    abrir_cuenta,
    registrar_bitacora,
    registrar_pago,
)


class State(rx.State):
    user_input: str = ""
    pass_input: str = ""
    error_msg: str = ""

    user_dpi_input: str = ""
    user_nombres_input: str = ""
    user_apellidos_input: str = ""
    user_role_input: str = str(ROLE_CLIENTE)

    logged_user: str = rx.LocalStorage("")
    user_role: str = rx.LocalStorage("0")
    is_authenticated: str = rx.LocalStorage("false")

    lista_usuarios: list[Usuario] = []
    mis_cuentas: list[Cuenta] = []
    mis_prestamos: list[Prestamo] = []
    mis_pagos: list[Pago] = []
    cliente_nombre_display: str = ""

    monto_pago: str = ""
    search_dpi: str = ""

    # Setters explicitos para evitar deprecations futuras de Reflex.
    def set_user_input(self, value: str):
        self.user_input = value

    def set_pass_input(self, value: str):
        self.pass_input = value

    def set_user_dpi_input(self, value: str):
        self.user_dpi_input = value

    def set_user_nombres_input(self, value: str):
        self.user_nombres_input = value

    def set_user_apellidos_input(self, value: str):
        self.user_apellidos_input = value

    def set_user_role_input(self, value: str):
        self.user_role_input = value

    def set_search_dpi(self, value: str):
        self.search_dpi = value

    def set_monto_pago(self, value: str):
        self.monto_pago = value

    @rx.var
    def es_admin(self) -> bool:
        return self.user_role == str(ROLE_ADMIN)

    @rx.var
    def es_cliente(self) -> bool:
        return self.user_role == str(ROLE_CLIENTE)

    @rx.var
    def es_staff(self) -> bool:
        return self.is_authenticated == "true" and not self.es_cliente

    def _reset_cliente_data(self) -> None:
        self.mis_cuentas = []
        self.mis_prestamos = []
        self.mis_pagos = []
        self.cliente_nombre_display = ""

    def _usuario_actual(self, session):
        if not self.logged_user:
            return None
        return get_usuario_by_username(session, self.logged_user)

    def _cliente_actual(self, session):
        user = self._usuario_actual(session)
        if not user:
            return None
        return get_cliente_by_usuario_id(session, user.id_usuario)

    def login_handler(self):
        with rx.session() as session:
            user = login_user(session, self.user_input.strip(), self.pass_input)
            if not user:
                self.is_authenticated = "false"
                self.error_msg = "USUARIO O CLAVE INCORRECTOS"
                return

            self.logged_user = user.username
            self.user_role = str(user.id_rol)
            self.is_authenticated = "true"
            self.error_msg = ""
            registrar_bitacora(session, user.id_usuario, "Inicio de sesion")

        if self.es_cliente:
            self.cargar_datos_cliente()
        return rx.redirect("/dashboard")

    def check_login(self):
        if self.is_authenticated != "true":
            return rx.redirect("/")

    def logout(self):
        with rx.session() as session:
            user = get_usuario_by_username(session, self.logged_user)
            registrar_bitacora(session, user.id_usuario if user else None, "Cierre de sesion")

        self.is_authenticated = "false"
        self.logged_user = ""
        self.user_role = "0"
        self.user_input = ""
        self.pass_input = ""
        self._reset_cliente_data()
        return rx.redirect("/")

    def obtener_todos_usuarios(self):
        if not self.es_admin:
            return rx.window_alert("Acceso denegado.")
        with rx.session() as session:
            self.lista_usuarios = obtener_usuarios(session)

    def crear_usuario(self):
        if not self.es_admin:
            return rx.window_alert("Solo admin puede crear usuarios.")
        if not self.user_input or not self.pass_input or not self.user_dpi_input:
            return rx.window_alert("Llene usuario, password y DPI.")

        nombres = self.user_nombres_input or self.user_input
        apellidos = self.user_apellidos_input or "S/A"
        id_rol = int(self.user_role_input)

        with rx.session() as session:
            try:
                create_usuario_y_cliente(
                    session=session,
                    username=self.user_input.strip(),
                    password=self.pass_input,
                    id_rol=id_rol,
                    dpi=self.user_dpi_input.strip(),
                    nombres=nombres.strip(),
                    apellidos=apellidos.strip(),
                )
            except ValueError as exc:
                return rx.window_alert(str(exc))

        self.obtener_todos_usuarios()
        self.user_input = ""
        self.pass_input = ""
        self.user_dpi_input = ""
        self.user_nombres_input = ""
        self.user_apellidos_input = ""
        return rx.window_alert("Usuario creado correctamente.")

    def cargar_datos_cliente(self):
        with rx.session() as session:
            cliente = self._cliente_actual(session)
            if not cliente:
                self._reset_cliente_data()
                return
            snapshot = get_cliente_snapshot(session, cliente)
            self.cliente_nombre_display = snapshot.nombre
            self.mis_cuentas = snapshot.cuentas
            self.mis_prestamos = snapshot.prestamos
            self.mis_pagos = snapshot.pagos

    def _resolver_cliente_objetivo(self, session):
        if self.es_staff:
            if not self.search_dpi.strip():
                return None
            return get_cliente_by_dpi(session, self.search_dpi.strip())
        return self._cliente_actual(session)

    def abrir_nueva_cuenta(self):
        with rx.session() as session:
            cliente = self._resolver_cliente_objetivo(session)
            if not cliente:
                return rx.window_alert("Cliente no encontrado.")
            abrir_cuenta(session, cliente)

        if self.es_admin:
            return self.buscar_cliente_por_dpi()
        self.cargar_datos_cliente()
        return rx.window_alert("Cuenta creada con exito.")

    def solicitar_prestamo(self):
        with rx.session() as session:
            cliente = self._resolver_cliente_objetivo(session)
            if not cliente:
                return rx.window_alert("Cliente no encontrado.")
            crear_prestamo(session, cliente)

        if self.es_admin:
            return self.buscar_cliente_por_dpi()
        self.cargar_datos_cliente()
        return rx.window_alert("Prestamo creado con exito.")

    def realizar_pago(self, id_prestamo: int):
        if not self.es_cliente:
            return rx.window_alert("Solo clientes pueden realizar pagos.")
        if not self.monto_pago:
            return rx.window_alert("Ingrese un monto valido.")
        try:
            monto = float(self.monto_pago)
        except ValueError:
            return rx.window_alert("El monto debe ser numerico.")

        with rx.session() as session:
            cliente_actual = self._cliente_actual(session)
            if not cliente_actual:
                return rx.window_alert("Cliente no encontrado.")
            prestamo = session.exec(
                Prestamo.select().where(Prestamo.id_prestamo == id_prestamo)
            ).first()
            if not prestamo:
                return rx.window_alert("Prestamo no encontrado.")
            if prestamo.id_cliente != cliente_actual.id_cliente:
                return rx.window_alert("No puede pagar prestamos de otro cliente.")
            try:
                registrar_pago(session, prestamo, monto)
            except ValueError as exc:
                return rx.window_alert(str(exc))

        self.monto_pago = ""
        if self.es_admin:
            return self.buscar_cliente_por_dpi()
        self.cargar_datos_cliente()
        return rx.window_alert("Pago realizado correctamente.")

    def buscar_cliente_por_dpi(self):
        if not self.es_staff:
            return rx.window_alert("Solo admin/colaborador puede buscar por DPI.")
        if not self.search_dpi.strip():
            self._reset_cliente_data()
            return rx.window_alert("Ingrese un DPI valido.")
        if not self.search_dpi.isdigit() or len(self.search_dpi) != 13:
            self._reset_cliente_data()
            return rx.window_alert("DPI invalido (13 digitos).")

        with rx.session() as session:
            cliente = get_cliente_by_dpi(session, self.search_dpi.strip())
            if not cliente:
                self._reset_cliente_data()
                return rx.window_alert("Cliente no encontrado.")
            snapshot = get_cliente_snapshot(session, cliente)
            self.cliente_nombre_display = snapshot.nombre
            self.mis_cuentas = snapshot.cuentas
            self.mis_prestamos = snapshot.prestamos
            self.mis_pagos = snapshot.pagos
        return rx.window_alert(f"Mostrando datos de {self.cliente_nombre_display}.")