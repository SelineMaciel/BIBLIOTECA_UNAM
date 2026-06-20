"""
vistas/reportes_views.py
-------------------------------
Blueprint de reportes. En esta fase muestra el dashboard completo con
gráficos reales (matplotlib/seaborn) embebidos como imágenes base64,
estadísticas descriptivas (pandas/numpy), carga masiva de libros desde
CSV/Excel y exportación de datos a Excel.
"""

from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    send_file, request, session
)

from controladores.reportes_controller import ReportesController
from controladores.libros_controller import LibrosController
from formularios.carga_masiva_form import CargaMasivaLibrosForm
from utilitarios.decoradores import login_requerido, requiere_permiso
from utilitarios.sesion import obtener_persona_actual

reportes_bp = Blueprint("reportes", __name__, url_prefix="/reportes")


@reportes_bp.route("/")
@login_requerido
@requiere_permiso("generar_reportes")
def dashboard():
    import datetime
    anio = request.args.get("anio", type=int) or datetime.date.today().year
    controlador = ReportesController()
    datos = controlador.dashboard_datos(anio)

    # Registrar trazabilidad si hay admin en sesión
    if session.get("tipo_sesion") == "admin":
        admin = obtener_persona_actual()
        if admin:
            controlador.registrar_generacion(admin, "Dashboard estadístico", f"Año {anio}")

    return render_template("reportes/dashboard.html", datos=datos, anio=anio)


@reportes_bp.route("/carga-masiva", methods=["GET", "POST"])
@login_requerido
@requiere_permiso("gestionar_libros")
def carga_masiva():
    controlador_libros = LibrosController()
    formulario = CargaMasivaLibrosForm()
    formulario.id_categoria.choices = controlador_libros.opciones_categoria()
    formulario.id_estado.choices = controlador_libros.opciones_estado()
    resultado = None

    if formulario.validate_on_submit():
        controlador = ReportesController()
        resultado = controlador.importar_libros(
            formulario.archivo.data,
            formulario.id_categoria.data,
            formulario.id_estado.data,
        )
        if "error" in resultado:
            flash(resultado["error"], "danger")
        else:
            flash(
                f"Importación completada: {resultado['libros_insertados']} libros "
                f"insertados, {resultado['total_errores']} filas con errores.",
                "success" if resultado["libros_insertados"] > 0 else "warning",
            )

    return render_template("reportes/carga_masiva.html", formulario=formulario, resultado=resultado)


@reportes_bp.route("/plantilla-excel")
@login_requerido
@requiere_permiso("gestionar_libros")
def descargar_plantilla():
    """Descarga la plantilla Excel vacía para carga masiva."""
    buffer = ReportesController().plantilla_carga_masiva()
    return send_file(
        buffer,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="plantilla_carga_masiva_libros.xlsx",
    )


@reportes_bp.route("/exportar/libros")
@login_requerido
@requiere_permiso("generar_reportes")
def exportar_libros():
    """Descarga el catálogo completo de libros en Excel."""
    buffer = ReportesController().exportar_libros_excel()
    return send_file(
        buffer,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="catalogo_libros.xlsx",
    )


@reportes_bp.route("/procesar-ciclo", methods=["POST"])
@login_requerido
@requiere_permiso("generar_reportes")
def procesar_ciclo_manual():
    """
    Ejecuta el ciclo diario manualmente (procesa vencimientos, genera
    multas y envía correos). Disponible para el admin como botón en el
    dashboard para forzar el proceso sin esperar al día siguiente.
    """
    from servicios.servicio_ciclo_diario import ServicioCicloDiario
    from flask import current_app
    try:
        resumen = ServicioCicloDiario().ejecutar()
        # Resetear el flag de "ya ejecutado hoy" para que pueda volver
        # a ejecutarse mañana normalmente
        current_app._ultima_ejecucion_ciclo = str(__import__("datetime").date.today())
        flash(
            f"Ciclo procesado: {resumen['prestamos_vencidos_marcados']} préstamos marcados vencidos, "
            f"{resumen['multas_generadas']} multas nuevas generadas, "
            f"{resumen['correos_multa_enviados']} avisos de deuda pendiente enviados, "
            f"{resumen['correos_recordatorio_enviados']} recordatorios de vencimiento próximo enviados.",
            "success"
        )
    except Exception as e:
        flash(f"Error al procesar el ciclo: {e}", "danger")
    return redirect(url_for("reportes.dashboard"))


@reportes_bp.route("/exportar/prestamos")
@login_requerido
@requiere_permiso("generar_reportes")
def exportar_prestamos():
    """Descarga el historial completo de préstamos en Excel."""
    buffer = ReportesController().exportar_prestamos_excel()
    return send_file(
        buffer,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="historial_prestamos.xlsx",
    )
