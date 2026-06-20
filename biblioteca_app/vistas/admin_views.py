"""
vistas/admin_views.py
---------------------------
Blueprint del panel de Administrador. La protección de ruta usa
@requiere_tipo("admin"), que internamente solo verifica el tipo de
sesión; los permisos finos (qué puede hacer dentro del panel) se
verifican con @requiere_permiso en cada acción concreta de los demás
blueprints (usuarios, libros, etc.).
"""

from flask import Blueprint, render_template

from utilitarios.decoradores import login_requerido, requiere_tipo

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_requerido
@requiere_tipo("admin")
def dashboard():
    return render_template("admin/dashboard.html")
