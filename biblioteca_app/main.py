"""
main.py
---------
Punto de entrada de la aplicación Flask. Crea la app, registra la
SECRET_KEY y todos los blueprints (vistas/), y arranca el servidor
de desarrollo.

Para ejecutar (con XAMPP/MySQL ya corriendo):
    python main.py
"""

from flask import Flask

from config import ConfiguracionApp

# Blueprints
from vistas.auth_views import auth_bp
from vistas.admin_views import admin_bp
from vistas.empleado_views import empleado_bp
from vistas.usuario_views import usuario_bp
from vistas.usuarios_views import usuarios_bp
from vistas.empleados_views import empleados_bp
from vistas.admins_views import admins_bp
from vistas.libros_views import libros_bp
from vistas.inventario_views import inventario_bp
from vistas.prestamos_views import prestamos_bp
from vistas.reservas_views import reservas_bp
from vistas.reportes_views import reportes_bp


def crear_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="vistas/templates",
        static_folder="static",
    )
    app.config["SECRET_KEY"] = ConfiguracionApp.SECRET_KEY
    app.config["DEBUG"] = ConfiguracionApp.DEBUG

    # Registro de blueprints (modularización)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(empleado_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(empleados_bp)
    app.register_blueprint(admins_bp)
    app.register_blueprint(libros_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(prestamos_bp)
    app.register_blueprint(reservas_bp)
    app.register_blueprint(reportes_bp)

    # ── Ciclo diario automático ──────────────────────────────────────
    # Se ejecuta una vez por día (al primer request del día).
    # Procesa vencimientos, genera multas y envía correos de aviso.
    # _ultima_ejecucion_ciclo vive en el contexto de la app (no de sesión
    # de usuario), así que persiste mientras Flask esté corriendo.
    app._ultima_ejecucion_ciclo = None  # type: ignore[attr-defined]

    @app.before_request
    def ciclo_diario_automatico():
        from flask import request as req
        # No ejecutar en rutas estáticas
        if req.endpoint == "static":
            return
        hoy = str(__import__("datetime").date.today())
        if app._ultima_ejecucion_ciclo == hoy:  # type: ignore[attr-defined]
            return
        # Marcar como ejecutado ANTES de procesar para no reintentar
        # si hay un error en la BD (evita bucle de errores)
        app._ultima_ejecucion_ciclo = hoy  # type: ignore[attr-defined]
        try:
            from servicios.servicio_ciclo_diario import ServicioCicloDiario
            resumen = ServicioCicloDiario().ejecutar()
            print(
                f"[CicloDiario {hoy}] "
                f"vencidos={resumen['prestamos_vencidos_marcados']} "
                f"multas={resumen['multas_generadas']} "
                f"correos_multa={resumen['correos_multa_enviados']} "
                f"correos_recordatorio={resumen['correos_recordatorio_enviados']}"
            )
        except Exception as e:
            print(f"[CicloDiario] Error al ejecutar ciclo diario: {e}")

    @app.errorhandler(403)
    def acceso_denegado(_error):
        return "Acceso denegado: no tienes permiso para ver esta página.", 403

    @app.errorhandler(404)
    def no_encontrado(_error):
        return "Página no encontrada.", 404

    return app


app = crear_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=ConfiguracionApp.DEBUG)
