"""
controladores/auth_controller.py
--------------------------------------
Orquesta el login: recibe credenciales ya validadas por el formulario
y decide a qué servicio delegar (ServicioAuth), y qué guardar en la
sesión Flask a través de utilitarios/sesion.py.
"""

from servicios.servicio_auth import ServicioAuth, CredencialesInvalidasError
from utilitarios.sesion import guardar_sesion


class AuthController:
    def __init__(self):
        self._servicio_auth = ServicioAuth()

    def procesar_login(self, email: str, password: str = None) -> dict:
        """
        Intenta loguear, en este orden: AdminUser (requiere password),
        Empleado (sin password), Usuario (sin password).
        Devuelve {"exito": bool, "mensaje": str, "panel": str (si exito)}.
        """
        # 1) Intentar como AdminUser si se proporcionó password
        if password:
            admin = self._servicio_auth._repo_admins.obtener_por_admin_user(email) \
                if "@" not in email else None
            # admin_user normalmente no es un email; igualmente probamos por
            # email también, en caso de que el admin haya ingresado su correo.
            admin_por_email = None
            try:
                admin_por_email = self._buscar_admin_por_email(email)
            except Exception:
                admin_por_email = None

            candidato_admin = admin or admin_por_email
            if candidato_admin is not None:
                from werkzeug.security import check_password_hash
                if check_password_hash(candidato_admin._password_hash, password):
                    guardar_sesion("admin", candidato_admin.id_admin, candidato_admin.nombre)
                    return {"exito": True, "mensaje": "Bienvenido, administrador.", "panel": "admin.dashboard"}
                else:
                    return {"exito": False, "mensaje": "Contraseña incorrecta para esa cuenta de administrador."}

        # 2) Intentar como Empleado (sin password)
        empleado = self._servicio_auth._repo_empleados.obtener_por_email(email)
        if empleado is not None:
            guardar_sesion("empleado", empleado.id_empleado, empleado.nombre)
            return {"exito": True, "mensaje": f"Bienvenido, {empleado.nombre}.", "panel": "empleado.dashboard"}

        # 3) Intentar como Usuario (sin password)
        usuario = self._servicio_auth._repo_usuarios.obtener_por_email(email)
        if usuario is not None:
            guardar_sesion("usuario", usuario.id_usuario, usuario.nombre)
            return {"exito": True, "mensaje": f"Bienvenido, {usuario.nombre}.", "panel": "usuario.dashboard"}

        return {"exito": False, "mensaje": "No se encontró ninguna cuenta con ese correo."}

    def _buscar_admin_por_email(self, email: str):
        sql = """
            SELECT a.id_admin, a.admin_user, a.password_hash, a.id_rol,
                   p.id_persona, p.nombre, p.email, p.phone
            FROM admin_users a
            INNER JOIN personas p ON p.id_persona = a.id_persona
            WHERE p.email = %s
        """
        filas = self._servicio_auth._repo_admins.ejecutar_consulta_personalizada(sql, (email,))
        return self._servicio_auth._repo_admins._fila_a_objeto(filas[0]) if filas else None
