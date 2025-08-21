from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from apps.quality_data.services import ExternalQualityAPIService
from apps.authentication.models import Company

User = get_user_model()


class Command(BaseCommand):
    help = 'Sincroniza datos de calidad desde la API externa'

    def add_arguments(self, parser):
        parser.add_argument(
            '--empresa',
            type=str,
            help='Nombre de la empresa a sincronizar'
        )
        parser.add_argument(
            '--all-companies',
            action='store_true',
            help='Sincronizar todas las empresas del sistema'
        )
        parser.add_argument(
            '--admin-user',
            type=str,
            help='Email del usuario administrador para la sincronización'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Límite de registros a sincronizar por empresa'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando sincronización de datos de calidad...')
        )

        # Obtener usuario administrador
        admin_user = self._get_admin_user(options.get('admin_user'))
        if not admin_user:
            raise CommandError('No se pudo obtener un usuario administrador')

        # Crear servicio de API externa
        external_service = ExternalQualityAPIService()

        # Verificar conexión
        if not external_service.login():
            raise CommandError('No se pudo conectar con la API externa')

        # Determinar empresas a sincronizar
        empresas = self._get_empresas_to_sync(options)

        if not empresas:
            raise CommandError('No se encontraron empresas para sincronizar')

        # Sincronizar cada empresa
        total_processed = 0
        total_created = 0
        total_updated = 0

        for empresa in empresas:
            self.stdout.write(f"\n🔄 Sincronizando empresa: {empresa}")
            
            try:
                result = external_service.sync_quality_data_for_company(empresa, admin_user)
                
                if result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ {empresa}: {result['records_processed']} procesados, "
                            f"{result['records_created']} creados, "
                            f"{result['records_updated']} actualizados"
                        )
                    )
                    total_processed += result['records_processed']
                    total_created += result['records_created']
                    total_updated += result['records_updated']
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ {empresa}: {result['message']}")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error sincronizando {empresa}: {str(e)}")
                )

        # Resumen final
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(
            self.style.SUCCESS(
                f"📊 RESUMEN DE SINCRONIZACIÓN:\n"
                f"  Empresas procesadas: {len(empresas)}\n"
                f"  Total registros procesados: {total_processed}\n"
                f"  Total registros creados: {total_created}\n"
                f"  Total registros actualizados: {total_updated}"
            )
        )

    def _get_admin_user(self, admin_email=None):
        """
        Obtiene un usuario administrador para la sincronización
        """
        if admin_email:
            try:
                return User.objects.get(email=admin_email, is_superuser=True)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"Usuario {admin_email} no encontrado o no es admin")
                )
        
        # Buscar cualquier superusuario
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            self.stdout.write(f"Usando admin: {admin_user.email}")
            return admin_user
        
        # Buscar usuario con rol admin
        admin_user = User.objects.filter(role__name='admin').first()
        if admin_user:
            self.stdout.write(f"Usando admin: {admin_user.email}")
            return admin_user
        
        return None

    def _get_empresas_to_sync(self, options):
        """
        Determina qué empresas sincronizar
        """
        empresas = []

        # Si se especifica una empresa específica
        if options.get('empresa'):
            empresas.append(options['empresa'])
            return empresas

        # Si se quiere sincronizar todas las empresas del sistema
        if options.get('all_companies'):
            companies = Company.objects.filter(activo=True)
            empresas = [company.name for company in companies]
            
            if not empresas:
                self.stdout.write(
                    self.style.WARNING('No se encontraron empresas activas en el sistema')
                )
            
            return empresas

        # Por defecto, usar empresas comunes de arándanos
        default_empresas = [
            "SAN LUCAR S.A.",
            "SAN LUCAR S.A.C.",
            "BLUEBERRY FARM",
            "ARANDANOS DEL PERU",
        ]
        
        self.stdout.write(
            self.style.WARNING(
                f"No se especificó empresa. Usando empresas por defecto: {default_empresas}"
            )
        )
        
        return default_empresas
