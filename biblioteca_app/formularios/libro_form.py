"""
formularios/libro_form.py
-------------------------------
Formulario de creación/edición de Libro.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange


class LibroForm(FlaskForm):
    isbn = StringField(
        "ISBN",
        validators=[DataRequired(message="El ISBN es obligatorio"), Length(max=20)],
    )
    titulo = StringField(
        "Título",
        validators=[DataRequired(message="El título es obligatorio"), Length(max=200)],
    )
    autor = StringField(
        "Autor principal",
        validators=[DataRequired(message="El autor principal es obligatorio"), Length(max=150)],
    )
    editorial = StringField("Editorial", validators=[Optional(), Length(max=150)])
    anio_publicacion = IntegerField(
        "Año de publicación",
        validators=[Optional(), NumberRange(min=1450, max=2100, message="Año fuera de rango")],
    )
    id_categoria = SelectField("Categoría", coerce=int, validators=[DataRequired()])
    id_estado = SelectField("Estado", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Guardar")


class LibroEditForm(LibroForm):
    """En edición el ISBN no se debe poder cambiar (es la PK)."""
    isbn = StringField("ISBN", render_kw={"readonly": True})
