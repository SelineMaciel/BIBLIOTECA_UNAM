"""
controladores/reportes_controller.py
--------------------------------------------
Envuelve ServicioReportes y ServicioAnalisis para la vista de
dashboard del Administrador, ahora con gráficos reales y
estadísticas descriptivas (Fase 5).
"""

import os
import tempfile

from servicios.servicio_reportes import ServicioReportes
from servicios.servicio_analisis import ServicioAnalisis
from controladores.libros_controller import LibrosController
from utilitarios.exportador_excel import ExportadorExcel


class ReportesController:
    def __init__(self):
        self._servicio_reportes = ServicioReportes()
        self._servicio_analisis = ServicioAnalisis()

    def dashboard_datos(self, anio: int = None) -> dict:
        """Devuelve datos JSON-serializables para Chart.js (dashboard interactivo)."""
        return self._servicio_analisis.datos_dashboard_json(anio)

    def registrar_generacion(self, admin, tipo_reporte: str, descripcion: str = ""):
        return self._servicio_reportes.registrar_generacion(admin, tipo_reporte, descripcion)

    def exportar_libros_excel(self):
        """Devuelve un BytesIO con todos los libros en formato Excel."""
        libros = LibrosController().listar()
        return ExportadorExcel.exportar_libros(libros)

    def exportar_prestamos_excel(self):
        """Devuelve un BytesIO con todos los préstamos en formato Excel."""
        from persistencia.repositorio_prestamos import RepositorioPrestamos
        prestamos = RepositorioPrestamos().obtener_todos(orden="id_prestamo DESC")
        return ExportadorExcel.exportar_prestamos(prestamos)

    def plantilla_carga_masiva(self):
        """Devuelve un BytesIO con la plantilla Excel vacía para carga masiva."""
        return ExportadorExcel.plantilla_carga_masiva()

    def importar_libros(self, archivo, id_categoria: int, id_estado: int) -> dict:
        """
        Recibe el FileStorage de Flask, lo guarda temporalmente, lo procesa
        con pandas (ServicioAnalisis) y persiste los libros válidos.
        """
        # Guardar en archivo temporal para que pandas pueda leerlo
        extension = archivo.filename.rsplit(".", 1)[-1].lower()
        tmp = tempfile.NamedTemporaryFile(suffix=f".{extension}", delete=False)
        try:
            archivo.save(tmp.name)
            tmp.close()
            resultado = self._servicio_analisis.importar_libros_desde_archivo(
                tmp.name, id_categoria, id_estado
            )
        finally:
            os.unlink(tmp.name)

        if "error" in resultado:
            return resultado

        # Persistir solo los registros que pasaron la validación
        libros_insertados, errores_db = 0, []
        controlador_libros = LibrosController()
        for datos in resultado["validos"]:
            try:
                controlador_libros.crear(datos)
                libros_insertados += 1
            except Exception as e:
                errores_db.append(f"ISBN {datos['isbn']}: {e}")

        resultado["libros_insertados"] = libros_insertados
        resultado["errores_db"] = errores_db
        return resultado
