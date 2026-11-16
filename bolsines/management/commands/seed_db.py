"""Carga datos de prueba: CMs, un Encargado de Bolsines y bolsines Enviados desde CMJ Córdoba."""
from datetime import date, datetime, time, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from bolsines.models import Bolsin, CambioEstadoBolsin, ComisionMedica, Empleado, Remito

# Códigos alineados con los bolsines precargados en el servidor GPS de la cátedra (gps-api).
CMS = [
    ('CM-CBA-01', 'Comisión Médica Jurisdiccional Córdoba', 'CMJ'),
    ('CM-CBA-02', 'Comisión Médica Jurisdiccional Córdoba Sur', 'CMJ'),
    ('CM-BA-01', 'Comisión Médica Central CABA', 'CMC'),
    ('CM-ROS-02', 'Comisión Médica Jurisdiccional Rosario', 'CMJ'),
    ('CM-MDZ-03', 'Comisión Médica Jurisdiccional Mendoza', 'CMJ'),
]
# (nro, destino, estado, peso g, cantidad de remitos). Los nros 101-103 existen en el GPS mock (origen CM-CBA-01).
BOLSINES = [
    (101, 'CM-ROS-02', Bolsin.ESTADO_ENVIADO, 2400, 3),
    (102, 'CM-MDZ-03', Bolsin.ESTADO_ENVIADO, 1800, 2),
    (103, 'CM-BA-01', Bolsin.ESTADO_ENVIADO, 3100, 4),
    (150, 'CM-ROS-02', Bolsin.ESTADO_ENVIADO, 950, 1),    # no existe en el GPS: demuestra el flujo A3
    (120, 'CM-ROS-02', Bolsin.ESTADO_CERRADO, 1200, 1),   # no se muestra: no está Enviado
]
# Gerentes de CM destino (reciben el correo del CU 30).
GERENTES = [('gcm-ros', '50101', 'CM-ROS-02', 'abdalavaleria@gmail.com'),
            ('gcm-mdz', '50102', 'CM-MDZ-03', 'mateo.crespo100@gmail.com'),
            ('gcm-ba', '50103', 'CM-BA-01', 'maurobastasiniprof@gmail.com')]

def cargar_historial(bolsin: Bolsin, empleado: Empleado) -> None:
    """Crea los cambios de estado hasta el estado actual del bolsín (Creado → Cerrado → Enviado), si no tiene."""
    if bolsin.cambios_estado.exists():
        return
    pasos = [('—', Bolsin.ESTADO_CREADO, 0), (Bolsin.ESTADO_CREADO, Bolsin.ESTADO_CERRADO, 135),
             (Bolsin.ESTADO_CERRADO, Bolsin.ESTADO_ENVIADO, 300)]
    inicio = timezone.make_aware(datetime.combine(bolsin.fecha, time(9, 0)))
    for anterior, nuevo, minutos in pasos:
        CambioEstadoBolsin.objects.create(bolsin=bolsin, estado_anterior=anterior, estado_nuevo=nuevo,
                                          empleado=empleado, fecha_hora=inicio + timedelta(minutes=minutos))
        if nuevo == bolsin.estado_actual:
            break


class Command(BaseCommand):
    help = 'Carga datos de prueba (usuario: legajo 40211 / contraseña bolsines2026).'

    @transaction.atomic
    def handle(self, *args, **options):
        cms = {}
        for codigo, nombre, tipo in CMS:
            cms[codigo], _ = ComisionMedica.objects.update_or_create(
                codigo=codigo, defaults={'nombre': nombre, 'tipo': tipo})

        user, _ = User.objects.get_or_create(username='eb40211', defaults={
            'first_name': 'Lucía', 'last_name': 'Ferreyra'})
        user.set_password('bolsines2026')
        user.save()
        encargado, _ = Empleado.objects.update_or_create(user=user, defaults={
            'legajo': '40211', 'rol': Empleado.ROL_ENCARGADO_BOLSINES, 'cm_asignada': cms['CM-CBA-01']})

        for username, legajo, cm, mail in GERENTES:
            g, _ = User.objects.get_or_create(username=username, defaults={'first_name': 'Gerente', 'last_name': cm})
            g.email = mail
            g.set_password('bolsines2026'); g.save()
            Empleado.objects.update_or_create(user=g, defaults={'legajo': legajo, 'rol': Empleado.ROL_GERENTE_CM, 'cm_asignada': cms[cm]})

        nro_remito = 5000
        for i, (nro, destino, estado, peso, n_remitos) in enumerate(BOLSINES):
            bolsin, _ = Bolsin.objects.update_or_create(nro_bolsin=nro, defaults={
                'fecha': date.today() - timedelta(days=i % 3),
                'peso_gramos': peso,
                'nro_precinto': f'PR-26-{4800 + nro:06d}',
                'cm_origen': cms['CM-CBA-01'],
                'cm_destino': cms[destino],
                'estado_actual': estado,
            })
            for _ in range(n_remitos):
                nro_remito += 1
                Remito.objects.update_or_create(nro_remito=nro_remito, defaults={
                    'bolsin': bolsin, 'cm_destino': cms[destino],
                    'estado_actual': Remito.ESTADO_EN_BOLSIN_ENVIADO})
            cargar_historial(bolsin, encargado)

        self.stdout.write(self.style.SUCCESS(
            'Datos cargados. Ingresá con legajo 40211 y contraseña bolsines2026.'))
