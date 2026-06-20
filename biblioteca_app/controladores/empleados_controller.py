"""
controladores/empleados_controller.py
--------------------------------------------
CRUD completo de Empleado.
"""

from persistencia.repositorio_personas import RepositorioEmpleados
from persistencia.repositorio_membresias import RepositorioSucursales


class EmpleadosController:
    def __init__(self):
        self._repo_empleados = RepositorioEmpleados()
        self._repo_sucursales = RepositorioSucursales()

    def listar(self) -> list:
        return self._repo_empleados.obtener_todos_completo()

    def obtener(self, id_empleado: int):
        return self._repo_empleados.obtener_por_id_completo(id_empleado)

    def opciones_sucursal(self) -> list:
        return [(s.id_sucursal, s.nombre) for s in self._repo_sucursales.obtener_todos(orden="id_sucursal")]

    def crear(self, datos: dict) -> int:
        existente = self._repo_empleados.obtener_por_email(datos["email"])
        if existente is not None:
            raise ValueError("Ya existe un empleado registrado con ese correo.")
        persona_datos = {"nombre": datos["nombre"], "email": datos["email"], "phone": datos.get("phone")}
        return self._repo_empleados.crear_completo(persona_datos, datos["cargo"], datos["id_sucursal"])

    def actualizar(self, id_empleado: int, datos: dict) -> bool:
        actual = self._repo_empleados.obtener_por_id_completo(id_empleado)
        if actual is None:
            return False
        cursor = self._repo_empleados._db.obtener_cursor()
        try:
            cursor.execute(
                "UPDATE personas SET nombre = %s, email = %s, phone = %s WHERE id_persona = %s",
                (datos["nombre"], datos["email"], datos.get("phone"), actual.id_persona),
            )
            cursor.execute(
                "UPDATE empleados SET cargo = %s, id_sucursal = %s WHERE id_empleado = %s",
                (datos["cargo"], datos["id_sucursal"], id_empleado),
            )
            self._repo_empleados._db.confirmar()
            return True
        except Exception:
            self._repo_empleados._db.cancelar()
            raise
        finally:
            cursor.close()

    def eliminar(self, id_empleado: int) -> bool:
        actual = self._repo_empleados.obtener_por_id_completo(id_empleado)
        if actual is None:
            return False
        cursor = self._repo_empleados._db.obtener_cursor()
        try:
            cursor.execute("DELETE FROM empleados WHERE id_empleado = %s", (id_empleado,))
            cursor.execute("DELETE FROM personas WHERE id_persona = %s", (actual.id_persona,))
            self._repo_empleados._db.confirmar()
            return True
        except Exception:
            self._repo_empleados._db.cancelar()
            raise
        finally:
            cursor.close()
