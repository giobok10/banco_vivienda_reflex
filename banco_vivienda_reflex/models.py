import reflex as rx
from typing import Optional
from sqlmodel import Field

class Usuario(rx.Model, table=True):
    __tablename__ = "usuarios"
    id_usuario: Optional[int] = Field(default=None, primary_key=True)
    username: str
    password_hash: str
    id_rol: int