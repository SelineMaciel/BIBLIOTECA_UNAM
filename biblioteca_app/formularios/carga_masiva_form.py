"""
formularios/carga_masiva_form.py
-----------------------------------------
Formulario de carga masiva de libros desde archivo CSV o Excel.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired


class CargaMasivaLibrosForm(FlaskForm):
    archivo = FileField(
        "Archivo CSV o Excel",
        validators=[
            FileRequired(message="Debes seleccionar un archivo."),
            FileAllowed(["csv", "xlsx", "xls"], message="Solo se permiten archivos .csv, .xlsx o .xls"),
        ],
    )
    id_categoria = SelectField(
        "Categoría a asignar a todos los libros del archivo",
        coerce=int,
        validators=[DataRequired()],
    )
    id_estado = SelectField(
        "Estado inicial",
        coerce=int,
        validators=[DataRequired()],
    )
    submit = SubmitField("Importar libros")
