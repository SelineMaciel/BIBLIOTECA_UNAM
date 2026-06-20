"""
vistas/prestamos_views.py
--------------------------------
Blueprint de gestión de préstamos: listar, registrar nuevo préstamo,
registrar devolución. Accesible para admin y empleado.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, session, request

from controladores.prestamos_controller import PrestamosController
from formularios.prestamo_form import PrestamoForm
from utilitarios.decoradores import login_requerido, requiere_permiso

prestamos_bp = Blueprint("prestamos", __name__, url_prefix="/prestamos")


@prestamos_bp.route("/")
@login_requerido
@requiere_permiso("registrar_prestamo")
def listar():
    controlador = PrestamosController()
    return render_template("prestamos/listar.html", prestamos=controlador.listar())


@prestamos_bp.route("/nuevo", methods=["GET", "POST"])
@login_requerido
@requiere_permiso("registrar_prestamo")
def crear():
    controlador = PrestamosController()
    formulario = PrestamoForm()
    formulario.id_usuario.choices = controlador.opciones_usuario()
    formulario.isbn.choices = controlador.opciones_libro_disponible()
    formulario.id_sucursal.choices = controlador.opciones_sucursal()

    if formulario.validate_on_submit():
        id_empleado = session["id_sesion"] if session.get("tipo_sesion") == "empleado" else None
        resultado = controlador.registrar_prestamo(
            formulario.id_usuario.data, formulario.isbn.data, formulario.id_sucursal.data, id_empleado
        )
        flash(resultado["mensaje"], "success" if resultado["exito"] else "danger")
        if resultado["exito"]:
            return redirect(url_for("prestamos.listar"))

    return render_template("prestamos/formulario.html", formulario=formulario)


@prestamos_bp.route("/<int:id_prestamo>/multas")
@login_requerido
@requiere_permiso("registrar_devolucion")
def multas_prestamo(id_prestamo):
    """Lista las multas de un préstamo y permite marcarlas como pagadas."""
    from persistencia.repositorio_prestamos import RepositorioMultas
    controlador = PrestamosController()
    prestamo = controlador.obtener(id_prestamo)
    if prestamo is None:
        flash("El préstamo no existe.", "warning")
        return redirect(url_for("prestamos.listar"))
    multas = RepositorioMultas().obtener_por_prestamo(id_prestamo)
    return render_template("prestamos/multas.html", prestamo=prestamo, multas=multas)


@prestamos_bp.route("/multas/<int:id_multa>/pagar", methods=["POST"])
@login_requerido
@requiere_permiso("registrar_devolucion")
def pagar_multa(id_multa):
    from servicios.servicio_multas import ServicioMultas
    id_prestamo = request.form.get("id_prestamo", type=int)
    if ServicioMultas().pagar_multa(id_multa):
        flash("Multa marcada como pagada.", "success")
    else:
        flash("No se pudo procesar el pago.", "danger")
    return redirect(url_for("prestamos.multas_prestamo", id_prestamo=id_prestamo))
@prestamos_bp.route("/<int:id_prestamo>/devolver", methods=["POST"])
@login_requerido
@requiere_permiso("registrar_devolucion")
def devolver(id_prestamo):
    controlador = PrestamosController()
    resultado = controlador.registrar_devolucion(id_prestamo)
    flash(resultado["mensaje"], "success" if resultado["exito"] else "danger")
    return redirect(url_for("prestamos.listar"))
