"""
modelos/rol.py
---------------
Define Rol y Permiso. Se relacionan muchos-a-muchos (un Rol agrega
una lista de Permiso). Esto es AGREGACIÓN: un Permiso puede seguir
existiendo aunque se elimine el Rol que lo tenía asignado.
"""


class Permiso:
    """Representa un permiso individual del sistema (ENCAPSULAMIENTO)."""

    def __init__(self, id_permiso: int, nombre_permiso: str, descripcion: str = ""):
        self._id_permiso = id_permiso
        self._nombre_permiso = nombre_permiso
        self._descripcion = descripcion

    @property
    def id_permiso(self) -> int:
        return self._id_permiso

    @property
    def nombre_permiso(self) -> str:
        return self._nombre_permiso

    @property
    def descripcion(self) -> str:
        return self._descripcion

    def __repr__(self):
        return f"Permiso({self._id_permiso}, '{self._nombre_permiso}')"

    def __eq__(self, otro):
        return isinstance(otro, Permiso) and self._id_permiso == otro._id_permiso

    def __hash__(self):
        return hash(self._id_permiso)


class Rol:
    """
    Representa un rol (Administrador, Empleado, Usuario).
    AGREGACIÓN: un Rol mantiene una lista de objetos Permiso, pero
    esos permisos existen de forma independiente en la tabla `permisos`.
    """

    def __init__(self, id_rol: int, nombre_rol: str, descripcion: str = ""):
        self._id_rol = id_rol
        self._nombre_rol = nombre_rol
        self._descripcion = descripcion
        self._permisos: list[Permiso] = []  # lista agregada, vacía hasta que se cargue

    # ---------------- Propiedades (encapsulamiento) ----------------

    @property
    def id_rol(self) -> int:
        return self._id_rol

    @property
    def nombre_rol(self) -> str:
        return self._nombre_rol

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @property
    def permisos(self) -> list:
        """Devuelve una copia para que nadie modifique la lista interna directamente."""
        return list(self._permisos)

    # ---------------- Comportamiento ----------------

    def agregar_permiso(self, permiso: Permiso):
        if permiso not in self._permisos:
            self._permisos.append(permiso)

    def tiene_permiso(self, nombre_permiso: str) -> bool:
        return any(p.nombre_permiso == nombre_permiso for p in self._permisos)

    def __repr__(self):
        return f"Rol({self._id_rol}, '{self._nombre_rol}')"
