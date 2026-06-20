"""
controladores/reservas_controller.py
--------------------------------------------
Envuelve ServicioReservas para la capa web.
"""

from persistencia.repositorio_reservas import RepositorioReservas
from persistencia.repositorio_personas import RepositorioUsuarios
from persistencia.repositorio_libros import RepositorioLibros
from persistencia.repositorio_membresias import RepositorioSucursales
from servicios.servicio_reservas import ServicioReservas, ReservaNoPermitidaError


class ReservasController:
    def __init__(self):
        self._repo_reservas = RepositorioReservas()
        self._repo_usuarios = RepositorioUsuarios()
        self._repo_libros = RepositorioLibros()
        self._repo_sucursales = RepositorioSucursales()
        self._servicio_reservas = ServicioReservas()

    def listar(self) -> list:
        return self._repo_reservas.obtener_todos(orden="id_reserva DESC")

    def opciones_usuario(self) -> list:
        return [(u.id_usuario, f"{u.nombre} ({u.email})") for u in self._repo_usuarios.obtener_todos_completo()]

    def opciones_libro(self) -> list:
        return [(l.isbn, f"{l.titulo} - {l.isbn}") for l in self._repo_libros.obtener_todos(orden="titulo")]

    def opciones_sucursal(self) -> list:
        return [(s.id_sucursal, s.nombre) for s in self._repo_sucursales.obtener_todos(orden="id_sucursal")]

    def crear_reserva(self, id_usuario: int, isbn: str, id_sucursal: int) -> dict:
        try:
            id_reserva = self._servicio_reservas.crear_reserva(id_usuario, isbn, id_sucursal)
            return {"exito": True, "id_reserva": id_reserva, "mensaje": "Reserva creada correctamente."}
        except ReservaNoPermitidaError as e:
            return {"exito": False, "mensaje": str(e)}

    def confirmar(self, id_reserva: int) -> bool:
        return self._servicio_reservas.confirmar_reserva(id_reserva)

    def cancelar(self, id_reserva: int) -> bool:
        return self._servicio_reservas.cancelar_reserva(id_reserva)
