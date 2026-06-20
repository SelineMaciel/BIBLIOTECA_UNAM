"""
vistas/usuarios_views.py
-------------------------------
Blueprint de gestión de Usuario (lectores). Restringido a admin
(permiso 'gestionar_usuarios').
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

from controladores.usuarios_controller import UsuariosController, EmailDuplicadoError
from formularios.usuario_form import UsuarioForm
from formularios.busqueda_form import BusquedaUsuarioForm
from utilitarios.decoradores import login_requerido, requiere_permiso

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@usuarios_bp.route("/")
@login_requerido
@requiere_permiso("gestionar_usuarios")
def listar():
    controlador = UsuariosController()
    formulario_busqueda = BusquedaUsuarioForm()
    texto = request.args.get("texto", "").strip() or None
    if texto:
        formulario_busqueda.texto.data = texto
    usuarios = controlador.listar(texto_busqueda=texto)
    return render_template("usuarios/listar.html", usuarios=usuarios, formulario_busqueda=formulario_busqueda)


@usuarios_bp.route("/nuevo", methods=["GET", "POST"])
@login_requerido
@requiere_permiso("gestionar_usuarios")
def crear():
    controlador = UsuariosController()
    formulario = UsuarioForm()
    formulario.id_membresia.choices = controlador.opciones_membresia()
    formulario.id_rol.choices = controlador.opciones_rol()

    if formulario.validate_on_submit():
        try:
            controlador.crear({
                "nombre": formulario.nombre.data,
                "email": formulario.email.data,
                "phone": formulario.phone.data,
                "edad": formulario.edad.data,
                "id_membresia": formulario.id_membresia.data,
                "id_rol": formulario.id_rol.data,
            })
            flash("Usuario creado correctamente.", "success")
            return redirect(url_for("usuarios.listar"))
        except EmailDuplicadoError as e:
            flash(str(e), "danger")

    return render_template("usuarios/formulario.html", formulario=formulario, accion="Crear")


@usuarios_bp.route("/<int:id_usuario>/editar", methods=["GET", "POST"])
@login_requerido
@requiere_permiso("gestionar_usuarios")
def editar(id_usuario):
    controlador = UsuariosController()
    usuario = controlador.obtener(id_usuario)
    if usuario is None:
        flash("El usuario no existe.", "warning")
        return redirect(url_for("usuarios.listar"))

    formulario = UsuarioForm()
    formulario.id_membresia.choices = controlador.opciones_membresia()
    formulario.id_rol.choices = controlador.opciones_rol()

    if request.method == "GET":
        formulario.nombre.data = usuario.nombre
        formulario.email.data = usuario.email
        formulario.phone.data = usuario.phone
        formulario.edad.data = usuario.edad
        formulario.id_membresia.data = usuario.membresia.id_membresia
        formulario.id_rol.data = usuario.rol.id_rol

    if formulario.validate_on_submit():
        try:
            controlador.actualizar(id_usuario, {
                "nombre": formulario.nombre.data,
                "email": formulario.email.data,
                "phone": formulario.phone.data,
                "edad": formulario.edad.data,
                "id_membresia": formulario.id_membresia.data,
                "id_rol": formulario.id_rol.data,
            })
            flash("Usuario actualizado correctamente.", "success")
            return redirect(url_for("usuarios.listar"))
        except EmailDuplicadoError as e:
            flash(str(e), "danger")

    return render_template("usuarios/formulario.html", formulario=formulario, accion="Editar")


@usuarios_bp.route("/<int:id_usuario>/eliminar", methods=["POST"])
@login_requerido
@requiere_permiso("gestionar_usuarios")
def eliminar(id_usuario):
    controlador = UsuariosController()
    if controlador.eliminar(id_usuario):
        flash("Usuario eliminado correctamente.", "success")
    else:
        flash("No se pudo eliminar el usuario (puede tener préstamos o reservas asociadas).", "danger")
    return redirect(url_for("usuarios.listar"))
