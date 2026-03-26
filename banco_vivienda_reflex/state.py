import reflex as rx
import random
from .models import Usuario, Cliente, Cuenta, Prestamo
from sqlalchemy import text  # <-- IMPORTACIÓN CORRECTA


class State(rx.State):
    user_input: str = ""
    pass_input: str = ""
    error_msg: str = ""

    # NUEVO: DPI para creación de usuario
    user_dpi_input: str = ""

    # Usamos valores por defecto muy claros
    logged_user: str = rx.LocalStorage("")
    user_role: str = rx.LocalStorage("0")
    is_authenticated: str = rx.LocalStorage("false")

    # =========================
    # NUEVAS VARIABLES CRUD
    # =========================
    lista_usuarios: list[Usuario] = []
    user_role_input: str = "2"  # Por defecto cliente

    # =========================
    # DATOS DEL CLIENTE
    # =========================
    mis_cuentas: list[Cuenta] = []
    mis_prestamos: list[Prestamo] = []
    cliente_nombre_display: str = ""  # <-- NUEVO (evita "Pendiente")

    # =========================
    # PAGO
    # =========================
    monto_pago: str = ""

    # =========================
    # BÚSQUEDA POR DPI
    # =========================
    search_dpi: str = ""

    # =========================
    # LOGIN
    # =========================
    def login_handler(self):
        with rx.session() as session:
            user = session.exec(
                Usuario.select().where(
                    (Usuario.username == self.user_input)
                    & (Usuario.password_hash == self.pass_input)
                )
            ).first()

            if user:
                self.logged_user = str(user.username)
                self.user_role = str(user.id_rol)
                self.is_authenticated = "true"
                self.error_msg = ""

                # 🔥 NUEVO: cargar datos automáticamente si es cliente
                if self.user_role == "2":
                    self.cargar_datos_cliente()

                return rx.redirect("/dashboard")
            else:
                self.is_authenticated = "false"
                self.error_msg = "USUARIO O CLAVE INCORRECTOS"

    def check_login(self):
        if self.is_authenticated != "true":
            return rx.redirect("/")

    def logout(self):
        self.is_authenticated = "false"
        self.logged_user = ""
        self.user_role = "0"
        self.user_input = ""
        self.pass_input = ""
        return rx.redirect("/")

    # =========================
    # CRUD USUARIOS
    # =========================
    def obtener_todos_usuarios(self):
        with rx.session() as session:
            self.lista_usuarios = session.exec(Usuario.select()).all()

    def crear_usuario(self):
        # 1. VALIDACIÓN
        if not self.user_input or not self.pass_input or not self.user_dpi_input:
            return rx.window_alert("Llene todos los campos (incluyendo DPI)")

        username_creado = self.user_input

        with rx.session() as session:
            nuevo_usuario = Usuario(
                username=self.user_input,
                password_hash=self.pass_input,
                id_rol=int(self.user_role_input),
                dpi=self.user_dpi_input,
                nombre_completo=username_creado,  # 🔥 CORRECCIÓN (adiós Pendiente)
            )
            session.add(nuevo_usuario)
            session.commit()
            session.refresh(nuevo_usuario)

            if nuevo_usuario.id_rol == 2:
                nuevo_cliente = Cliente(
                    id_usuario=nuevo_usuario.id_usuario,
                    dpi=self.user_dpi_input,
                    nombres=username_creado,  # 🔥 CORRECCIÓN
                    apellidos="S/A",  # 🔥 limpio
                    direccion="Ciudad",
                    telefono="00000000"
                )
                session.add(nuevo_cliente)
                session.commit()

        self.obtener_todos_usuarios()

        self.user_input = ""
        self.pass_input = ""
        self.user_dpi_input = ""

        return rx.window_alert(
            f"Usuario y Cliente {username_creado} creados con éxito."
        )

    # =========================
    # CARGA DE DATOS CLIENTE
    # =========================
    def cargar_datos_cliente(self):
        with rx.session() as session:
            user_obj = session.exec(
                Usuario.select().where(
                    Usuario.username == self.logged_user
                )
            ).first()

            if user_obj:
                cliente_obj = session.exec(
                    Cliente.select().where(
                        Cliente.id_usuario == user_obj.id_usuario
                    )
                ).first()

                if cliente_obj:
                    self.mis_cuentas = session.exec(
                        Cuenta.select().where(
                            Cuenta.id_cliente == cliente_obj.id_cliente
                        )
                    ).all()

                    self.mis_prestamos = session.exec(
                        Prestamo.select().where(
                            Prestamo.id_cliente == cliente_obj.id_cliente
                        )
                    ).all()

    # =========================
    # NUEVO: PRODUCTOS
    # =========================
    def abrir_nueva_cuenta(self):
        with rx.session() as session:
            dpi_target = self.search_dpi if self.user_role == "1" else None

            if self.user_role != "1":
                user_obj = session.exec(
                    Usuario.select().where(
                        Usuario.username == self.logged_user
                    )
                ).first()

                cliente_obj = session.exec(
                    Cliente.select().where(
                        Cliente.id_usuario == user_obj.id_usuario
                    )
                ).first()
            else:
                cliente_obj = session.exec(
                    Cliente.select().where(
                        Cliente.dpi == dpi_target
                    )
                ).first()

            if not cliente_obj:
                return rx.window_alert("Cliente no encontrado")

            nueva = Cuenta(
                id_cliente=cliente_obj.id_cliente,
                numero_cuenta=f"4550{random.randint(100000, 999999)}",
                tipo_cuenta="Ahorro",
                saldo=500.00,
            )

            session.add(nueva)
            session.commit()

        # 🔥 REFRESCO AUTOMÁTICO
        if self.user_role == "1":
            self.buscar_cliente_por_dpi()
        else:
            self.cargar_datos_cliente()

        return rx.window_alert("¡Cuenta Aperturada con Éxito!")

    def solicitar_prestamo(self):
        with rx.session() as session:
            dpi_target = self.search_dpi if self.user_role == "1" else None

            if self.user_role != "1":
                user_obj = session.exec(
                    Usuario.select().where(
                        Usuario.username == self.logged_user
                    )
                ).first()

                cliente_obj = session.exec(
                    Cliente.select().where(
                        Cliente.id_usuario == user_obj.id_usuario
                    )
                ).first()
            else:
                cliente_obj = session.exec(
                    Cliente.select().where(
                        Cliente.dpi == dpi_target
                    )
                ).first()

            if not cliente_obj:
                return rx.window_alert("Cliente no encontrado")

            nuevo_p = Prestamo(
                id_cliente=cliente_obj.id_cliente,
                monto_aprobado=5000.00,
                saldo_pendiente=5000.00,
                tasa_interes=10.0,
                plazo_meses=12,
                estado="Activo",
            )

            session.add(nuevo_p)
            session.commit()

        # 🔥 REFRESCO
        if self.user_role == "1":
            self.buscar_cliente_por_dpi()
        else:
            self.cargar_datos_cliente()

        return rx.window_alert("¡Préstamo Aprobado por Q5,000.00!")

    # =========================
    # PAGO (ACTUALIZADO FINAL)
    # =========================
    def realizar_pago(self, id_prestamo: int):
        if not self.monto_pago:
            return rx.window_alert("Ingrese un monto válido")

        try:
            monto_a_pagar = float(self.monto_pago)
        except:
            return rx.window_alert("El monto debe ser un número.")

        if monto_a_pagar <= 0:
            return rx.window_alert("Monto inválido.")

        with rx.session() as session:
            prestamo = session.exec(
                Prestamo.select().where(Prestamo.id_prestamo == id_prestamo)
            ).first()

            if not prestamo:
                return rx.window_alert("Préstamo no encontrado.")

            cuentas = session.exec(
                Cuenta.select()
                .where(Cuenta.id_cliente == prestamo.id_cliente)
                .order_by(Cuenta.saldo.desc())
            ).all()

            saldo_total = sum(c.saldo for c in cuentas)

            if saldo_total < monto_a_pagar:
                return rx.window_alert("Fondos insuficientes en sus cuentas.")

            restante = monto_a_pagar
            for cuenta in cuentas:
                if restante <= 0:
                    break
                if cuenta.saldo >= restante:
                    cuenta.saldo -= restante
                    restante = 0
                else:
                    restante -= cuenta.saldo
                    cuenta.saldo = 0
                session.add(cuenta)

            prestamo.saldo_pendiente -= monto_a_pagar
            if prestamo.saldo_pendiente <= 0:
                prestamo.saldo_pendiente = 0
                prestamo.estado = "Pagado"
            session.add(prestamo)

            session.execute(text(
                f"INSERT INTO pagos (id_prestamo, monto) VALUES ({id_prestamo}, {monto_a_pagar})"
            ))

            session.commit()

        self.monto_pago = ""

        # 🔥 REFRESCO
        if self.user_role == "1":
            self.buscar_cliente_por_dpi()
        else:
            self.cargar_datos_cliente()

        return rx.window_alert(f"Pago de Q{monto_a_pagar} procesado exitosamente.")

    # =========================
    # BÚSQUEDA POR DPI (CORREGIDA)
    # =========================
    def buscar_cliente_por_dpi(self):
        # 🔥 CORRECCIÓN CLAVE
        if not self.search_dpi.strip():
            self.mis_cuentas = []
            self.mis_prestamos = []
            self.cliente_nombre_display = ""
            return rx.window_alert("Por favor ingrese un DPI válido.")

        with rx.session() as session:
            cliente = session.exec(
                Cliente.select().where(
                    Cliente.dpi == self.search_dpi
                )
            ).first()

            if cliente:
                self.cliente_nombre_display = f"{cliente.nombres} {cliente.apellidos}"

                self.mis_cuentas = session.exec(
                    Cuenta.select().where(
                        Cuenta.id_cliente == cliente.id_cliente
                    )
                ).all()

                self.mis_prestamos = session.exec(
                    Prestamo.select().where(
                        Prestamo.id_cliente == cliente.id_cliente
                    )
                ).all()

                return rx.window_alert(
                    f"Mostrando datos de: {cliente.nombres} {cliente.apellidos}"
                )
            else:
                self.mis_cuentas = []
                self.mis_prestamos = []
                self.cliente_nombre_display = ""
                return rx.window_alert("Cliente no encontrado.")