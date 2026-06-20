"""
controladores/prestamos_controller.py
--------------------------------------------
Envuelve ServicioPrestamos para la capa web: listados, formularios y
registro de préstamos/devoluciones.
"""

from persistencia.repositorio_prestamos import RepositorioPrestamos
from persistencia.repositorio_personas import RepositorioUsuarios
from persistencia.repositorio_libros import RepositorioLibros
from persistencia.repositorio_membresias import RepositorioSucursales
from servicios.servicio_prestamos import ServicioPrestamos, PrestamoNoPermitidoError


class PrestamosController:
    def __init__(self):
        self._repo_prestamos = RepositorioPrestamos()
        self._repo_usuarios = RepositorioUsuarios()
        self._repo_libros = RepositorioLibros()
        self._repo_sucursales = RepositorioSucursales()
        self._servicio_prestamos = ServicioPrestamos()

    def listar(self) -> list:
        return self._repo_prestamos.obtener_todos(orden="id_prestamo DESC")

    def obtener(self, id_prestamo: int):
        return self._repo_prestamos.obtener_por_id(id_prestamo)

    def opciones_usuario(self) -> list:
        return [(u.id_usuario, f"{u.nombre} ({u.email})") for u in self._repo_usuarios.obtener_todos_completo()]

    def opciones_libro_disponible(self) -> list:
        return [(l.isbn, f"{l.titulo} - {l.isbn}") for l in self._repo_libros.buscar_disponibles()]

    def opciones_sucursal(self) -> list:
        return [(s.id_sucursal, s.nombre) for s in self._repo_sucursales.obtener_todos(orden="id_sucursal")]

    def registrar_prestamo(self, id_usuario: int, isbn: str, id_sucursal: int, id_empleado: int = None) -> dict:
        try:
            id_prestamo = self._servicio_prestamos.crear_prestamo(id_usuario, isbn, id_sucursal, id_empleado)
            return {"exito": True, "id_prestamo": id_prestamo, "mensaje": "Préstamo registrado correctamente."}
        except PrestamoNoPermitidoError as e:
            return {"exito": False, "mensaje": str(e)}

    def registrar_devolucion(self, id_prestamo: int) -> dict:
        try:
            self._servicio_prestamos.registrar_devolucion(id_prestamo)
            return {"exito": True, "mensaje": "Devolución registrada correctamente."}
        except PrestamoNoPermitidoError as e:
            return {"exito": False, "mensaje": str(e)}
