"""
servicios/servicio_reportes.py
------------------------------------
Genera estadísticas descriptivas básicas sobre préstamos, libros y
usuarios, y registra cada generación en la tabla `reportes` (trazabilidad
de qué AdminUser generó qué reporte y cuándo).

En la Fase 5 (Ciencia de Datos) este servicio se ampliará para usar
pandas/numpy/matplotlib/seaborn y construir el dashboard estadístico
completo (gráficos de barras, circulares, series temporales). Por
ahora deja las consultas base ya construidas y probadas, devolviendo
estructuras de datos simples (listas de dicts) que luego pandas podrá
consumir directamente con pd.DataFrame(...).
"""

from persistencia.repositorio_reservas import RepositorioReportes
from modelos.reserva import Reporte


class ServicioReportes:
    def __init__(self):
        self._repo_reportes = RepositorioReportes()

    def libros_mas_prestados(self, limite: int = 10) -> list:
        sql = """
            SELECT l.titulo, COUNT(*) AS total_prestamos
            FROM prestamos p
            INNER JOIN libros l ON l.ISBN = p.isbn
            GROUP BY l.ISBN, l.titulo
            ORDER BY total_prestamos DESC
            LIMIT %s
        """
        return self._repo_reportes.ejecutar_consulta_personalizada(sql, (limite,))

    def prestamos_por_categoria(self) -> list:
        sql = """
            SELECT c.nombre_categoria, COUNT(*) AS total_prestamos
            FROM prestamos p
            INNER JOIN libros l ON l.ISBN = p.isbn
            INNER JOIN categorias c ON c.id_categoria = l.id_categoria
            GROUP BY c.id_categoria, c.nombre_categoria
            ORDER BY total_prestamos DESC
        """
        return self._repo_reportes.ejecutar_consulta_personalizada(sql)

    def distribucion_membresias(self) -> list:
        sql = """
            SELECT m.tipo_membresia, COUNT(*) AS total_usuarios
            FROM usuarios u
            INNER JOIN membresias m ON m.id_membresia = u.id_membresia
            GROUP BY m.id_membresia, m.tipo_membresia
        """
        return self._repo_reportes.ejecutar_consulta_personalizada(sql)

    def prestamos_por_mes(self, anio: int) -> list:
        sql = """
            SELECT MONTH(fecha_prestamo) AS mes, COUNT(*) AS total
            FROM prestamos
            WHERE YEAR(fecha_prestamo) = %s
            GROUP BY MONTH(fecha_prestamo)
            ORDER BY mes
        """
        return self._repo_reportes.ejecutar_consulta_personalizada(sql, (anio,))

    def resumen_multas(self) -> dict:
        sql = """
            SELECT
                COUNT(*) AS total_multas,
                SUM(CASE WHEN estado_pago = 'PENDIENTE' THEN 1 ELSE 0 END) AS pendientes,
                SUM(CASE WHEN estado_pago = 'PAGADO' THEN 1 ELSE 0 END) AS pagadas,
                COALESCE(SUM(monto), 0) AS monto_total
            FROM multas
        """
        filas = self._repo_reportes.ejecutar_consulta_personalizada(sql)
        return filas[0] if filas else {}

    def registrar_generacion(self, admin, tipo_reporte: str, descripcion: str = "") -> Reporte:
        """Inserta una fila en `reportes` para dejar trazabilidad de
        quién generó qué reporte y cuándo (AdminUser -> generarReportes)."""
        valores = {
            "id_admin": admin.id_admin,
            "tipo_reporte": tipo_reporte,
            "descripcion": descripcion,
        }
        columnas = ", ".join(valores.keys())
        marcadores = ", ".join(["%s"] * len(valores))
        sql = f"INSERT INTO reportes ({columnas}) VALUES ({marcadores})"
        cursor = self._repo_reportes._db.obtener_cursor()
        cursor.execute(sql, list(valores.values()))
        id_reporte = cursor.lastrowid
        self._repo_reportes._db.confirmar()
        cursor.close()
        return self._repo_reportes.obtener_por_id(id_reporte)
