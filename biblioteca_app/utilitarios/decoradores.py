"""
utilitarios/decoradores.py
------------------------------
Decoradores reutilizables para proteger rutas Flask:
  - @login_requerido: exige que haya una sesión activa.
  - @requiere_permiso("nombre_permiso"): exige sesión + que la
    persona logueada tenga ese permiso (usa ServicioPermisos, que a
    su vez delega en el polimorfismo de Persona.tiene_acceso()).
  - @requiere_tipo("admin", "empleado", "usuario"): exige que la
    sesión sea de uno de los tipos indicados.

Estos decoradores son los únicos puntos del proyecto donde Flask
"toca" la lógica de permisos; todo lo demás vive en servicios/.
"""

from functools import wraps
from flask import session, redirect, url_for, flash, abort

from servicios.servicio_permisos import ServicioPermisos


def login_requerido(funcion):
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        if "tipo_sesion" not in session or "id_sesion" not in session:
            flash("Debes iniciar sesión para acceder a esta página.", "warning")
            return redirect(url_for("auth.login"))
        return funcion(*args, **kwargs)
    return envoltura


def requiere_tipo(*tipos_permitidos):
    """
    tipos_permitidos: alguno de "admin", "empleado", "usuario".
    Ejemplo: @requiere_tipo("admin", "empleado")
    """
    def decorador(funcion):
        @wraps(funcion)
        def envoltura(*args, **kwargs):
            if "tipo_sesion" not in session:
                flash("Debes iniciar sesión para acceder a esta página.", "warning")
                return redirect(url_for("auth.login"))
            if session["tipo_sesion"] not in tipos_permitidos:
                abort(403)
            return funcion(*args, **kwargs)
        return envoltura
    return decorador


def requiere_permiso(nombre_permiso: str):
    """
    Exige que la persona en sesión tenga el permiso indicado. Reconstruye
    el objeto Persona desde la sesión usando las funciones de
    utilitarios/sesion.py (ver ese módulo) y delega en ServicioPermisos,
    que a su vez usa el polimorfismo de tiene_acceso().
    """
    def decorador(funcion):
        @wraps(funcion)
        def envoltura(*args, **kwargs):
            from utilitarios.sesion import obtener_persona_actual  # import perezoso evita ciclos

            if "tipo_sesion" not in session:
                flash("Debes iniciar sesión para acceder a esta página.", "warning")
                return redirect(url_for("auth.login"))

            persona = obtener_persona_actual()
            servicio_permisos = ServicioPermisos()
            if not servicio_permisos.usuario_puede(persona, nombre_permiso):
                abort(403)
            return funcion(*args, **kwargs)
        return envoltura
    return decorador
