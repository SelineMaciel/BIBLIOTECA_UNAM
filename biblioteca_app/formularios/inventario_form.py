"""
formularios/inventario_form.py
------------------------------------
Formulario de creación/edición de Inventario: relaciona un Libro con
una Sucursal y define cuántas unidades hay en total y disponibles.
"""

from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, ValidationError


class InventarioForm(FlaskForm):
    isbn = SelectField("Libro", validators=[DataRequired()])
    id_sucursal = SelectField("Sucursal", coerce=int, validators=[DataRequired()])
    cantidad_total = IntegerField(
        "Cantidad total",
        validators=[DataRequired(message="La cantidad total es obligatoria"), NumberRange(min=0, message="No puede ser negativa")],
    )
    cantidad_disponible = IntegerField(
        "Cantidad disponible",
        validators=[DataRequired(message="La cantidad disponible es obligatoria"), NumberRange(min=0, message="No puede ser negativa")],
    )
    submit = SubmitField("Guardar")

    def validate_cantidad_disponible(self, campo):
        if self.cantidad_total.data is not None and campo.data is not None:
            if campo.data > self.cantidad_total.data:
                raise ValidationError("La cantidad disponible no puede ser mayor que la cantidad total.")
