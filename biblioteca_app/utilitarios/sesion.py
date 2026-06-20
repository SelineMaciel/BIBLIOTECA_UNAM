"""
utilitarios/sesion.py
-------------------------
La sesión Flask solo guarda datos simples (tipo_sesion, id_sesion).
Este módulo se encarga de, a partir de esos datos, reconstruir el
objeto de dominio completo (Usuario, Empleado o AdminUser) cuando
se necesita. Así evitamos serializar objetos completos en la cookie
de sesión y mantenemos la capa de persistencia como única fuente de
verdad.
"""

from flask import session

from persistencia.repositorio_personas import (
    RepositorioUsuarios,
    RepositorioEmpleados,
    RepositorioAdminUsers,
)


def guardar_sesion(tipo: str, id_persona_especifico: int, nombre: str):
    """tipo: 'admin' | 'empleado' | 'usuario'"""
    session["tipo_sesion"] = tipo
    session["id_sesion"] = id_persona_especifico
    session["nombre_sesion"] = nombre


def cerrar_sesion():
    session.clear()


def obtener_persona_actual():
    """
    Devuelve el objeto Persona (Usuario, Empleado o AdminUser) según
    lo guardado en la sesión actual, o None si no hay sesión activa.
    POLIMORFISMO: el resultado puede ser cualquiera de las 3 subclases;
    quien llame a este método no necesita preocuparse por cuál es.
    """
    tipo = session.get("tipo_sesion")
    id_sesion = session.get("id_sesion")
    if tipo is None or id_sesion is None:
        return None

    if tipo == "admin":
        return RepositorioAdminUsers().obtener_por_id_completo(id_sesion)
    elif tipo == "empleado":
        return RepositorioEmpleados().obtener_por_id_completo(id_sesion)
    elif tipo == "usuario":
        return RepositorioUsuarios().obtener_por_id_completo(id_sesion)
    return None
