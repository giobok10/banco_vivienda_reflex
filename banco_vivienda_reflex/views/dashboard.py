import reflex as rx
from ..state import State

def dashboard_page() -> rx.Component:
    return rx.center(
        rx.cond(
            State.is_authenticated == "true",
            rx.vstack(
                rx.heading("SISTEMA BANCARIO CENTRAL", size="8", color_scheme="grass"),
                rx.badge(f"TERMINAL: {State.logged_user}", variant="outline"),
                
                rx.card(
                    rx.vstack(
                        rx.text("ACCESO NIVEL:"),
                        rx.heading(
                            rx.cond(
                                State.user_role == "1",
                                "ADMINISTRADOR",
                                "CLIENTE"
                            )
                        ),
                    ),
                    padding="2em",
                ),

                # =========================
                # BOTÓN SOLO PARA ADMIN
                # =========================
                rx.cond(
                    State.user_role == "1",
                    rx.button(
                        "GESTIONAR USUARIOS",
                        on_click=lambda: rx.redirect("/usuarios"),
                        color_scheme="blue"
                    ),
                ),

                rx.button(
                    "LOGOUT / DESCONECTAR",
                    on_click=State.logout,
                    color_scheme="red"
                ),

                spacing="5",
            ),
            rx.text("REDIRECCIONANDO AL LOGIN...") 
        ),
        on_mount=State.check_login,
        height="100vh",
    )