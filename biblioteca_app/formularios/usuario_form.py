"""
formularios/usuario_form.py
---------------------------------
Formulario de creación/edición de Usuario (lector de biblioteca).
Incluye los datos heredados de Persona (nombre, email, phone) y los
propios de Usuario (edad, membresía, rol).
"""

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, NumberRange, Optional, Length


class UsuarioForm(FlaskForm):
    nombre = StringField(
        "Nombre completo",
        validators=[DataRequired(message="El nombre es obligatorio"), Length(max=100)],
    )
    email = StringField(
        "Correo electrónico",
        validators=[DataRequired(message="El correo es obligatorio"), Email(message="Correo inválido")],
    )
    phone = StringField("Teléfono", validators=[Optional(), Length(max=20)])
    edad = IntegerField(
        "Edad",
        validators=[Optional(), NumberRange(min=0, max=120, message="Edad fuera de rango")],
    )
    id_membresia = SelectField("Membresía", coerce=int, validators=[DataRequired()])
    id_rol = SelectField("Rol", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Guardar")
