"""
servicios/servicio_ciclo_diario.py
-------------------------------------
Orquesta el ciclo diario automático del sistema:
  1. Procesa vencimientos y genera multas (ServicioMultas).
  2. Envía recordatorio a usuarios con préstamos próximos a vencer.
  3. Envía aviso de multa a TODOS los usuarios con multas pendientes
     (no solo a los que recibieron una multa nueva hoy).

Se llama desde main.py mediante un before_request de Flask, como máximo
una vez por día por instancia del servidor.
"""

from datetime import date

from servicios.servicio_multas import ServicioMultas
from servicios.servicio_prestamos import ServicioPrestamos
from servicios.servicio_notificaciones import (
    EnviadorNotificaciones,
    NotificacionRecordatorioDevolucion,
    NotificacionMultaGenerada,
)


class ServicioCicloDiario:
    def __init__(self):
        self._servicio_multas = ServicioMultas()
        self._servicio_prestamos = ServicioPrestamos()
        self._enviador = EnviadorNotificaciones()

    def ejecutar(self) -> dict:
        """
        Ejecuta el ciclo completo. El envío de correos de multa es
        independiente de si hoy se generaron multas nuevas: se avisa
        a todos los usuarios que tienen deuda pendiente en este momento.
        """
        resumen = {
            "fecha": str(date.today()),
            "prestamos_vencidos_marcados": 0,
            "multas_generadas": 0,
            "correos_recordatorio_enviados": 0,
            "correos_multa_enviados": 0,
        }

        # 1. Procesar vencimientos y generar multas del día
        resultado = self._servicio_multas.procesar_vencimientos()
        resumen["prestamos_vencidos_marcados"] = resultado["prestamos_marcados_vencidos"]
        resumen["multas_generadas"] = resultado["total_multas_nuevas"]

        # 2. Notificar a TODOS los usuarios con deuda pendiente (no solo nuevas)
        #    Consultamos directamente los préstamos vencidos con multas pendientes
        usuarios_con_deuda = self._obtener_usuarios_con_deuda_pendiente()
        for info in usuarios_con_deuda:
            notif = NotificacionMultaGenerada(
                destinatario_nombre=info["nombre_usuario"],
                destinatario_email=info["email_usuario"],
                titulo_libro=info["titulo_libro"],
                monto=info["total_pendiente"],
                dias_atraso=info["dias_atraso"],
            )
            if self._enviador.enviar(notif):
                resumen["correos_multa_enviados"] += 1

        # 3. Recordatorios para préstamos próximos a vencer (2 días)
        proximos = self._servicio_prestamos.proximos_a_vencer(dias_aviso=2)
        for prestamo in proximos:
            limite = self._servicio_prestamos.fecha_limite_devolucion(
                prestamo.usuario, prestamo.fecha_prestamo
            )
            notif = NotificacionRecordatorioDevolucion(
                destinatario_nombre=prestamo.usuario.nombre,
                destinatario_email=prestamo.usuario.email,
                titulo_libro=prestamo.libro.titulo,
                fecha_limite=limite,
            )
            if self._enviador.enviar(notif):
                resumen["correos_recordatorio_enviados"] += 1

        return resumen

    def _obtener_usuarios_con_deuda_pendiente(self) -> list:
        """
        Devuelve un registro por cada préstamo vencido que tenga al menos
        una multa pendiente, con el total de la deuda de ese préstamo.
        Se usa para el envío diario de recordatorios de pago.
        """
        sql = """
            SELECT
                pe.id_persona,
                pe.nombre   AS nombre_usuario,
                pe.email    AS email_usuario,
                li.titulo   AS titulo_libro,
                pr.id_prestamo,
                pr.fecha_prestamo,
                COALESCE(SUM(mu.monto), 0)  AS total_pendiente,
                DATEDIFF(CURDATE(), pr.fecha_prestamo) AS dias_atraso
            FROM prestamos pr
            INNER JOIN usuarios u  ON u.id_usuario  = pr.id_usuario
            INNER JOIN personas pe ON pe.id_persona = u.id_persona
            INNER JOIN libros li   ON li.ISBN        = pr.isbn
            INNER JOIN multas mu   ON mu.id_prestamo = pr.id_prestamo
            INNER JOIN estados_prestamo ep ON ep.id_estado_prestamo = pr.id_estado
            WHERE mu.estado_pago = 'PENDIENTE'
              AND ep.descripcion IN ('Activo', 'Vencido')
              AND pr.fecha_devolucion IS NULL
            GROUP BY pr.id_prestamo, pe.id_persona, pe.nombre, pe.email,
                     li.titulo, pr.fecha_prestamo
            HAVING total_pendiente > 0
        """
        from persistencia.repositorio_prestamos import RepositorioMultas
        return RepositorioMultas().ejecutar_consulta_personalizada(sql)
