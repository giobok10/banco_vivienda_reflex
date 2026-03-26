import reflex as rx
import os
from dotenv import load_dotenv
from reflex.plugins.sitemap import SitemapPlugin

load_dotenv()

config = rx.Config(
    app_name="banco_vivienda_reflex",
    db_url=os.getenv("DATABASE_URL"),
    disable_plugins=[SitemapPlugin],
)