"""
config.py
----------
Configuración centralizada del proyecto. Aquí viven los parámetros
de conexión a la base de datos y otras claves/ajustes globales.

No se importa ningún framework web aquí: este módulo debe poder
usarse tanto desde scripts de prueba como desde la app Flask.
"""

import os


class ConfiguracionBD:
    """Parámetros de conexión a MySQL (XAMPP)."""
    HOST = os.environ.get("DB_HOST", "127.0.0.1")
    PUERTO = int(os.environ.get("DB_PORT", 3306))
    USUARIO = os.environ.get("DB_USER", "root")
    PASSWORD = os.environ.get("DB_PASSWORD", "")  # XAMPP por defecto: vacío
    BASE_DATOS = os.environ.get("DB_NAME", "biblioteca1")

    @classmethod
    def como_diccionario(cls) -> dict:
        """Devuelve los parámetros en el formato que espera
        mysql.connector.connect(**kwargs)."""
        return {
            "host": cls.HOST,
            "port": cls.PUERTO,
            "user": cls.USUARIO,
            "password": cls.PASSWORD,
            "database": cls.BASE_DATOS,
        }


class ConfiguracionApp:
    """Configuración general de la aplicación Flask (se usará en Fase 4)."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-secreta-cambiar-en-produccion")
    DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"


class ConfiguracionEmail:
    """
    Configuración para envío de correos vía API REST de Resend.
    Plan gratuito: 3,000 correos/mes, sin tarjeta de crédito.

    Pasos para obtener la API key:
    1. Crear cuenta en resend.com (solo email, gratis)
    2. Dashboard → API Keys → Create API Key → copiar la clave (empieza con 're_')
    3. Pegar la clave en API_KEY
    4. En EMAIL_REMITENTE usar 'onboarding@resend.dev' para pruebas (no requiere
       verificar dominio), o tu propio dominio verificado en producción.
    """
    API_KEY         = "re_Z6UjZijt_ef6yvfkSQXWHjkAzQgNvG3ew"                        # ← pegar clave de Resend aquí
    EMAIL_REMITENTE = "onboarding@resend.dev"   # remitente de prueba de Resend
    EMAIL_NOMBRE    = "Biblioteca"
