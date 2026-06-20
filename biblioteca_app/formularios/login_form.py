"""
formularios/login_form.py
------------------------------
Formulario único de login. El campo password es opcional porque,
según lo decidido, solo AdminUser tiene contraseña real; Empleado y
Usuario inician sesión solo con su email (uso académico, ver
servicios/servicio_auth.py).
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Optional


class LoginForm(FlaskForm):
    email = StringField(
        "Correo electrónico",
        validators=[DataRequired(message="El correo es obligatorio"), Email(message="Correo inválido")],
    )
    password = PasswordField(
        "Contraseña (solo administradores)",
        validators=[Optional()],
    )
    submit = SubmitField("Iniciar sesión")
