"""
servicios/servicio_permisos.py
----------------------------------
Centraliza la verificación de permisos. Internamente delega en el
método polimórfico persona.tiene_acceso(nombre_permiso), que cada
subclase de Persona implementa a su manera (ver modelos/persona.py).

Este servicio existe para que controladores/decoradores no llamen
directamente a persona.tiene_acceso(...) disperso por todo el código,
sino que pasen siempre por un único punto centralizado y fácil de
auditar o extender (ej. loggear intentos de acceso denegado).
"""


class AccesoDenegadoError(Exception):
    pass


class ServicioPermisos:

    def usuario_puede(self, persona, nombre_permiso: str) -> bool:
        """
        Recibe CUALQUIER subclase de Persona (Usuario, Empleado o
        AdminUser) y delega en su propia implementación de
        tiene_acceso(). Esto ES polimorfismo en acción: este método
        no necesita un if/elif por tipo de persona.
        """
        if persona is None:
            return False
        return persona.tiene_acceso(nombre_permiso)

    def exigir_permiso(self, persona, nombre_permiso: str):
        """Versión que lanza excepción en vez de devolver booleano,
        útil para usar al inicio de una operación crítica."""
        if not self.usuario_puede(persona, nombre_permiso):
            nombre_legible = getattr(persona, "nombre", "Desconocido")
            raise AccesoDenegadoError(
                f"'{nombre_legible}' no tiene el permiso requerido: '{nombre_permiso}'"
            )

    def panel_para(self, persona) -> str:
        """También polimórfico: cada Persona sabe a qué panel pertenece."""
        if persona is None:
            return "panel_invitado"
        return persona.panel()
