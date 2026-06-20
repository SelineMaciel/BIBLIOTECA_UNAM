"""
formularios/admin_form.py
-------------------------------
Formulario de creación de AdminUser. La edición de password se
maneja por separado (no se reusa este form para evitar reescribir
el hash accidentalmente con un campo vacío).
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional


class AdminForm(FlaskForm):
    nombre = StringField(
        "Nombre completo",
        validators=[DataRequired(message="El nombre es obligatorio"), Length(max=100)],
    )
    email = StringField(
        "Correo electrónico",
        validators=[DataRequired(message="El correo es obligatorio"), Email(message="Correo inválido")],
    )
    phone = StringField("Teléfono", validators=[Optional(), Length(max=20)])
    admin_user = StringField(
        "Usuario administrador",
        validators=[DataRequired(message="El usuario es obligatorio"), Length(max=50)],
    )
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(message="La contraseña es obligatoria"), Length(min=6, message="Mínimo 6 caracteres")],
    )
    id_rol = SelectField("Rol", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Guardar")
