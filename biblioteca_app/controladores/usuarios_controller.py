"""
controladores/usuarios_controller.py
------------------------------------------
CRUD completo de Usuario, más los datos auxiliares necesarios para
poblar los SelectField del formulario (membresías, roles).
"""

from persistencia.repositorio_personas import RepositorioUsuarios
from persistencia.repositorio_membresias import RepositorioMembresias
from persistencia.repositorio_roles import RepositorioRoles


class EmailDuplicadoError(Exception):
    pass


class UsuariosController:
    def __init__(self):
        self._repo_usuarios = RepositorioUsuarios()
        self._repo_membresias = RepositorioMembresias()
        self._repo_roles = RepositorioRoles()

    def listar(self, texto_busqueda: str = None) -> list:
        if texto_busqueda:
            return self._repo_usuarios.buscar_por_nombre(texto_busqueda)
        return self._repo_usuarios.obtener_todos_completo()

    def obtener(self, id_usuario: int):
        return self._repo_usuarios.obtener_por_id_completo(id_usuario)

    def opciones_membresia(self) -> list:
        """[(id, etiqueta), ...] para el SelectField."""
        return [(m.id_membresia, f"{m.tipo_membresia} (máx {m.max_prestamos}, {m.dias_prestamo} días)")
                for m in self._repo_membresias.obtener_todos(orden="id_membresia")]

    def opciones_rol(self) -> list:
        return [(r.id_rol, r.nombre_rol) for r in self._repo_roles.obtener_todos(orden="id_rol")]

    def crear(self, datos: dict) -> int:
        existente = self._repo_usuarios.obtener_por_email(datos["email"])
        if existente is not None:
            raise EmailDuplicadoError("Ya existe una persona registrada con ese correo.")

        persona_datos = {"nombre": datos["nombre"], "email": datos["email"], "phone": datos.get("phone")}
        return self._repo_usuarios.crear_completo(
            persona_datos, datos.get("edad"), datos["id_membresia"], datos["id_rol"]
        )

    def actualizar(self, id_usuario: int, datos: dict) -> bool:
        actual = self._repo_usuarios.obtener_por_id_completo(id_usuario)
        if actual is None:
            return False

        # Si cambió el email, validar que no choque con otra persona
        if datos["email"] != actual.email:
            existente = self._repo_usuarios.obtener_por_email(datos["email"])
            if existente is not None:
                raise EmailDuplicadoError("Ese correo ya está en uso por otra cuenta.")

        persona_datos = {"nombre": datos["nombre"], "email": datos["email"], "phone": datos.get("phone")}
        return self._repo_usuarios.actualizar_completo(
            id_usuario, persona_datos, datos.get("edad"), datos["id_membresia"], datos["id_rol"]
        )

    def eliminar(self, id_usuario: int) -> bool:
        return self._repo_usuarios.eliminar_completo(id_usuario)
