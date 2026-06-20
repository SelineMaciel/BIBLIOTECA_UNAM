"""
servicios/servicio_notificaciones.py
-----------------------------------------
Define una jerarquía de Notificacion (HERENCIA + POLIMORFISMO):
cada subclase sabe construir su propio asunto y cuerpo de mensaje,
pero todas comparten la misma interfaz (asunto(), cuerpo()).

El envío real (vía API REST de SendGrid/Mailgun) se implementará en
la Fase 6, en este mismo archivo, dentro de EnviadorNotificaciones.
Por ahora EnviadorNotificaciones ya está preparado para recibir
cualquier subclase de Notificacion sin necesitar saber cuál es
(de nuevo, polimorfismo): solo llama notificacion.asunto() y
notificacion.cuerpo().
"""

from abc import ABC, abstractmethod


class Notificacion(ABC):
    """Clase base abstracta para cualquier tipo de notificación enviable."""

    def __init__(self, destinatario_nombre: str, destinatario_email: str):
        self._destinatario_nombre = destinatario_nombre
        self._destinatario_email = destinatario_email

    @property
    def destinatario_email(self) -> str:
        return self._destinatario_email

    @property
    def destinatario_nombre(self) -> str:
        return self._destinatario_nombre

    @abstractmethod
    def asunto(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def cuerpo(self) -> str:
        raise NotImplementedError


class NotificacionRecordatorioDevolucion(Notificacion):
    """Se envía cuando un préstamo está próximo a vencer."""

    def __init__(self, destinatario_nombre, destinatario_email, titulo_libro: str, fecha_limite):
        super().__init__(destinatario_nombre, destinatario_email)
        self._titulo_libro = titulo_libro
        self._fecha_limite = fecha_limite

    def asunto(self) -> str:
        return "Recordatorio: devolución próxima a vencer"

    def cuerpo(self) -> str:
        return (
            f"Hola {self._destinatario_nombre},\n\n"
            f"Te recordamos que el libro \"{self._titulo_libro}\" debe ser devuelto "
            f"antes del {self._fecha_limite.strftime('%d/%m/%Y')}.\n\n"
            f"Gracias por usar nuestra biblioteca."
        )


class NotificacionMultaGenerada(Notificacion):
    """Se envía cuando se genera una multa por atraso."""

    def __init__(self, destinatario_nombre, destinatario_email, titulo_libro: str, monto: float, dias_atraso: int):
        super().__init__(destinatario_nombre, destinatario_email)
        self._titulo_libro = titulo_libro
        self._monto = monto
        self._dias_atraso = dias_atraso

    def asunto(self) -> str:
        return "Se generó una multa en tu cuenta"

    def cuerpo(self) -> str:
        return (
            f"Hola {self._destinatario_nombre},\n\n"
            f"El libro \"{self._titulo_libro}\" tiene {self._dias_atraso} día(s) de atraso. "
            f"Se generó una multa de S/ {self._monto:.2f}.\n\n"
            f"Por favor regulariza tu situación en la sucursal más cercana."
        )


class NotificacionConfirmacionReserva(Notificacion):
    """Se envía cuando una reserva queda confirmada y lista para recoger."""

    def __init__(self, destinatario_nombre, destinatario_email, titulo_libro: str, fecha_expiracion):
        super().__init__(destinatario_nombre, destinatario_email)
        self._titulo_libro = titulo_libro
        self._fecha_expiracion = fecha_expiracion

    def asunto(self) -> str:
        return "Tu reserva está confirmada"

    def cuerpo(self) -> str:
        return (
            f"Hola {self._destinatario_nombre},\n\n"
            f"Tu reserva del libro \"{self._titulo_libro}\" está confirmada. "
            f"Tienes hasta el {self._fecha_expiracion.strftime('%d/%m/%Y')} para recogerlo "
            f"en la sucursal seleccionada."
        )


class EnviadorNotificaciones:
    """
    Envía correos reales vía API REST de Resend (resend.com).
    Usa solo urllib de la librería estándar de Python — sin instalar nada.

    Si API_KEY está vacío cae a modo simulado (imprime en consola)
    para no romper el flujo en desarrollo.

    POLIMORFISMO: recibe cualquier subclase de Notificacion y usa
    solo la interfaz común (asunto/cuerpo/destinatario).
    """

    RESEND_URL = "https://api.resend.com/emails"

    def enviar(self, notificacion: Notificacion) -> bool:
        from config import ConfiguracionEmail
        api_key   = ConfiguracionEmail.API_KEY
        remitente = ConfiguracionEmail.EMAIL_REMITENTE
        nombre    = ConfiguracionEmail.EMAIL_NOMBRE

        if not api_key:
            # Modo desarrollo: simular envío en consola
            print(f"[EMAIL simulado] Para: {notificacion.destinatario_email}")
            print(f"  Asunto : {notificacion.asunto()}")
            print(f"  Cuerpo :\n{notificacion.cuerpo()}\n")
            return True

        # Modo producción: API REST de Resend
        import json as _json
        try:
            import requests as _requests
        except ImportError:
            print("[Resend] La librería 'requests' no está instalada. Ejecuta: pip install requests")
            return False

        try:
            resp = _requests.post(
                self.RESEND_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type":  "application/json",
                },
                json={
                    "from":    f"{nombre} <{remitente}>",
                    "to":      [notificacion.destinatario_email],
                    "subject": notificacion.asunto(),
                    "text":    notificacion.cuerpo(),
                },
                timeout=10,
            )
            if resp.status_code in (200, 201):
                data = resp.json()
                print(f"[Resend] OK → {notificacion.destinatario_email} | id={data.get('id')}")
                return True
            else:
                print(f"[Resend] Error HTTP {resp.status_code}: {resp.text}")
                return False
        except Exception as e:
            print(f"[Resend] Excepción inesperada: {e}")
            return False

    def enviar_varias(self, notificaciones: list) -> int:
        enviadas = 0
        for n in notificaciones:
            if self.enviar(n):
                enviadas += 1
        return enviadas
