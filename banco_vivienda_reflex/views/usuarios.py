import reflex as rx
from ..state import State
from ..models import Usuario

def usuarios_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("GESTIÓN DE USUARIOS", size="8", color_scheme="grass"),
            rx.text("Panel de administración de accesos", opacity=0.8),

            # --- FORMULARIO DE REGISTRO ---
            rx.card(
                rx.vstack(
                    rx.heading("Registrar Nuevo Usuario", size="4"),
                    rx.input(placeholder="Username", on_change=State.set_user_input, width="100%"),
                    rx.input(placeholder="Password", type="password", on_change=State.set_pass_input, width="100%"),
                    rx.select(
                        ["1", "2"], 
                        placeholder="Seleccionar Rol (1: Admin, 2: Cliente)",
                        on_change=State.set_user_role_input, # Crearemos este setter
                        width="100%"
                    ),
                    rx.button("GUARDAR EN NEON", on_click=State.crear_usuario, color_scheme="grass", width="100%"),
                ),
                width="100%",
                padding="1.5em",
            ),

            rx.divider(),

            # --- TABLA DE USUARIOS ---
            rx.button("RECARGAR LISTA", on_click=State.obtener_todos_usuarios, variant="soft"),
            
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("ID"),
                        rx.table.column_header_cell("Usuario"),
                        rx.table.column_header_cell("Rol"),
                    )
                ),
                rx.table.body(
                    rx.foreach(State.lista_usuarios, lambda u: rx.table.row(
                        rx.table.cell(u.id_usuario.to(str)),
                        rx.table.cell(u.username),
                        rx.table.cell(u.id_rol.to(str)),
                    ))
                ),
                width="100%",
            ),
            
            rx.button("VOLVER AL DASHBOARD", on_click=lambda: rx.redirect("/dashboard"), variant="ghost"),
            spacing="5",
            width="80%",
        ),
        on_mount=State.obtener_todos_usuarios,
        padding="2em",
    )