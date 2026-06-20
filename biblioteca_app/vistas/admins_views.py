"""
vistas/admins_views.py
-----------------------------
Blueprint de gestión de AdminUser. Solo accesible para quienes ya
tienen permiso 'configurar_sistema' (el más sensible del sistema).
"""

from flask import Blueprint, render_template, redirect, url_for, flash

from controladores.admins_controller import AdminsController
from formularios.admin_form import AdminForm
from utilitarios.decoradores import login_requerido, requiere_permiso

admins_bp = Blueprint("admins", __name__, url_prefix="/administradores")


@admins_bp.route("/")
@login_requerido
@requiere_permiso("configurar_sistema")
def listar():
    controlador = AdminsController()
    return render_template("admin/listar_admins.html", admins=controlador.listar())


@admins_bp.route("/nuevo", methods=["GET", "POST"])
@login_requerido
@requiere_permiso("configurar_sistema")
def crear():
    controlador = AdminsController()
    formulario = AdminForm()
    formulario.id_rol.choices = controlador.opciones_rol()

    if formulario.validate_on_submit():
        try:
            controlador.crear({
                "nombre": formulario.nombre.data,
                "email": formulario.email.data,
                "phone": formulario.phone.data,
                "admin_user": formulario.admin_user.data,
                "password": formulario.password.data,
                "id_rol": formulario.id_rol.data,
            })
            flash("Administrador creado correctamente.", "success")
            return redirect(url_for("admins.listar"))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template("admin/formulario_admin.html", formulario=formulario)


@admins_bp.route("/<int:id_admin>/eliminar", methods=["POST"])
@login_requerido
@requiere_permiso("configurar_sistema")
def eliminar(id_admin):
    controlador = AdminsController()
    if controlador.eliminar(id_admin):
        flash("Administrador eliminado correctamente.", "success")
    else:
        flash("No se pudo eliminar el administrador.", "danger")
    return redirect(url_for("admins.listar"))
