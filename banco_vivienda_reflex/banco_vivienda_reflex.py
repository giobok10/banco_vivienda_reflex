import reflex as rx
from .views.login import login_page
from .views.dashboard import dashboard_page
from .views.usuarios import usuarios_page

app = rx.App(
    theme=rx.theme(
        appearance="dark", 
        accent_color="grass", 
        panel_background="translucent"
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap",
    ],
)

app.add_page(login_page, route="/", title="Banco Vivienda | Login")
app.add_page(dashboard_page, route="/dashboard", title="Banco Vivienda | Sistema")
app.add_page(usuarios_page, route="/usuarios")