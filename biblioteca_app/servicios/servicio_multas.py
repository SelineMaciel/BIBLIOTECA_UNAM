"""
servicios/servicio_multas.py
---------------------------------
Calcula y registra multas por días de atraso en la devolución.
Usa la COMPOSICIÓN definida en modelos/prestamo.py: las multas se
generan siempre a partir de un Prestamo concreto (prestamo.generar_multa),
nunca de forma aislada.
"""

from datetime import date

from persistencia.repositorio_prestamos import (
    RepositorioPrestamos, RepositorioMultas, RepositorioEstadosPrestamo
)
from servicios.servicio_prestamos import ServicioPrestamos


class ServicioMultas:
    MONTO_POR_DIA_ATRASO = 1.50  # S/ por día de atraso

    def __init__(self):
        self._repo_prestamos = RepositorioPrestamos()
        self._repo_multas = RepositorioMultas()
        self._repo_estados = RepositorioEstadosPrestamo()
        self._servicio_prestamos = ServicioPrestamos()

    def procesar_vencimientos(self) -> dict:
        """
        Método principal del ciclo diario automático. Hace dos cosas:
          1. Marca como 'Vencido' los préstamos activos que superaron
             su fecha límite (actualiza estado en BD).
          2. Genera una multa diaria por cada préstamo vencido que no
             tenga ya una multa registrada hoy.

        Devuelve un resumen con lo que hizo, útil para el log y para
        mostrar en el panel de admin cuando se dispara manualmente.
        """
        estado_vencido = self._repo_estados.obtener_por_descripcion("Vencido")
        vencidos = self._servicio_prestamos.obtener_vencidos_hoy()
        multas_generadas = []
        prestamos_marcados = 0

        for prestamo in vencidos:
            limite = self._servicio_prestamos.fecha_limite_devolucion(
                prestamo.usuario, prestamo.fecha_prestamo
            )
            dias_atraso = (date.today() - limite).days
            if dias_atraso <= 0:
                continue

            # 1. Actualizar estado a "Vencido" si sigue como "Activo"
            if prestamo.estado.descripcion == "Activo":
                self._repo_prestamos.ejecutar_consulta_personalizada(
                    "UPDATE prestamos SET id_estado = %s WHERE id_prestamo = %s",
                    (estado_vencido.id_estado_prestamo, prestamo.id_prestamo)
                )
                self._repo_prestamos._db.confirmar()
                prestamos_marcados += 1

            # 2. Generar multa del día si no existe ya una para hoy
            multas_existentes = self._repo_multas.obtener_por_prestamo(prestamo.id_prestamo)
            ya_generada_hoy = any(m.fecha_multa == date.today() for m in multas_existentes)
            if ya_generada_hoy:
                continue

            monto = round(dias_atraso * self.MONTO_POR_DIA_ATRASO, 2)
            id_multa = self._repo_multas.crear_para_prestamo(
                prestamo.id_prestamo, monto, date.today()
            )
            multas_generadas.append({
                "id_multa": id_multa,
                "id_prestamo": prestamo.id_prestamo,
                "usuario": prestamo.usuario.nombre,
                "email_usuario": prestamo.usuario.email,
                "libro": prestamo.libro.titulo,
                "monto": monto,
                "dias_atraso": dias_atraso,
            })

        return {
            "prestamos_marcados_vencidos": prestamos_marcados,
            "multas_generadas": multas_generadas,
            "total_multas_nuevas": len(multas_generadas),
        }

    # Mantenemos el nombre anterior como alias para compatibilidad
    def calcular_y_generar_multas_vencidos(self) -> list:
        return self.procesar_vencimientos()["multas_generadas"]

    def total_pendiente_por_usuario(self, id_usuario: int) -> float:
        prestamos_usuario = self._repo_prestamos.ejecutar_consulta_personalizada(
            "SELECT id_prestamo FROM prestamos WHERE id_usuario = %s", (id_usuario,)
        )
        total = 0.0
        for fila in prestamos_usuario:
            multas = self._repo_multas.obtener_por_prestamo(fila["id_prestamo"])
            total += sum(m.monto for m in multas if m.esta_pendiente())
        return round(total, 2)

    def multas_pendientes_por_usuario(self, id_usuario: int) -> list:
        """
        Devuelve el detalle de todas las multas pendientes de un usuario,
        con información del préstamo y libro asociado. Usado en la vista
        de multas del panel de usuario.
        """
        sql = """
            SELECT mu.id_multa, mu.monto, mu.fecha_multa, mu.estado_pago,
                   pr.id_prestamo, pr.fecha_prestamo,
                   li.titulo
            FROM multas mu
            INNER JOIN prestamos pr ON pr.id_prestamo = mu.id_prestamo
            INNER JOIN libros li ON li.ISBN = pr.isbn
            WHERE pr.id_usuario = %s AND mu.estado_pago = 'PENDIENTE'
            ORDER BY mu.fecha_multa DESC
        """
        return self._repo_multas.ejecutar_consulta_personalizada(sql, (id_usuario,))

    def pagar_multa(self, id_multa: int) -> bool:
        return self._repo_multas.marcar_pagada(id_multa)
