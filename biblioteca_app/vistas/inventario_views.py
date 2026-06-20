"""
vistas/inventario_views.py
---------------------------------
Blueprint de gestión de Inventario (stock de libros por sucursal).
Restringido al permiso 'gestionar_libros', ya que el inventario es
una extensión natural de la gestión del catálogo.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

from controladores.inventario_controller import InventarioController, InventarioDuplicadoError
from formularios.inventario_form import InventarioForm
from utilitarios.decoradores import login_requerido, requiere_permiso

inventario_bp = Blueprint("inventario", __name__, url_prefix="/inventario")


@inventario_bp.route("/")
@login_requerido
@requiere_permiso("gestionar_libros")
def listar():
    controlador = InventarioController()
    return render_template("inventario/listar.html", items=controlador.listar())


@inventario_bp.route("/nuevo", methods=["GET", "POST"])
@login_requerido
@requiere_permiso("gestionar_libros")
def crear():
    controlador = InventarioController()
    formulario = InventarioForm()
    formulario.isbn.choices = controlador.opciones_libro()
    formulario.id_sucursal.choices = controlador.opciones_sucursal()

    if formulario.validate_on_submit():
        try:
            controlador.crear({
                "isbn": formulario.isbn.data,
                "id_sucursal": formulario.id_sucursal.data,
                "cantidad_total": formulario.cantidad_total.data,
                "cantidad_disponible": formulario.cantidad_disponible.data,
            })
            flash("Inventario registrado correctamente.", "success")
            return redirect(url_for("inventario.listar"))
        except InventarioDuplicadoError as e:
            flash(str(e), "danger")

    return render_template("inventario/formulario.html", formulario=formulario, accion="Crear")


@inventario_bp.route("/<int:id_inventario>/editar", methods=["GET", "POST"])
@login_requerido
@requiere_permiso("gestionar_libros")
def editar(id_inventario):
    controlador = InventarioController()
    item = controlador.obtener(id_inventario)
    if item is None:
        flash("El registro de inventario no existe.", "warning")
        return redirect(url_for("inventario.listar"))

    formulario = InventarioForm()
    formulario.isbn.choices = controlador.opciones_libro()
    formulario.id_sucursal.choices = controlador.opciones_sucursal()

    if request.method == "GET":
        formulario.isbn.data = item.libro.isbn
        formulario.id_sucursal.data = item.sucursal.id_sucursal
        formulario.cantidad_total.data = item.cantidad_total
        formulario.cantidad_disponible.data = item.cantidad_disponible

    if formulario.validate_on_submit():
        controlador.actualizar(id_inventario, {
            "isbn": formulario.isbn.data,
            "id_sucursal": formulario.id_sucursal.data,
            "cantidad_total": formulario.cantidad_total.data,
            "cantidad_disponible": formulario.cantidad_disponible.data,
        })
        flash("Inventario actualizado correctamente.", "success")
        return redirect(url_for("inventario.listar"))

    return render_template("inventario/formulario.html", formulario=formulario, accion="Editar")


@inventario_bp.route("/<int:id_inventario>/eliminar", methods=["POST"])
@login_requerido
@requiere_permiso("gestionar_libros")
def eliminar(id_inventario):
    controlador = InventarioController()
    if controlador.eliminar(id_inventario):
        flash("Registro de inventario eliminado correctamente.", "success")
    else:
        flash("No se pudo eliminar el registro de inventario.", "danger")
    return redirect(url_for("inventario.listar"))
