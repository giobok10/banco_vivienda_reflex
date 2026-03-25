import reflex as rx
from ..state import State

def login_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("BANCO DE VIVIENDA", size="9", color_scheme="grass"),
            rx.text("SISTEMA CENTRAL DE AUTENTICACIÓN", opacity=0.8),
            rx.input(placeholder="Usuario", on_change=State.set_user_input, width="100%"),
            rx.input(placeholder="Password", type="password", on_change=State.set_pass_input, width="100%"),
            rx.button("ACCEDER", on_click=State.login_handler, width="100%", color_scheme="grass"),
            rx.cond(State.error_msg != "", rx.text(State.error_msg, color="red")),
            spacing="4", padding="2em", border="1px solid #333", border_radius="15px",
        ),
        height="100vh",
        background="radial-gradient(circle, #1a2a1a 0%, #050505 100%)",
    )