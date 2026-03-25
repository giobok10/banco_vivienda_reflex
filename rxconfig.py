import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

config = rx.Config(
    app_name="banco_vivienda_reflex",
    db_url=os.getenv("DATABASE_URL"),
)