"""
modelos/persona.py
--------------------
Núcleo de la HERENCIA del proyecto.

Persona es una clase ABSTRACTA (no se puede instanciar directamente,
no representa a nadie real por sí sola: siempre es un Usuario, un
Empleado o un AdminUser). Usuario, Empleado y AdminUser heredan los
atributos comunes (nombre, email, telefono) y cada una agrega lo
propio de su rol en el sistema.

POLIMORFISMO: las tres subclases sobreescriben tiene_acceso() y
panel(). El código que llama a estos métodos (por ejemplo en
servicios/servicio_permisos.py) no necesita saber qué subclase
recibió: simplemente llama persona.tiene_acceso(...) y cada clase
responde según su propia lógica.
"""

from abc import ABC, abstractmethod


class Persona(ABC):
    """Clase base abstracta para Usuario, Empleado y AdminUser."""

    def __init__(self, id_persona: int, nombre: str, email: str, phone: str = None):
        self._id_persona = id_persona
        self._nombre = nombre
        self._email = email
        self._phone = phone

    # ---------------- Encapsulamiento: solo acceso vía properties ----------------

    @property
    def id_persona(self) -> int:
        return self._id_persona

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not valor.strip():
            raise ValueError("El nombre no puede estar vacío")
        self._nombre = valor.strip()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str):
        if "@" not in valor:
            raise ValueError("Email inválido")
        self._email = valor

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, valor: str):
        self._phone = valor

    # ---------------- Métodos abstractos: cada subclase los define a su manera ----------------

    @abstractmethod
    def tiene_acceso(self, nombre_permiso: str) -> bool:
        """¿Esta persona puede ejecutar la acción asociada a este permiso?"""
        raise NotImplementedError

    @abstractmethod
    def panel(self) -> str:
        """Nombre/identificador del panel o vista principal que le corresponde."""
        raise NotImplementedError

    def __repr__(self):
        return f"{self.__class__.__name__}({self._id_persona}, '{self._nombre}')"


class Usuario(Persona):
    """
    Usuario final de la biblioteca (lector). Hereda de Persona y
    agrega edad, membresía y rol propios de su contexto.
    ASOCIACIÓN: Usuario se asocia con Membresia y Rol (no los agrega,
    no los "posee"; simplemente referencia un tipo compartido).
    """

    def __init__(
        self,
        id_persona: int,
        nombre: str,
        email: str,
        phone: str,
        id_usuario: int,
        edad: int,
        membresia,   # objeto Membresia (asociación)
        rol,         # objeto Rol (asociación)
    ):
        super().__init__(id_persona, nombre, email, phone)
        self._id_usuario = id_usuario
        self._edad = edad
        self._membresia = membresia
        self._rol = rol
        self._historial_prestamos = []  # agregación: lista de Prestamo

    @property
    def id_usuario(self) -> int:
        return self._id_usuario

    @property
    def edad(self) -> int:
        return self._edad

    @property
    def membresia(self):
        return self._membresia

    @property
    def rol(self):
        return self._rol

    @property
    def historial_prestamos(self) -> list:
        return list(self._historial_prestamos)

    def agregar_prestamo(self, prestamo):
        self._historial_prestamos.append(prestamo)

    def puede_solicitar_prestamo(self) -> bool:
        """Regla de negocio propia de Usuario: depende de su membresía."""
        activos = [p for p in self._historial_prestamos if not p.fue_devuelto()]
        return len(activos) < self._membresia.max_prestamos

    # ---------------- Polimorfismo ----------------

    def tiene_acceso(self, nombre_permiso: str) -> bool:
        return self._rol.tiene_permiso(nombre_permiso)

    def panel(self) -> str:
        return "panel_usuario"


class Empleado(Persona):
    """
    Empleado de una sucursal (bibliotecario). Hereda de Persona y
    agrega cargo y sucursal asignada.
    ASOCIACIÓN: Empleado se asocia con Sucursal.
    """

    def __init__(
        self,
        id_persona: int,
        nombre: str,
        email: str,
        phone: str,
        id_empleado: int,
        cargo: str,
        sucursal,  # objeto Sucursal (asociación)
    ):
        super().__init__(id_persona, nombre, email, phone)
        self._id_empleado = id_empleado
        self._cargo = cargo
        self._sucursal = sucursal

    @property
    def id_empleado(self) -> int:
        return self._id_empleado

    @property
    def cargo(self) -> str:
        return self._cargo

    @property
    def sucursal(self):
        return self._sucursal

    # Empleado no tiene rol propio en la tabla `empleados` del esquema actual;
    # su acceso se modela como fijo a las operaciones diarias de biblioteca.
    # ---------------- Polimorfismo ----------------

    def tiene_acceso(self, nombre_permiso: str) -> bool:
        permisos_empleado = {
            "registrar_prestamo",
            "registrar_devolucion",
            "consultar_catalogo",
            "hacer_reserva",
        }
        return nombre_permiso in permisos_empleado

    def panel(self) -> str:
        return "panel_empleado"


class AdminUser(Persona):
    """
    Administrador del sistema. Hereda de Persona y agrega credenciales
    propias (admin_user, password_hash) y un Rol asociado.
    """

    def __init__(
        self,
        id_persona: int,
        nombre: str,
        email: str,
        phone: str,
        id_admin: int,
        admin_user: str,
        password_hash: str,
        rol,  # objeto Rol (asociación)
    ):
        super().__init__(id_persona, nombre, email, phone)
        self._id_admin = id_admin
        self._admin_user = admin_user
        self._password_hash = password_hash
        self._rol = rol

    @property
    def id_admin(self) -> int:
        return self._id_admin

    @property
    def admin_user(self) -> str:
        return self._admin_user

    @property
    def rol(self):
        return self._rol

    def verificar_password(self, password_plano: str, verificador) -> bool:
        """
        verificador es una función/objeto inyectado (por ejemplo
        werkzeug.security.check_password_hash) para no acoplar este
        modelo a una librería específica de hashing.
        """
        return verificador(self._password_hash, password_plano)

    # ---------------- Polimorfismo ----------------

    def tiene_acceso(self, nombre_permiso: str) -> bool:
        # El administrador hereda del Rol "Administrador", que en los
        # datos iniciales tiene TODOS los permisos asignados.
        return self._rol.tiene_permiso(nombre_permiso)

    def panel(self) -> str:
        return "panel_admin"
