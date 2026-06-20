"""
formularios/busqueda_form.py
-----------------------------------
Formulario simple de búsqueda/filtro, reutilizado en varias vistas
(libros, usuarios). GET en vez de POST para que la búsqueda quede
en la URL y se pueda compartir/recargar sin perder el filtro.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import Optional


class BusquedaLibroForm(FlaskForm):
    class Meta:
        csrf = False  # formulario GET, no necesita protección CSRF

    texto = StringField("Buscar por título", validators=[Optional()])
    id_categoria = SelectField("Categoría", coerce=int, validators=[Optional()])
    solo_disponibles = SelectField(
        "Disponibilidad",
        choices=[("", "Todos"), ("si", "Solo disponibles")],
        validators=[Optional()],
    )
    submit = SubmitField("Buscar")


class BusquedaUsuarioForm(FlaskForm):
    class Meta:
        csrf = False

    texto = StringField("Buscar por nombre", validators=[Optional()])
    submit = SubmitField("Buscar")
