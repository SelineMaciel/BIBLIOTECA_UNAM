"""
vistas/libros_views.py
----------------------------
Blueprint de gestión de libros: listado con búsqueda/filtros, crear,
editar, eliminar. Lectura abierta a cualquier sesión (catálogo);
escritura restringida por permiso 'gestionar_libros'.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

from controladores.libros_controller import LibrosController, ISBNDuplicadoError
from formularios.libro_form import LibroForm, LibroEditForm
from formularios.busqueda_form import BusquedaLibroForm
from utilitarios.decoradores import login_requerido, requiere_permiso

libros_bp = Blueprint("libros", __name__, url_prefix="/libros")


@libros_bp.route("/")
@login_requerido
def listar():
    controlador = LibrosController()
    formulario_busqueda = BusquedaLibroForm()
    formulario_busqueda.id_categoria.choices = [(0, "Todas")] + controlador.opciones_categoria()

    texto = request.args.get("texto", "").strip() or None
    id_categoria = request.args.get("id_categoria", type=int) or None
    solo_disponibles = request.args.get("solo_disponibles") == "si"

    if texto:
        formulario_busqueda.texto.data = texto
    if id_categoria:
        formulario_busqueda.id_categoria.data = id_categoria
    if solo_disponibles:
        formulario_busqueda.solo_disponibles.data = "si"

    libros = controlador.listar(texto=texto, id_categoria=id_categoria, solo_disponibles=solo_disponibles)
    return render_template("libros/listar.html", libros=libros, formulario_busqueda=formulario_busqueda)


@libros_bp.route("/nuevo", methods=["GET", "POST"])
@login_requerido
@requiere_permiso("gestionar_libros")
def crear():
    controlador = LibrosController()
    formulario = LibroForm()
    formulario.id_categoria.choices = controlador.opciones_categoria()
    formulario.id_estado.choices = controlador.opciones_estado()

    if formulario.validate_on_submit():
        try:
            controlador.crear({
                "isbn": formulario.isbn.data,
                "titulo": formulario.titulo.data,
                "autor": formulario.autor.data,
                "editorial": formulario.editorial.data,
                "anio_publicacion": formulario.anio_publicacion.data,
                "id_categoria": formulario.id_categoria.data,
                "id_estado": formulario.id_estado.data,
            })
            flash("Libro creado correctamente.", "success")
            return redirect(url_for("libros.listar"))
        except ISBNDuplicadoError as e:
            flash(str(e), "danger")

    return render_template("libros/formulario.html", formulario=formulario, accion="Crear")


@libros_bp.route("/<isbn>/editar", methods=["GET", "POST"])
@login_requerido
@requiere_permiso("gestionar_libros")
def editar(isbn):
    controlador = LibrosController()
    libro = controlador.obtener(isbn)
    if libro is None:
        flash("El libro no existe.", "warning")
        return redirect(url_for("libros.listar"))

    formulario = LibroEditForm()
    formulario.id_categoria.choices = controlador.opciones_categoria()
    formulario.id_estado.choices = controlador.opciones_estado()

    if request.method == "GET":
        formulario.isbn.data = libro.isbn
        formulario.titulo.data = libro.titulo
        formulario.autor.data = libro.autor_principal
        formulario.editorial.data = libro.editorial
        formulario.anio_publicacion.data = libro.anio_publicacion
        formulario.id_categoria.data = libro.categoria.id_categoria
        formulario.id_estado.data = libro.estado.id_estado

    if formulario.validate_on_submit():
        controlador.actualizar(isbn, {
            "titulo": formulario.titulo.data,
            "autor": formulario.autor.data,
            "editorial": formulario.editorial.data,
            "anio_publicacion": formulario.anio_publicacion.data,
            "id_categoria": formulario.id_categoria.data,
            "id_estado": formulario.id_estado.data,
        })
        flash("Libro actualizado correctamente.", "success")
        return redirect(url_for("libros.listar"))

    return render_template("libros/formulario.html", formulario=formulario, accion="Editar")


@libros_bp.route("/<isbn>/eliminar", methods=["POST"])
@login_requerido
@requiere_permiso("gestionar_libros")
def eliminar(isbn):
    controlador = LibrosController()
    if controlador.eliminar(isbn):
        flash("Libro eliminado correctamente.", "success")
    else:
        flash("No se pudo eliminar el libro (puede tener préstamos o reservas asociadas).", "danger")
    return redirect(url_for("libros.listar"))
