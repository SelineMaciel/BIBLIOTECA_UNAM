"""
servicios/servicio_auth.py
-----------------------------
Lógica de negocio de autenticación. No conoce Flask ni HTTP: solo
recibe credenciales y devuelve un objeto Persona (Usuario, Empleado
o AdminUser) o None si las credenciales no son válidas.

POLIMORFISMO: el resultado de iniciar_sesion() puede ser cualquier
subclase de Persona; el código que lo use (controladores/vistas)
llama persona.tiene_acceso(...) o persona.panel() sin necesitar
saber de cuál subclase se trata.

Seguridad: las contraseñas NUNCA se comparan en texto plano. Se usa
werkzeug.security (la misma librería que trae Flask) para hashear
y verificar.
"""

from werkzeug.security import generate_password_hash, check_password_hash

from persistencia.repositorio_personas import (
    RepositorioUsuarios,
    RepositorioEmpleados,
    RepositorioAdminUsers,
)


class CredencialesInvalidasError(Exception):
    """Se lanza cuando el login falla (usuario no existe o password incorrecta)."""
    pass


class ServicioAuth:
    def __init__(self):
        self._repo_usuarios = RepositorioUsuarios()
        self._repo_empleados = RepositorioEmpleados()
        self._repo_admins = RepositorioAdminUsers()

    # ---------------- Hashing de contraseñas (solo aplica a AdminUser) ----------------

    @staticmethod
    def hashear_password(password_plano: str) -> str:
        return generate_password_hash(password_plano)

    # ---------------- Login ----------------

    def iniciar_sesion_admin(self, admin_user: str, password_plano: str):
        """Devuelve un AdminUser autenticado o lanza CredencialesInvalidasError."""
        admin = self._repo_admins.obtener_por_admin_user(admin_user)
        if admin is None:
            raise CredencialesInvalidasError("Usuario administrador no encontrado")

        if not check_password_hash(admin._password_hash, password_plano):
            raise CredencialesInvalidasError("Contraseña incorrecta")

        return admin

    def iniciar_sesion_por_email(self, email: str, password_plano: str = None):
        """
        Busca primero entre Usuarios y luego entre Empleados por email.
        En este esquema, Usuario y Empleado no tienen password propio
        (el control de acceso de ellos lo gestiona el Administrador o
        Empleado que los registra); por eso este método se usa
        principalmente para btener el objeto de sesión de un Usuario
        que ya fue autenticado por otro medio (ej. sesión iniciada por
        un empleado en mostrador). Para AdminUser siempre se exige
        password mediante iniciar_sesion_admin().
        """
        usuario = self._repo_usuarios.obtener_por_email(email)
        if usuario is not None:
            return usuario

        empleado = self._repo_empleados.obtener_por_email(email)
        if empleado is not None:
            return empleado

        raise CredencialesInvalidasError("No existe una cuenta con ese correo")

    def registrar_admin(self, nombre: str, email: str, phone: str, admin_user: str, password_plano: str, id_rol: int) -> int:
        password_hash = self.hashear_password(password_plano)
        persona_datos = {"nombre": nombre, "email": email, "phone": phone}
        return self._repo_admins.crear_completo(persona_datos, admin_user, password_hash, id_rol)
