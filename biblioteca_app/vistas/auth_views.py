"""
vistas/auth_views.py
-------------------------
Blueprint de autenticación: página de inicio, login y logout.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, session

from formularios.login_form import LoginForm
from controladores.auth_controller import AuthController
from utilitarios.sesion import cerrar_sesion

auth_bp = Blueprint("auth", __name__, url_prefix="")


@auth_bp.route("/")
def index():
    if session.get("tipo_sesion") == "admin":
        return redirect(url_for("admin.dashboard"))
    elif session.get("tipo_sesion") == "empleado":
        return redirect(url_for("empleado.dashboard"))
    elif session.get("tipo_sesion") == "usuario":
        return redirect(url_for("usuario.dashboard"))
    return render_template("auth/inicio.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    formulario = LoginForm()
    if formulario.validate_on_submit():
        controlador = AuthController()
        resultado = controlador.procesar_login(formulario.email.data, formulario.password.data)
        if resultado["exito"]:
            flash(resultado["mensaje"], "success")
            return redirect(url_for(resultado["panel"]))
        else:
            flash(resultado["mensaje"], "danger")
    return render_template("auth/login.html", formulario=formulario)


@auth_bp.route("/logout")
def logout():
    cerrar_sesion()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.index"))
