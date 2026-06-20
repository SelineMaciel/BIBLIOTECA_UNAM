"""
persistencia/repositorio_prestamos.py
-----------------------------------------
Repositorios concretos para EstadoPrestamo, Multa y Prestamo.

RepositorioPrestamos ensambla Usuario, Libro, Empleado y Sucursal
(asociaciones) y construye la lista de Multa (composición) cargando
desde la tabla `multas` y adjuntándolas al objeto Prestamo.
"""

from datetime import date
from persistencia.repositorio_base import RepositorioBase
from persistencia.repositorio_personas import RepositorioUsuarios, RepositorioEmpleados
from persistencia.repositorio_libros import RepositorioLibros
from persistencia.repositorio_membresias import RepositorioSucursales
from modelos.prestamo import EstadoPrestamo, Multa, Prestamo


class RepositorioEstadosPrestamo(RepositorioBase):
    def __init__(self):
        super().__init__(nombre_tabla="estados_prestamo", columnas_pk="id_estado_prestamo")

    def _fila_a_objeto(self, fila: dict) -> EstadoPrestamo:
        return EstadoPrestamo(fila["id_estado_prestamo"], fila["descripcion"])

    def _objeto_a_valores(self, objeto: EstadoPrestamo) -> dict:
        return {"descripcion": objeto.descripcion}

    def obtener_por_descripcion(self, descripcion: str) -> EstadoPrestamo:
        resultados = self.buscar("descripcion", descripcion)
        return resultados[0] if resultados else None


class RepositorioMultas(RepositorioBase):
    def __init__(self):
        super().__init__(nombre_tabla="multas", columnas_pk="id_multa")

    def _fila_a_objeto(self, fila: dict) -> Multa:
        return Multa(
            id_multa=fila["id_multa"],
            monto=float(fila["monto"]),
            fecha_multa=fila["fecha_multa"],
            estado_pago=fila["estado_pago"],
        )

    def _objeto_a_valores(self, objeto: Multa) -> dict:
        return {
            "monto": objeto.monto,
            "fecha_multa": objeto.fecha_multa,
            "estado_pago": objeto.estado_pago,
        }

    def obtener_por_prestamo(self, id_prestamo: int) -> list:
        return self.buscar("id_prestamo", id_prestamo)

    def crear_para_prestamo(self, id_prestamo: int, monto: float, fecha_multa: date) -> int:
        sql = "INSERT INTO multas (id_prestamo, monto, fecha_multa) VALUES (%s, %s, %s)"
        cursor = self._db.obtener_cursor()
        cursor.execute(sql, (id_prestamo, monto, fecha_multa))
        nuevo_id = cursor.lastrowid
        self._db.confirmar()
        cursor.close()
        return nuevo_id

    def marcar_pagada(self, id_multa: int) -> bool:
        sql = "UPDATE multas SET estado_pago = 'PAGADO' WHERE id_multa = %s"
        cursor = self._db.obtener_cursor()
        cursor.execute(sql, (id_multa,))
        afectadas = cursor.rowcount
        self._db.confirmar()
        cursor.close()
        return afectadas > 0


class RepositorioPrestamos(RepositorioBase):
    def __init__(self):
        super().__init__(nombre_tabla="prestamos", columnas_pk="id_prestamo")
        self._repo_usuarios = RepositorioUsuarios()
        self._repo_libros = RepositorioLibros()
        self._repo_empleados = RepositorioEmpleados()
        self._repo_sucursales = RepositorioSucursales()
        self._repo_estados = RepositorioEstadosPrestamo()
        self._repo_multas = RepositorioMultas()

    def _fila_a_objeto(self, fila: dict) -> Prestamo:
        usuario = self._repo_usuarios.obtener_por_id_completo(fila["id_usuario"])
        libro = self._repo_libros.obtener_por_id(fila["isbn"])
        estado = self._repo_estados.obtener_por_id(fila["id_estado"])
        empleado = self._repo_empleados.obtener_por_id_completo(fila["id_empleado"]) if fila.get("id_empleado") else None
        sucursal = self._repo_sucursales.obtener_por_id(fila["id_sucursal"]) if fila.get("id_sucursal") else None

        prestamo = Prestamo(
            id_prestamo=fila["id_prestamo"],
            usuario=usuario,
            libro=libro,
            fecha_prestamo=fila["fecha_prestamo"],
            estado=estado,
            fecha_devolucion=fila.get("fecha_devolucion"),
            empleado=empleado,
            sucursal=sucursal,
        )
        # Composición: se adjuntan las multas reales desde la BD
        for multa in self._repo_multas.obtener_por_prestamo(fila["id_prestamo"]):
            prestamo._multas.append(multa)
        return prestamo

    def _objeto_a_valores(self, objeto: Prestamo) -> dict:
        return {
            "id_usuario": objeto.usuario.id_usuario,
            "isbn": objeto.libro.isbn,
            "fecha_prestamo": objeto.fecha_prestamo,
            "fecha_devolucion": objeto.fecha_devolucion,
            "id_estado": objeto.estado.id_estado_prestamo,
            "id_empleado": objeto.empleado.id_empleado if objeto.empleado else None,
            "id_sucursal": objeto.sucursal.id_sucursal if objeto.sucursal else None,
        }

    def obtener_activos_por_usuario(self, id_usuario: int) -> list:
        sql = """
            SELECT p.* FROM prestamos p
            INNER JOIN estados_prestamo e ON e.id_estado_prestamo = p.id_estado
            WHERE p.id_usuario = %s AND e.descripcion = 'Activo'
        """
        filas = self.ejecutar_consulta_personalizada(sql, (id_usuario,))
        return [self._fila_a_objeto(fila) for fila in filas]

    def obtener_vencidos(self, fecha_limite: date) -> list:
        """Préstamos activos cuya fecha_prestamo + dias_membresia ya pasó."""
        sql = """
            SELECT p.* FROM prestamos p
            INNER JOIN estados_prestamo e ON e.id_estado_prestamo = p.id_estado
            WHERE e.descripcion = 'Activo' AND p.fecha_prestamo < %s
        """
        filas = self.ejecutar_consulta_personalizada(sql, (fecha_limite,))
        return [self._fila_a_objeto(fila) for fila in filas]

    def registrar_devolucion(self, id_prestamo: int, fecha_devolucion: date, id_estado: int) -> bool:
        sql = "UPDATE prestamos SET fecha_devolucion = %s, id_estado = %s WHERE id_prestamo = %s"
        cursor = self._db.obtener_cursor()
        cursor.execute(sql, (fecha_devolucion, id_estado, id_prestamo))
        afectadas = cursor.rowcount
        self._db.confirmar()
        cursor.close()
        return afectadas > 0
