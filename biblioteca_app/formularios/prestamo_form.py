"""
formularios/prestamo_form.py
-----------------------------------
Formulario para registrar un nuevo préstamo desde la vista de
empleado/admin.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired


class PrestamoForm(FlaskForm):
    id_usuario = SelectField("Usuario", coerce=int, validators=[DataRequired()])
    isbn = SelectField("Libro", validators=[DataRequired()])
    id_sucursal = SelectField("Sucursal", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Registrar préstamo")


class ReservaForm(FlaskForm):
    id_usuario = SelectField("Usuario", coerce=int, validators=[DataRequired()])
    isbn = SelectField("Libro", validators=[DataRequired()])
    id_sucursal = SelectField("Sucursal de recojo", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Crear reserva")
