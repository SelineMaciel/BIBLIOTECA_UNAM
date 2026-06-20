"""
vistas/empleados_views.py
--------------------------------
Blueprint de gestión de Empleado. Restringido a admin
(permiso 'gestionar_empleados').
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

from controladores.empleados_controller import EmpleadosController
from formularios.empleado_form import EmpleadoForm
from utilitarios.decoradores import login_requerido, requiere_permiso

empleados_bp = Blueprint("empleados", __name__, url_prefix="/empleados")


@empleados_bp.route("/")
@login_requerido
@requiere_permiso("gestionar_empleados")
def listar():
    controlador = EmpleadosController()
    return render_template("empleados/listar.html", empleados=controlador.listar())


@empleados_bp.route("/nuevo", methods=["GET", "POST"])
@login_requerido
@requiere_permiso("gestionar_empleados")
def crear():
    controlador = EmpleadosController()
    formulario = EmpleadoForm()
    formulario.id_sucursal.choices = controlador.opciones_sucursal()

    if formulario.validate_on_submit():
        try:
            controlador.crear({
                "nombre": formulario.nombre.data,
                "email": formulario.email.data,
                "phone": formulario.phone.data,
                "cargo": formulario.cargo.data,
                "id_sucursal": formulario.id_sucursal.data,
            })
            flash("Empleado creado correctamente.", "success")
            return redirect(url_for("empleados.listar"))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template("empleados/formulario.html", formulario=formulario, accion="Crear")


@empleados_bp.route("/<int:id_empleado>/editar", methods=["GET", "POST"])
@login_requerido
@requiere_permiso("gestionar_empleados")
def editar(id_empleado):
    controlador = EmpleadosController()
    empleado = controlador.obtener(id_empleado)
    if empleado is None:
        flash("El empleado no existe.", "warning")
        return redirect(url_for("empleados.listar"))

    formulario = EmpleadoForm()
    formulario.id_sucursal.choices = controlador.opciones_sucursal()

    if request.method == "GET":
        formulario.nombre.data = empleado.nombre
        formulario.email.data = empleado.email
        formulario.phone.data = empleado.phone
        formulario.cargo.data = empleado.cargo
        formulario.id_sucursal.data = empleado.sucursal.id_sucursal

    if formulario.validate_on_submit():
        controlador.actualizar(id_empleado, {
            "nombre": formulario.nombre.data,
            "email": formulario.email.data,
            "phone": formulario.phone.data,
            "cargo": formulario.cargo.data,
            "id_sucursal": formulario.id_sucursal.data,
        })
        flash("Empleado actualizado correctamente.", "success")
        return redirect(url_for("empleados.listar"))

    return render_template("empleados/formulario.html", formulario=formulario, accion="Editar")


@empleados_bp.route("/<int:id_empleado>/eliminar", methods=["POST"])
@login_requerido
@requiere_permiso("gestionar_empleados")
def eliminar(id_empleado):
    controlador = EmpleadosController()
    if controlador.eliminar(id_empleado):
        flash("Empleado eliminado correctamente.", "success")
    else:
        flash("No se pudo eliminar el empleado.", "danger")
    return redirect(url_for("empleados.listar"))
