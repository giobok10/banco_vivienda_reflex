import reflex as rx
from ..state import State
from ..models import Cuenta, Prestamo, Usuario

def render_cuenta(cuenta: Cuenta):
    return rx.table.row(
        rx.table.cell(cuenta.numero_cuenta),
        rx.table.cell(cuenta.tipo_cuenta),
        rx.table.cell(f"Q{cuenta.saldo:,.2f}", color="green"),
    )

def render_usuario(user: Usuario):
    return rx.table.row(
        rx.table.cell(user.id_usuario),
        rx.table.cell(user.username),
        rx.table.cell(rx.cond(user.id_rol == 1, "Admin", "Cliente")),
    )

def render_prestamo(prestamo: Prestamo):
    return rx.table.row(
        rx.table.cell(f"ID-{prestamo.id_prestamo}"),
        rx.table.cell(f"Q{prestamo.monto_aprobado:,.2f}"),
        rx.table.cell(f"Q{prestamo.saldo_pendiente:,.2f}", color="red"),
        rx.table.cell(f"{prestamo.tasa_interes}%"),
        rx.table.cell(prestamo.estado),
        rx.table.cell(
            rx.cond(
                State.user_role != "1",
                rx.popover.root(
                    rx.popover.trigger(rx.button("Abonar", size="1", color_scheme="blue")),
                    rx.popover.content(
                        rx.vstack(
                            rx.input(placeholder="Monto", on_change=State.set_monto_pago, type="number"),
                            rx.button("Confirmar", on_click=lambda: State.realizar_pago(prestamo.id_prestamo)),
                        )
                    ),
                ),
                rx.badge("Solo Lectura", color_scheme="gray"),
            )
        ),
    )

def dashboard_page() -> rx.Component:
    return rx.center(
        rx.cond(
            State.is_authenticated == "true",
            rx.vstack(
                rx.heading("SISTEMA BANCARIO CENTRAL", size="8", margin_bottom="1em"),
                rx.badge(f"SESIÓN: {State.logged_user}", color_scheme="gold", size="3"),

                # SECCIÓN ADMIN (ROL 1)
                rx.cond(
                    State.user_role == "1",
                    rx.vstack(
                        rx.tabs.root(
                            rx.tabs.list(
                                rx.tabs.trigger("Clientes", value="tab1"),
                                rx.tabs.trigger("Usuarios", value="tab2"),
                            ),
                            rx.tabs.content(
                                rx.vstack(
                                    rx.hstack(
                                        rx.input(placeholder="DPI Cliente", on_change=State.set_search_dpi),
                                        # 🔥 LIMPIEZA ANTES DE BUSCAR
                                        rx.button(
                                            "Buscar",
                                            on_click=[
                                                State.set_mis_cuentas([]),
                                                State.set_mis_prestamos([]),
                                                State.buscar_cliente_por_dpi,
                                            ],
                                        ),
                                    ),
                                    rx.hstack(
                                        rx.button("Aperturar Cuenta", on_click=State.abrir_nueva_cuenta, color_scheme="green"),
                                        rx.button("Asignar Préstamo", on_click=State.solicitar_prestamo, color_scheme="blue"),
                                    ),
                                    rx.table.root(rx.table.body(rx.foreach(State.mis_cuentas, render_cuenta)), width="100%"),
                                    rx.table.root(rx.table.body(rx.foreach(State.mis_prestamos, render_prestamo)), width="100%"),
                                    width="100%",
                                ),
                                value="tab1",
                            ),
                            rx.tabs.content(
                                rx.vstack(
                                    rx.hstack(
                                        # 🔥 INPUT DPI (YA EXISTENTE)
                                        rx.input(placeholder="DPI", on_change=State.set_user_dpi_input),
                                        rx.input(placeholder="User", on_change=State.set_user_input),
                                        rx.input(placeholder="Pass", type="password", on_change=State.set_pass_input),
                                        rx.select(["1", "2"], placeholder="Rol", on_change=State.set_user_role_input),
                                        rx.button("Crear", on_click=State.crear_usuario, color_scheme="orange"),
                                    ),
                                    rx.button("Refrescar", on_click=State.obtener_todos_usuarios, size="1"),
                                    rx.table.root(rx.table.body(rx.foreach(State.lista_usuarios, render_usuario)), width="100%"),
                                    width="100%",
                                ),
                                value="tab2",
                            ),
                            width="100%",
                        ),
                        width="100%",
                    ),
                ),

                # SECCIÓN CLIENTE (ROL != 1)
                rx.cond(
                    State.user_role != "1",
                    rx.vstack(
                        rx.hstack(
                            rx.button("Nueva Cuenta", on_click=State.abrir_nueva_cuenta, color_scheme="green"),
                            rx.button("Solicitar Préstamo", on_click=State.solicitar_prestamo, color_scheme="blue"),
                        ),
                        rx.table.root(rx.table.body(rx.foreach(State.mis_cuentas, render_cuenta)), width="100%"),
                        rx.table.root(rx.table.body(rx.foreach(State.mis_prestamos, render_prestamo)), width="100%"),
                        width="100%",
                    ),
                ),

                rx.button("Cerrar Sesión", on_click=State.logout, color_scheme="red", variant="soft", margin_top="2em"),
                padding="2em",
                border="1px solid #eaeaea",
                border_radius="15px",
                width="100%",
            ),
            rx.button("Ir al Login", on_click=lambda: rx.redirect("/")),
        ),
        on_mount=[State.check_login, State.cargar_datos_cliente],
        padding_top="5em",
    )