"""
formularios/empleado_form.py
-----------------------------------
Formulario de creación/edición de Empleado.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length


class EmpleadoForm(FlaskForm):
    nombre = StringField(
        "Nombre completo",
        validators=[DataRequired(message="El nombre es obligatorio"), Length(max=100)],
    )
    email = StringField(
        "Correo electrónico",
        validators=[DataRequired(message="El correo es obligatorio"), Email(message="Correo inválido")],
    )
    phone = StringField("Teléfono", validators=[Optional(), Length(max=20)])
    cargo = StringField(
        "Cargo",
        validators=[DataRequired(message="El cargo es obligatorio"), Length(max=100)],
    )
    id_sucursal = SelectField("Sucursal", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Guardar")
