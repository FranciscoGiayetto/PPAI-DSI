"""Carga datos de prueba: CMs, un Encargado de Bolsines y bolsines Enviados desde CMJ Córdoba."""
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from bolsines.models import Bolsin, ComisionMedica, Empleado, Remito

CMS = [
    ('CMJ-COR', 'Comisión Médica Jurisdiccional Córdoba', 'CMJ'),
    ('CMC-CABA', 'Comisión Médica Central CABA', 'CMC'),
    ('CMJ-ROS', 'Comisión Médica Jurisdiccional Rosario', 'CMJ'),
    ('CMJ-MZA', 'Comisión Médica Jurisdiccional Mendoza', 'CMJ'),
    ('CMJ-TUC', 'Comisión Médica Jurisdiccional Tucumán', 'CMJ'),
    ('CMJ-SAL', 'Comisión Médica Jurisdiccional Salta', 'CMJ'),
]
# (nro, destino, estado, peso g, cantidad de remitos)
BOLSINES = [
    (1048, 'CMC-CABA', Bolsin.ESTADO_ENVIADO, 2400, 3),
    (1047, 'CMJ-ROS', Bolsin.ESTADO_ENVIADO, 1800, 2),
    (1046, 'CMJ-MZA', Bolsin.ESTADO_ENVIADO, 3100, 4),
    (1044, 'CMJ-TUC', Bolsin.ESTADO_ENVIADO, 950, 1),
    (1043, 'CMC-CABA', Bolsin.ESTADO_ENVIADO, 2050, 2),
    (1041, 'CMJ-SAL', Bolsin.ESTADO_ENVIADO, 1500, 2),   # sin señal en la demo (A3)
    (1049, 'CMJ-ROS', Bolsin.ESTADO_CERRADO, 1200, 1),   # no se muestra: no está Enviado
]


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
        Empleado.objects.update_or_create(user=user, defaults={
            'legajo': '40211', 'rol': Empleado.ROL_ENCARGADO_BOLSINES, 'cm_asignada': cms['CMJ-COR']})

        nro_remito = 5000
        for i, (nro, destino, estado, peso, n_remitos) in enumerate(BOLSINES):
            bolsin, _ = Bolsin.objects.update_or_create(nro_bolsin=nro, defaults={
                'fecha': date.today() - timedelta(days=i % 3),
                'peso_gramos': peso,
                'nro_precinto': f'PR-26-{4800 + nro - 1036:06d}',
                'cm_origen': cms['CMJ-COR'],
                'cm_destino': cms[destino],
                'estado_actual': estado,
            })
            for _ in range(n_remitos):
                nro_remito += 1
                Remito.objects.update_or_create(nro_remito=nro_remito, defaults={
                    'bolsin': bolsin, 'cm_destino': cms[destino],
                    'estado_actual': Remito.ESTADO_EN_BOLSIN_ENVIADO})

        self.stdout.write(self.style.SUCCESS(
            'Datos cargados. Ingresá con legajo 40211 y contraseña bolsines2026.'))
