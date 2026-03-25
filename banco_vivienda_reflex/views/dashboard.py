import reflex as rx
from ..state import State
from ..models import Cuenta, Prestamo

def render_cuenta(cuenta: Cuenta):
    return rx.table.row(
        rx.table.cell(cuenta.numero_cuenta),
        rx.table.cell(cuenta.tipo_cuenta),
        rx.table.cell(f"Q{cuenta.saldo:,.2f}", color="green"),
    )

def render_prestamo(prestamo: Prestamo):
    return rx.table.row(
        rx.table.cell(f"ID-{prestamo.id_prestamo}"),
        rx.table.cell(f"Q{prestamo.monto_aprobado:,.2f}"),
        rx.table.cell(f"Q{prestamo.saldo_pendiente:,.2f}", color="red"),
        rx.table.cell(f"{prestamo.tasa_interes}%"),
        rx.table.cell(prestamo.estado),
        # BOTÓN DE PAGO CON POPOVER
        rx.table.cell(
            rx.popover.root(
                rx.popover.trigger(
                    rx.button("Abonar", size="1", color_scheme="blue", variant="soft")
                ),
                rx.popover.content(
                    rx.vstack(
                        rx.text("Monto a pagar:", size="2", weight="bold"),
                        rx.input(
                            placeholder="Ej: 500.00", 
                            on_change=State.set_monto_pago,
                            type="number"
                        ),
                        rx.popover.close(
                            rx.button(
                                "Confirmar", 
                                on_click=lambda: State.realizar_pago(prestamo.id_prestamo),
                                width="100%"
                            )
                        ),
                        spacing="2",
                    ),
                ),
            )
        ),
    )

def dashboard_page() -> rx.Component:
    return rx.center(
        rx.cond(
            State.is_authenticated == "true",
            rx.vstack(
                rx.heading("SISTEMA BANCARIO CENTRAL", size="8", color_scheme="grass"),
                rx.badge(f"USUARIO: {State.logged_user}", variant="soft", color_scheme="grass"),
                
                # --- VISTA PARA CLIENTES ---
                rx.cond(
                    State.user_role != "1",
                    rx.vstack(
                        rx.heading("Mis Productos Financieros", size="5"),
                        rx.tabs.root(
                            rx.tabs.list(
                                rx.tabs.trigger("Cuentas", value="tab1"),
                                rx.tabs.trigger("Préstamos", value="tab2"),
                            ),
                            rx.tabs.content(
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("No. Cuenta"),
                                            rx.table.column_header_cell("Tipo"),
                                            rx.table.column_header_cell("Saldo"),
                                        )
                                    ),
                                    rx.table.body(rx.foreach(State.mis_cuentas, render_cuenta)),
                                ),
                                value="tab1",
                            ),
                            rx.tabs.content(
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("ID"),
                                            rx.table.column_header_cell("Monto Aprobado"),
                                            rx.table.column_header_cell("Saldo Pendiente"),
                                            rx.table.column_header_cell("Tasa"),
                                            rx.table.column_header_cell("Estado"),
                                            rx.table.column_header_cell("Acciones"), # <--- ESTA ES LA COLUMNA EXTRA
                                        )
                                    ),
                                    rx.table.body(rx.foreach(State.mis_prestamos, render_prestamo)),
                                ),
                                value="tab2",
                            ),
                            width="100%",
                        ),
                        spacing="4",
                        width="100%",
                    )
                ),

                # --- VISTA PARA ADMINS (Opcional por ahora) ---
                rx.cond(
                    State.user_role == "1",
                    rx.card(
                        rx.vstack(
                            rx.text("Panel de Administración"),
                            rx.button("GESTIONAR USUARIOS", on_click=lambda: rx.redirect("/usuarios")),
                        )
                    )
                ),

                rx.button("CERRAR SESIÓN", on_click=State.logout, color_scheme="red", variant="surface"),
                spacing="6",
                padding="2em",
                width="90%",
            ),
            rx.text("Cargando sesión...")
        ),
        on_mount=[State.check_login, State.cargar_datos_cliente],
        height="100vh",
    )