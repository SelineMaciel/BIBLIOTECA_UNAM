"""
persistencia/repositorio_personas.py
----------------------------------------
Repositorios concretos para las 3 subclases de Persona: Usuario,
Empleado y AdminUser. Cada uno se encarga de:
  1) Leer/escribir la fila de `personas` (datos heredados).
  2) Leer/escribir la fila de su propia tabla (usuarios/empleados/admin_users).
  3) Ensamblar los objetos asociados (Rol, Membresia, Sucursal) para
     construir el objeto de dominio completo.

Esto refleja en código el hecho de que en la BD la herencia se modela
como tablas separadas relacionadas por id_persona (estrategia clásica
de "Class Table Inheritance").
"""

from persistencia.repositorio_base import RepositorioBase
from persistencia.repositorio_roles import RepositorioRoles
from persistencia.repositorio_membresias import RepositorioMembresias, RepositorioSucursales
from modelos.persona import Usuario, Empleado, AdminUser


class RepositorioUsuarios(RepositorioBase):
    def __init__(self):
        super().__init__(nombre_tabla="usuarios", columnas_pk="id_usuario")
        self._repo_roles = RepositorioRoles()
        self._repo_membresias = RepositorioMembresias()

    def _fila_a_objeto(self, fila: dict) -> Usuario:
        rol = self._repo_roles.obtener_con_permisos(fila["id_rol"])
        membresia = self._repo_membresias.obtener_por_id(fila["id_membresia"])
        return Usuario(
            id_persona=fila["id_persona"],
            nombre=fila["nombre"],
            email=fila["email"],
            phone=fila.get("phone"),
            id_usuario=fila["id_usuario"],
            edad=fila.get("edad"),
            membresia=membresia,
            rol=rol,
        )

    def _objeto_a_valores(self, objeto: Usuario) -> dict:
        return {
            "id_persona": objeto.id_persona,
            "edad": objeto.edad,
            "id_membresia": objeto.membresia.id_membresia,
            "id_rol": objeto.rol.id_rol,
        }

    # ---------------- Consultas completas (JOIN con personas) ----------------

    def obtener_todos_completo(self) -> list:
        sql = """
            SELECT u.id_usuario, u.edad, u.id_membresia, u.id_rol,
                   p.id_persona, p.nombre, p.email, p.phone
            FROM usuarios u
            INNER JOIN personas p ON p.id_persona = u.id_persona
            ORDER BY u.id_usuario
        """
        filas = self.ejecutar_consulta_personalizada(sql)
        return [self._fila_a_objeto(fila) for fila in filas]

    def obtener_por_id_completo(self, id_usuario: int) -> Usuario:
        sql = """
            SELECT u.id_usuario, u.edad, u.id_membresia, u.id_rol,
                   p.id_persona, p.nombre, p.email, p.phone
            FROM usuarios u
            INNER JOIN personas p ON p.id_persona = u.id_persona
            WHERE u.id_usuario = %s
        """
        filas = self.ejecutar_consulta_personalizada(sql, (id_usuario,))
        return self._fila_a_objeto(filas[0]) if filas else None

    def obtener_por_email(self, email: str) -> Usuario:
        sql = """
            SELECT u.id_usuario, u.edad, u.id_membresia, u.id_rol,
                   p.id_persona, p.nombre, p.email, p.phone
            FROM usuarios u
            INNER JOIN personas p ON p.id_persona = u.id_persona
            WHERE p.email = %s
        """
        filas = self.ejecutar_consulta_personalizada(sql, (email,))
        return self._fila_a_objeto(filas[0]) if filas else None

    def buscar_por_nombre(self, texto_busqueda: str) -> list:
        sql = """
            SELECT u.id_usuario, u.edad, u.id_membresia, u.id_rol,
                   p.id_persona, p.nombre, p.email, p.phone
            FROM usuarios u
            INNER JOIN personas p ON p.id_persona = u.id_persona
            WHERE p.nombre LIKE %s
            ORDER BY p.nombre
        """
        filas = self.ejecutar_consulta_personalizada(sql, (f"%{texto_busqueda}%",))
        return [self._fila_a_objeto(fila) for fila in filas]

    def crear_completo(self, persona_datos: dict, edad: int, id_membresia: int, id_rol: int) -> int:
        """
        Crea primero la fila en `personas` y luego en `usuarios`,
        dentro de la misma transacción lógica.
        persona_datos = {"nombre": ..., "email": ..., "phone": ...}
        """
        cursor = self._db.obtener_cursor()
        try:
            cursor.execute(
                "INSERT INTO personas (nombre, email, phone) VALUES (%s, %s, %s)",
                (persona_datos["nombre"], persona_datos["email"], persona_datos.get("phone")),
            )
            id_persona = cursor.lastrowid

            cursor.execute(
                "INSERT INTO usuarios (id_persona, edad, id_membresia, id_rol) VALUES (%s, %s, %s, %s)",
                (id_persona, edad, id_membresia, id_rol),
            )
            id_usuario = cursor.lastrowid

            self._db.confirmar()
            return id_usuario
        except Exception:
            self._db.cancelar()
            raise
        finally:
            cursor.close()

    def actualizar_completo(self, id_usuario: int, persona_datos: dict, edad: int, id_membresia: int, id_rol: int) -> bool:
        fila_actual = self._obtener_fila_cruda(id_usuario)
        if fila_actual is None:
            return False

        cursor = self._db.obtener_cursor()
        try:
            cursor.execute(
                "UPDATE personas SET nombre = %s, email = %s, phone = %s WHERE id_persona = %s",
                (persona_datos["nombre"], persona_datos["email"], persona_datos.get("phone"), fila_actual["id_persona"]),
            )
            cursor.execute(
                "UPDATE usuarios SET edad = %s, id_membresia = %s, id_rol = %s WHERE id_usuario = %s",
                (edad, id_membresia, id_rol, id_usuario),
            )
            self._db.confirmar()
            return True
        except Exception:
            self._db.cancelar()
            raise
        finally:
            cursor.close()

    def eliminar_completo(self, id_usuario: int) -> bool:
        """Elimina usuario y su persona base (si no tiene registros dependientes)."""
        fila_actual = self._obtener_fila_cruda(id_usuario)
        if fila_actual is None:
            return False
        id_persona = fila_actual["id_persona"]

        cursor = self._db.obtener_cursor()
        try:
            cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))
            cursor.execute("DELETE FROM personas WHERE id_persona = %s", (id_persona,))
            self._db.confirmar()
            return True
        except Exception:
            self._db.cancelar()
            raise
        finally:
            cursor.close()

    def _obtener_fila_cruda(self, id_usuario: int) -> dict:
        """Devuelve la fila tal cual está en `usuarios`, sin ensamblar
        objetos relacionados (útil cuando solo se necesita id_persona)."""
        filas = self.ejecutar_consulta_personalizada(
            "SELECT * FROM usuarios WHERE id_usuario = %s", (id_usuario,)
        )
        return filas[0] if filas else None


class RepositorioEmpleados(RepositorioBase):
    def __init__(self):
        super().__init__(nombre_tabla="empleados", columnas_pk="id_empleado")
        self._repo_sucursales = RepositorioSucursales()

    def _fila_a_objeto(self, fila: dict) -> Empleado:
        sucursal = self._repo_sucursales.obtener_por_id(fila["id_sucursal"])
        return Empleado(
            id_persona=fila["id_persona"],
            nombre=fila["nombre"],
            email=fila["email"],
            phone=fila.get("phone"),
            id_empleado=fila["id_empleado"],
            cargo=fila["cargo"],
            sucursal=sucursal,
        )

    def _objeto_a_valores(self, objeto: Empleado) -> dict:
        return {
            "id_persona": objeto.id_persona,
            "cargo": objeto.cargo,
            "id_sucursal": objeto.sucursal.id_sucursal,
        }

    def obtener_todos_completo(self) -> list:
        sql = """
            SELECT e.id_empleado, e.cargo, e.id_sucursal,
                   p.id_persona, p.nombre, p.email, p.phone
            FROM empleados e
            INNER JOIN personas p ON p.id_persona = e.id_persona
            ORDER BY e.id_empleado
        """
        filas = self.ejecutar_consulta_personalizada(sql)
        return [self._fila_a_objeto(fila) for fila in filas]

    def obtener_por_id_completo(self, id_empleado: int) -> Empleado:
        sql = """
            SELECT e.id_empleado, e.cargo, e.id_sucursal,
                   p.id_persona, p.nombre, p.email, p.phone
            FROM empleados e
            INNER JOIN personas p ON p.id_persona = e.id_persona
            WHERE e.id_empleado = %s
        """
        filas = self.ejecutar_consulta_personalizada(sql, (id_empleado,))
        return self._fila_a_objeto(filas[0]) if filas else None

    def obtener_por_email(self, email: str) -> Empleado:
        sql = """
            SELECT e.id_empleado, e.cargo, e.id_sucursal,
                   p.id_persona, p.nombre, p.email, p.phone
            FROM empleados e
            INNER JOIN personas p ON p.id_persona = e.id_persona
            WHERE p.email = %s
        """
        filas = self.ejecutar_consulta_personalizada(sql, (email,))
        return self._fila_a_objeto(filas[0]) if filas else None

    def crear_completo(self, persona_datos: dict, cargo: str, id_sucursal: int) -> int:
        cursor = self._db.obtener_cursor()
        try:
            cursor.execute(
                "INSERT INTO personas (nombre, email, phone) VALUES (%s, %s, %s)",
                (persona_datos["nombre"], persona_datos["email"], persona_datos.get("phone")),
            )
            id_persona = cursor.lastrowid
            cursor.execute(
                "INSERT INTO empleados (id_persona, cargo, id_sucursal) VALUES (%s, %s, %s)",
                (id_persona, cargo, id_sucursal),
            )
            id_empleado = cursor.lastrowid
            self._db.confirmar()
            return id_empleado
        except Exception:
            self._db.cancelar()
            raise
        finally:
            cursor.close()


class RepositorioAdminUsers(RepositorioBase):
    def __init__(self):
        super().__init__(nombre_tabla="admin_users", columnas_pk="id_admin")
        self._repo_roles = RepositorioRoles()

    def _fila_a_objeto(self, fila: dict) -> AdminUser:
        rol = self._repo_roles.obtener_con_permisos(fila["id_rol"])
        return AdminUser(
            id_persona=fila["id_persona"],
            nombre=fila["nombre"],
            email=fila["email"],
            phone=fila.get("phone"),
            id_admin=fila["id_admin"],
            admin_user=fila["admin_user"],
            password_hash=fila["password_hash"],
            rol=rol,
        )

    def _objeto_a_valores(self, objeto: AdminUser) -> dict:
        return {
            "id_persona": objeto.id_persona,
            "admin_user": objeto.admin_user,
            "password_hash": objeto._password_hash,
            "id_rol": objeto.rol.id_rol,
        }

    def obtener_por_admin_user(self, admin_user: str) -> AdminUser:
        sql = """
            SELECT a.id_admin, a.admin_user, a.password_hash, a.id_rol,
                   p.id_persona, p.nombre, p.email, p.phone
            FROM admin_users a
            INNER JOIN personas p ON p.id_persona = a.id_persona
            WHERE a.admin_user = %s
        """
        filas = self.ejecutar_consulta_personalizada(sql, (admin_user,))
        return self._fila_a_objeto(filas[0]) if filas else None

    def obtener_por_id_completo(self, id_admin: int) -> AdminUser:
        """
        Versión con JOIN contra `personas`, necesaria porque AdminUser
        hereda nombre/email/phone de Persona y esas columnas no viven
        en `admin_users`. Se usa, por ejemplo, al reconstruir la
        sesión desde utilitarios/sesion.py.
        """
        sql = """
            SELECT a.id_admin, a.admin_user, a.password_hash, a.id_rol,
                   p.id_persona, p.nombre, p.email, p.phone
            FROM admin_users a
            INNER JOIN personas p ON p.id_persona = a.id_persona
            WHERE a.id_admin = %s
        """
        filas = self.ejecutar_consulta_personalizada(sql, (id_admin,))
        return self._fila_a_objeto(filas[0]) if filas else None

    def obtener_todos_completo(self) -> list:
        sql = """
            SELECT a.id_admin, a.admin_user, a.password_hash, a.id_rol,
                   p.id_persona, p.nombre, p.email, p.phone
            FROM admin_users a
            INNER JOIN personas p ON p.id_persona = a.id_persona
            ORDER BY a.id_admin
        """
        filas = self.ejecutar_consulta_personalizada(sql)
        return [self._fila_a_objeto(fila) for fila in filas]

    def crear_completo(self, persona_datos: dict, admin_user: str, password_hash: str, id_rol: int) -> int:
        cursor = self._db.obtener_cursor()
        try:
            cursor.execute(
                "INSERT INTO personas (nombre, email, phone) VALUES (%s, %s, %s)",
                (persona_datos["nombre"], persona_datos["email"], persona_datos.get("phone")),
            )
            id_persona = cursor.lastrowid
            cursor.execute(
                "INSERT INTO admin_users (id_persona, admin_user, password_hash, id_rol) VALUES (%s, %s, %s, %s)",
                (id_persona, admin_user, password_hash, id_rol),
            )
            id_admin = cursor.lastrowid
            self._db.confirmar()
            return id_admin
        except Exception:
            self._db.cancelar()
            raise
        finally:
            cursor.close()
