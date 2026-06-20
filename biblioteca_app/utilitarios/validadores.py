"""
utilitarios/validadores.py
-------------------------------
Validaciones reutilizables, independientes de Flask-WTF, para usar
también desde controladores o servicios cuando haga falta validar
datos que no vienen directamente de un formulario web (ej. import
masivo de libros en la Fase 5).
"""

import re

PATRON_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PATRON_ISBN = re.compile(r"^[0-9\-Xx]{8,20}$")


def es_email_valido(email: str) -> bool:
    return bool(email) and bool(PATRON_EMAIL.match(email))


def es_isbn_valido(isbn: str) -> bool:
    return bool(isbn) and bool(PATRON_ISBN.match(isbn))


def es_anio_valido(anio) -> bool:
    if anio is None or anio == "":
        return True  # el campo es opcional en el esquema
    try:
        anio_int = int(anio)
        return 1450 <= anio_int <= 2100  # rango razonable, 1450 ~ inicio imprenta
    except (TypeError, ValueError):
        return False


def es_telefono_valido(telefono: str) -> bool:
    if not telefono:
        return True  # opcional en el esquema
    return bool(re.match(r"^[0-9+\-\s()]{6,20}$", telefono))
