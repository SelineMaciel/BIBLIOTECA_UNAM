"""
utilitarios/exportador_excel.py
---------------------------------------
Genera archivos Excel en memoria (BytesIO) usando pandas + openpyxl,
listos para enviarse como descarga desde una ruta Flask sin necesitar
guardar archivos en disco.
"""

import io
import pandas as pd
from datetime import datetime


class ExportadorExcel:
    """
    Exporta datos del sistema a Excel con formato básico.
    Se devuelve un BytesIO que Flask puede enviar directamente como
    respuesta de descarga con send_file().
    """

    @staticmethod
    def exportar_dataframe(df: pd.DataFrame, nombre_hoja: str = "Datos") -> io.BytesIO:
        """
        Convierte cualquier DataFrame a Excel en memoria.
        Aplica formato de encabezados en negrita/fondo gris.
        """
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=nombre_hoja)
            # Formato básico del encabezado
            hoja = writer.sheets[nombre_hoja]
            from openpyxl.styles import Font, PatternFill, Alignment
            estilo_encabezado = Font(bold=True, color="FFFFFF")
            fondo_encabezado = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
            for celda in hoja[1]:
                celda.font = estilo_encabezado
                celda.fill = fondo_encabezado
                celda.alignment = Alignment(horizontal="center")
            # Ajustar ancho de columnas automáticamente
            for columna in hoja.columns:
                max_largo = max(len(str(celda.value or "")) for celda in columna)
                hoja.column_dimensions[columna[0].column_letter].width = min(max_largo + 4, 50)
        buffer.seek(0)
        return buffer

    @staticmethod
    def exportar_libros(libros: list) -> io.BytesIO:
        datos = [
            {
                "ISBN": l.isbn,
                "Título": l.titulo,
                "Autor": l.autor_principal,
                "Editorial": l.editorial or "",
                "Año": l.anio_publicacion or "",
                "Categoría": l.categoria.nombre_categoria,
                "Estado": l.estado.nombre_estado,
            }
            for l in libros
        ]
        df = pd.DataFrame(datos)
        return ExportadorExcel.exportar_dataframe(df, "Libros")

    @staticmethod
    def exportar_prestamos(prestamos: list) -> io.BytesIO:
        datos = [
            {
                "ID": p.id_prestamo,
                "Usuario": p.usuario.nombre if p.usuario else "",
                "Libro": p.libro.titulo if p.libro else "",
                "Fecha préstamo": p.fecha_prestamo,
                "Fecha devolución": p.fecha_devolucion or "Pendiente",
                "Estado": p.estado.descripcion,
                "Multas pendientes (S/)": p.total_multas_pendientes(),
            }
            for p in prestamos
        ]
        df = pd.DataFrame(datos)
        return ExportadorExcel.exportar_dataframe(df, "Préstamos")

    @staticmethod
    def plantilla_carga_masiva() -> io.BytesIO:
        """
        Genera una plantilla Excel lista para que el admin la descargue,
        la llene con libros y la suba para importación masiva.
        """
        df = pd.DataFrame(columns=["ISBN", "titulo", "autor", "editorial", "anio_publicacion"])
        # Fila de ejemplo para guiar al usuario
        ejemplo = {
            "ISBN": "978-0000000000",
            "titulo": "Ejemplo de título",
            "autor": "Apellido, Nombre",
            "editorial": "Editorial Ejemplo",
            "anio_publicacion": 2024,
        }
        df = pd.concat([df, pd.DataFrame([ejemplo])], ignore_index=True)
        return ExportadorExcel.exportar_dataframe(df, "Libros_a_importar")
