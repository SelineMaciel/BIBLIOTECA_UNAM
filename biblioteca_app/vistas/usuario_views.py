"""
vistas/usuario_views.py
------------------------------
Blueprint del panel de Usuario (lector). Muestra su historial de
préstamos, reservas vigentes y detalle de multas pendientes.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, session

from utilitarios.decoradores import login_requerido, requiere_tipo
from persistencia.repositorio_prestamos import RepositorioPrestamos
from servicios.servicio_reservas import ServicioReservas
from servicios.servicio_multas import ServicioMultas

usuario_bp = Blueprint("usuario", __name__, url_prefix="/usuario")


@usuario_bp.route("/dashboard")
@login_requerido
@requiere_tipo("usuario")
def dashboard():
    id_usuario = session["id_sesion"]
    prestamos_activos = RepositorioPrestamos().obtener_activos_por_usuario(id_usuario)
    reservas_vigentes = ServicioReservas().reservas_vigentes_de_usuario(id_usuario)
    total_multas = ServicioMultas().total_pendiente_por_usuario(id_usuario)
    return render_template(
        "usuario/dashboard.html",
        prestamos_activos=prestamos_activos,
        reservas_vigentes=reservas_vigentes,
        total_multas=total_multas,
    )


@usuario_bp.route("/multas")
@login_requerido
@requiere_tipo("usuario")
def mis_multas():
    """Vista detallada de multas pendientes del usuario logueado."""
    id_usuario = session["id_sesion"]
    servicio = ServicioMultas()
    multas = servicio.multas_pendientes_por_usuario(id_usuario)
    total = servicio.total_pendiente_por_usuario(id_usuario)
    return render_template("usuario/multas.html", multas=multas, total=total)
