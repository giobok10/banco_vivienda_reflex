import reflex as rx
from .models import Usuario

class State(rx.State):
    user_input: str = ""
    pass_input: str = ""
    error_msg: str = ""

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
    # LOGIN
    # =========================
    def login_handler(self):
        with rx.session() as session:
            user = session.exec(
                Usuario.select().where(
                    (Usuario.username == self.user_input) & 
                    (Usuario.password_hash == self.pass_input)
                )
            ).first()

            if user:
                # Seteamos todo como strings para LocalStorage
                self.logged_user = str(user.username)
                self.user_role = str(user.id_rol)
                self.is_authenticated = "true"
                self.error_msg = ""
                return rx.redirect("/dashboard")
            else:
                self.is_authenticated = "false"
                self.error_msg = "USUARIO O CLAVE INCORRECTOS"

    def check_login(self):
        """Si no es exactamente la cadena 'true', para afuera."""
        if self.is_authenticated != "true":
            return rx.redirect("/")

    def logout(self):
        """Limpieza profunda de la sesión"""
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
        if not self.user_input or not self.pass_input:
            return rx.window_alert("Llene todos los campos")
        
        with rx.session() as session:
            nuevo = Usuario(
                username=self.user_input,
                password_hash=self.pass_input,
                id_rol=int(self.user_role_input)
            )
            session.add(nuevo)
            session.commit()

        # Refrescar tabla después de crear
        self.obtener_todos_usuarios()

        return rx.window_alert(f"Usuario {self.user_input} creado!")