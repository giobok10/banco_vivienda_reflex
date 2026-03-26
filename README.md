# Banco Vivienda Reflex

Aplicacion web bancaria desarrollada con Reflex + PostgreSQL (Neon) para gestionar clientes, cuentas, prestamos y pagos, con control de acceso por roles.

## Objetivo del proyecto

Este proyecto implementa la fase 1 del sistema solicitado para Banco de Vivienda, incluyendo:

- Autenticacion de usuarios.
- Gestion de clientes y productos financieros.
- Registro y consulta de pagos.
- Reglas de negocio por rol.
- Integracion con base de datos en la nube (Neon/PostgreSQL).

## Stack tecnologico

- `Python 3.12+`
- `Reflex`
- `SQLModel / SQLAlchemy`
- `PostgreSQL (Neon)`
- `uv` para entorno y ejecucion

## Roles y capacidades

- `Admin`
  - Crear usuarios.
  - Buscar clientes por DPI.
  - Aperturar cuentas y asignar prestamos a clientes.
- `Colaborador`
  - Buscar clientes por DPI.
  - Aperturar cuentas y asignar prestamos a clientes.
- `Cliente`
  - Consultar sus cuentas, prestamos y pagos.
  - Solicitar cuenta/prestamo.
  - Realizar pagos de sus propios prestamos.

## Reglas de negocio y seguridad (resumen)

- Validaciones de entrada para usuario, password, DPI y montos.
- Control de permisos por rol aplicado en backend (no solo UI).
- Hash de contrasenas para autenticacion.
- Bloqueo de operaciones no permitidas (ej. cliente no puede pagar prestamos de otro cliente).
- Bitacora de acciones de sesion.

## Estructura principal

- `banco_vivienda_reflex/models.py`: modelos de datos.
- `banco_vivienda_reflex/state.py`: estado y orquestacion de flujos.
- `banco_vivienda_reflex/services.py`: logica de negocio.
- `banco_vivienda_reflex/security.py`: utilidades de seguridad.
- `banco_vivienda_reflex/views/`: vistas de login, dashboard y usuarios.
- `alembic/versions/`: migraciones.
- `backup_db.sh`: script de respaldo de base de datos.

## Configuracion local

1. Crear archivo `.env` con `DATABASE_URL` de Neon.
2. Instalar dependencias:

```bash
uv sync
```

3. Ejecutar migraciones:

```bash
uv run reflex db migrate
```

4. Levantar aplicacion:

```bash
uv run reflex run
```

## Notas para evaluacion academica

- La base de datos esta modelada para 3FN con entidades principales:
  `roles`, `usuarios`, `clientes`, `cuentas`, `prestamos`, `pagos`.
- Se incluyen tablas de apoyo:
  `telefonos`, `direcciones`, `bitacora`.
- El entregable formal (manual tecnico y manual de usuario) se documenta por separado en PDF.

## Estado del repositorio

Proyecto funcional en rama `main` y preparado para despliegue y documentacion final.
