"""
vistas/empleado_views.py
------------------------------
Blueprint del panel de Empleado.
"""

from flask import Blueprint, render_template

from utilitarios.decoradores import login_requerido, requiere_tipo

empleado_bp = Blueprint("empleado", __name__, url_prefix="/empleado")


@empleado_bp.route("/dashboard")
@login_requerido
@requiere_tipo("empleado")
def dashboard():
    return render_template("empleado/dashboard.html")
