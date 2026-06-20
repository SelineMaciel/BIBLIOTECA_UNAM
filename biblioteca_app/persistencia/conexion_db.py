"""
persistencia/conexion_db.py
----------------------------
Gestiona la conexión a MySQL mediante el patrón Singleton: sin
importar cuántas veces se solicite una conexión a lo largo de la
aplicación, siempre se reutiliza la misma instancia.

Aquí se aplica ENCAPSULAMIENTO: el atributo que guarda la conexión
real es "privado" (_conexion) y solo se expone a través de métodos
públicos controlados (obtener_cursor, confirmar, cancelar, cerrar).
"""

import mysql.connector
from mysql.connector import MySQLConnection
from config import ConfiguracionBD


class ConexionDB:
    """Singleton que administra una única conexión activa a MySQL."""

    _instancia = None  # referencia única de la clase (patrón Singleton)

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._conexion = None  # atributo "privado"
        return cls._instancia

    # ---------- Métodos públicos (la única forma de tocar la conexión) ----------

    def _conectar(self) -> MySQLConnection:
        """Crea la conexión real si todavía no existe o si se perdió."""
        if self._conexion is None or not self._conexion.is_connected():
            self._conexion = mysql.connector.connect(
                **ConfiguracionBD.como_diccionario()
            )
        return self._conexion

    def obtener_cursor(self, diccionario: bool = True):
        """
        Devuelve un cursor listo para usar.
        diccionario=True hace que cada fila se devuelva como dict
        (nombre_columna -> valor), mucho más cómodo para los modelos.
        """
        conexion = self._conectar()
        return conexion.cursor(dictionary=diccionario)

    def confirmar(self):
        """Hace commit de la transacción actual."""
        if self._conexion:
            self._conexion.commit()

    def cancelar(self):
        """Hace rollback de la transacción actual (en caso de error)."""
        if self._conexion:
            self._conexion.rollback()

    def cerrar(self):
        """Cierra la conexión física (normalmente no se llama en cada request)."""
        if self._conexion and self._conexion.is_connected():
            self._conexion.close()
            self._conexion = None

    def probar_conexion(self) -> bool:
        """Utilidad simple para verificar que la BD responde."""
        try:
            cursor = self.obtener_cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except mysql.connector.Error as error:
            print(f"[ConexionDB] Error al conectar: {error}")
            return False
