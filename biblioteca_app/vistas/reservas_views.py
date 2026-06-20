"""
vistas/reservas_views.py
-------------------------------
Blueprint de gestión de reservas: listar, crear, confirmar, cancelar.
"""

from flask import Blueprint, render_template, redirect, url_for, flash

from controladores.reservas_controller import ReservasController
from formularios.prestamo_form import ReservaForm
from utilitarios.decoradores import login_requerido, requiere_permiso

reservas_bp = Blueprint("reservas", __name__, url_prefix="/reservas")


@reservas_bp.route("/")
@login_requerido
@requiere_permiso("hacer_reserva")
def listar():
    controlador = ReservasController()
    return render_template("reservas/listar.html", reservas=controlador.listar())


@reservas_bp.route("/nueva", methods=["GET", "POST"])
@login_requerido
@requiere_permiso("hacer_reserva")
def crear():
    controlador = ReservasController()
    formulario = ReservaForm()
    formulario.id_usuario.choices = controlador.opciones_usuario()
    formulario.isbn.choices = controlador.opciones_libro()
    formulario.id_sucursal.choices = controlador.opciones_sucursal()

    if formulario.validate_on_submit():
        resultado = controlador.crear_reserva(
            formulario.id_usuario.data, formulario.isbn.data, formulario.id_sucursal.data
        )
        flash(resultado["mensaje"], "success" if resultado["exito"] else "danger")
        if resultado["exito"]:
            return redirect(url_for("reservas.listar"))

    return render_template("reservas/formulario.html", formulario=formulario)


@reservas_bp.route("/<int:id_reserva>/confirmar", methods=["POST"])
@login_requerido
@requiere_permiso("hacer_reserva")
def confirmar(id_reserva):
    controlador = ReservasController()
    if controlador.confirmar(id_reserva):
        flash("Reserva confirmada.", "success")
    else:
        flash("No se pudo confirmar la reserva.", "danger")
    return redirect(url_for("reservas.listar"))


@reservas_bp.route("/<int:id_reserva>/cancelar", methods=["POST"])
@login_requerido
@requiere_permiso("hacer_reserva")
def cancelar(id_reserva):
    controlador = ReservasController()
    if controlador.cancelar(id_reserva):
        flash("Reserva cancelada.", "info")
    else:
        flash("No se pudo cancelar la reserva.", "danger")
    return redirect(url_for("reservas.listar"))
