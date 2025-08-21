import requests
import json
import aiohttp
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from django.conf import settings
from django.core.cache import cache
from .models import QualityData
from django.db.models import Avg, Count
from asgiref.sync import sync_to_async


class ExternalQualityAPIService:
    """
    Servicio para conectar con la API externa de calidad de arándanos
    """
    
    def __init__(self, base_url: str = None, username: str = None, password: str = None):
        """
        Inicializa el servicio de API externa
        
        Args:
            base_url: URL base de la API externa
            username: Usuario para autenticación
            password: Contraseña para autenticación
        """
        # Usar configuración del settings o valores por defecto
        self.base_url = base_url or getattr(settings, 'EXTERNAL_QUALITY_API_URL', 'http://34.136.15.241:8001')
        self.username = username or getattr(settings, 'EXTERNAL_QUALITY_API_USERNAME', 'admin')
        self.password = password or getattr(settings, 'EXTERNAL_QUALITY_API_PASSWORD', 'admin123')
        
        self.base_url = self.base_url.rstrip('/')
        self.token = None
        self.token_expiry = None
        
        # URLs de la API
        self.login_url = f"{self.base_url}/api/v1/auth/login"
        self.data_url = f"{self.base_url}/api/v1/data/calidad-producto-terminado"
        
        print(f"🔗 Servicio API externa inicializado para: {self.base_url}")
    
    def login(self) -> bool:
        """
        Inicia sesión y obtiene un token JWT
        
        Returns:
            bool: True si el login fue exitoso, False en caso contrario
        """
        try:
            data = {
                "username": self.username,
                "password": self.password
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            print(f"🔐 Intentando login con usuario: {self.username}")
            
            response = requests.post(
                self.login_url,
                json=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data["access_token"]
                self.token_expiry = datetime.now().timestamp() + (30 * 60)  # 30 minutos
                
                print("✅ Login exitoso - Token generado")
                return True
            else:
                print(f"❌ Error en login: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Error de conexión: No se puede conectar a {self.base_url}")
            return False
        except requests.exceptions.Timeout:
            print("❌ Error de timeout: La API no respondió en tiempo")
            return False
        except Exception as e:
            print(f"❌ Error inesperado en login: {str(e)}")
            return False
    
    async def login_async(self) -> bool:
        """
        Versión async del login
        
        Returns:
            bool: True si el login fue exitoso, False en caso contrario
        """
        try:
            data = {
                "username": self.username,
                "password": self.password
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            print(f"🔐 Intentando login async con usuario: {self.username}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.login_url,
                    json=data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.token = token_data["access_token"]
                        self.token_expiry = datetime.now().timestamp() + (30 * 60)  # 30 minutos
                        
                        print("✅ Login async exitoso - Token generado")
                        return True
                    else:
                        print(f"❌ Error en login async: {response.status} - {await response.text()}")
                        return False
                
        except aiohttp.ClientConnectionError:
            print(f"❌ Error de conexión async: No se puede conectar a {self.base_url}")
            return False
        except asyncio.TimeoutError:
            print("❌ Error de timeout async: La API no respondió en tiempo")
            return False
        except Exception as e:
            print(f"❌ Error inesperado en login async: {str(e)}")
            return False
    
    def _is_token_valid(self) -> bool:
        """
        Verifica si el token actual es válido
        
        Returns:
            bool: True si el token es válido, False en caso contrario
        """
        if not self.token:
            return False
        
        # Verificar si el token ha expirado (con margen de 1 minuto)
        if self.token_expiry and datetime.now().timestamp() > (self.token_expiry - 60):
            print("🔄 Token expirado o próximo a expirar")
            return False
        
        return True
    
    def _ensure_valid_token(self) -> bool:
        """
        Asegura que hay un token válido, renovándolo si es necesario
        
        Returns:
            bool: True si hay un token válido, False en caso contrario
        """
        if not self._is_token_valid():
            print("🔄 Renovando token...")
            return self.login()
        return True
    
    async def _ensure_valid_token_async(self) -> bool:
        """
        Versión async para asegurar token válido
        
        Returns:
            bool: True si hay un token válido, False en caso contrario
        """
        if not self._is_token_valid():
            print("🔄 Renovando token async...")
            return await self.login_async()
        return True
    
    def get_quality_data_by_company(self, empresa: str, limit: Optional[int] = None, offset: int = 0) -> Optional[List[Dict[str, Any]]]:
        """
        Obtiene datos de calidad filtrados por empresa
        
        Args:
            empresa: Nombre de la empresa a filtrar
            limit: Número máximo de registros a obtener (None = sin límite)
            offset: Número de registros a saltar
            
        Returns:
            Lista de registros filtrados por empresa o None si hay error
        """
        if not self._ensure_valid_token():
            print("❌ No se pudo obtener un token válido")
            return None
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
            
            # Preparar filtros: algunos datasets usan PRODUCTOR en lugar de EMPRESA
            filters = {"EMPRESA": empresa, "PRODUCTOR": empresa}
            
            data = {
                "filters": filters
            }
            
            if limit is not None:
                # Enviar ambos estilos de paginación por compatibilidad
                data["limit"] = limit
                data["page_size"] = limit
                # Calcular número de página a partir del offset en caso de que el API externo use page/page_size
                page_number = (offset // max(limit, 1)) + 1 if offset > 0 else 1
                data["page"] = page_number
            if offset > 0:
                data["offset"] = offset
            
            print(f"🔍 Obteniendo datos de calidad para empresa: {empresa}")
            print(f"📊 Parámetros: {data}")
            
            response = requests.post(
                self.data_url,
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Datos de calidad obtenidos exitosamente: {len(result)} registros para {empresa}")
                return result
            elif response.status_code == 401:
                print("🔄 Token expirado, intentando renovar...")
                if self.login():
                    # Reintentar la petición con el nuevo token
                    return self.get_quality_data_by_company(empresa, limit, offset)
                else:
                    print("❌ No se pudo renovar el token")
                    return None
            else:
                print(f"❌ Error obteniendo datos de calidad: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("❌ Error de conexión")
            return None
        except requests.exceptions.Timeout:
            print("❌ Error de timeout")
            return None
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
            return None
    
    def get_all_quality_data_by_company(self, empresa: str, page_size: int = 100, max_pages: int = 100) -> Optional[List[Dict[str, Any]]]:
        """
        Obtiene todos los datos de calidad para una empresa, manejando paginación mediante limit/offset.
        
        Args:
            empresa: Nombre de la empresa a filtrar
            page_size: Tamaño de página a solicitar al API externo
            max_pages: Límite de seguridad de páginas para evitar loops infinitos
        
        Returns:
            Lista completa de registros o None si hay error
        """
        all_results: List[Dict[str, Any]] = []
        seen_ids = set()
        page_index: int = 1
        pages_fetched: int = 0
        
        while True:
            pages_fetched += 1
            if pages_fetched > max_pages:
                print(f"⚠️ Se alcanzó el máximo de páginas ({max_pages}). Deteniendo la paginación para {empresa}.")
                break
            
            offset = (page_index - 1) * page_size
            print(f"➡️ Solicitando página {page_index} (page_size={page_size}, offset={offset}) para {empresa}")
            batch = self.get_quality_data_by_company(empresa, limit=page_size, offset=offset)
            if batch is None:
                print("⚠️ Error durante la obtención paginada; retornando resultados parciales")
                return all_results if all_results else None
            
            if not batch:
                # No hay más registros
                break
            
            # De-duplicar por 'record_id' o 'id' si existen
            new_items = []
            for item in batch:
                candidate_id = item.get('record_id') or item.get('id') or item.get('processed_data', {}).get('record_id')
                key = candidate_id or json.dumps(item, sort_keys=True)
                if key not in seen_ids:
                    seen_ids.add(key)
                    new_items.append(item)
            
            if not new_items:
                # La página no trajo elementos nuevos; evitar loop infinito
                print("⚠️ Página sin elementos nuevos; posible repetición por parámetros no reconocidos. Deteniendo.")
                break
            
            all_results.extend(new_items)
            
            # Si el lote recibido es menor que el tamaño de página, asumimos última página
            if len(batch) < page_size:
                break
            
            page_index += 1
        
        print(f"📦 Total registros obtenidos para {empresa}: {len(all_results)}")
        return all_results
    
    async def get_quality_data_by_company_async(self, empresa: str, limit: Optional[int] = None, offset: int = 0) -> Optional[List[Dict[str, Any]]]:
        """
        Versión async para obtener datos de calidad filtrados por empresa
        
        Args:
            empresa: Nombre de la empresa a filtrar
            limit: Número máximo de registros a obtener (None = sin límite)
            offset: Número de registros a saltar
            
        Returns:
            Lista de registros filtrados por empresa o None si hay error
        """
        if not await self._ensure_valid_token_async():
            print("❌ No se pudo obtener un token válido (async)")
            return None
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
            
            # Preparar filtros: algunos datasets usan PRODUCTOR en lugar de EMPRESA
            filters = {"EMPRESA": empresa, "PRODUCTOR": empresa}
            
            data = {
                "filters": filters
            }
            
            if limit is not None:
                data["limit"] = limit
            if offset > 0:
                data["offset"] = offset
            
            print(f"🔍 Obteniendo datos de calidad async para empresa: {empresa}")
            print(f"📊 Parámetros: {data}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.data_url,
                    json=data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Datos de calidad obtenidos exitosamente (async): {len(result)} registros para {empresa}")
                        return result
                    elif response.status == 401:
                        print("🔄 Token expirado, intentando renovar (async)...")
                        if await self.login_async():
                            # Reintentar la petición con el nuevo token
                            return await self.get_quality_data_by_company_async(empresa, limit, offset)
                        else:
                            print("❌ No se pudo renovar el token (async)")
                            return None
                    else:
                        print(f"❌ Error obteniendo datos de calidad (async): {response.status} - {await response.text()}")
                        return None
                
        except aiohttp.ClientConnectionError:
            print("❌ Error de conexión (async)")
            return None
        except asyncio.TimeoutError:
            print("❌ Error de timeout (async)")
            return None
        except Exception as e:
            print(f"❌ Error inesperado (async): {str(e)}")
            return None
    
    def sync_quality_data_for_company(self, empresa: str, user=None) -> Dict[str, Any]:
        """
        Sincroniza datos de calidad para una empresa específica
        
        Args:
            empresa: Nombre de la empresa
            user: Usuario que realiza la sincronización
            
        Returns:
            Diccionario con el resultado de la sincronización
        """
        print(f"🔄 Iniciando sincronización de datos para: {empresa}")
        
        # Obtener datos de la API externa
        # Obtener TODOS los datos usando paginación por si el API externo aplica un límite por defecto
        external_data = self.get_all_quality_data_by_company(empresa)
        
        if not external_data:
            return {
                'success': False,
                'message': 'No se pudieron obtener datos de la API externa',
                'records_processed': 0,
                'records_created': 0,
                'records_updated': 0
            }
        
        records_created = 0
        records_updated = 0
        
        for data_item in external_data:
            try:
                # Procesar y mapear los datos
                processed_data = self._process_external_data(data_item)
                
                # Intentar identificar de forma única por record_id del sistema externo
                record_id = processed_data.get('processed_data', {}).get('additional_info', {}).get('record_id')
                quality_data = None
                created = False
                if record_id:
                    quality_data = QualityData.objects.filter(
                        empresa=empresa,
                        processed_data__additional_info__record_id=record_id
                    ).first()
                
                if quality_data is None:
                    # Fallback a combinación empresa + fecha_registro
                    quality_data, created = QualityData.objects.get_or_create(
                        empresa=empresa,
                        fecha_registro=processed_data['fecha_registro'],
                        defaults={
                            **processed_data,
                            'created_by': user,
                            'processed_data': processed_data['processed_data']
                        }
                    )
                else:
                    # Ya existe por record_id
                    for field, value in processed_data.items():
                        if field != 'processed_data':
                            setattr(quality_data, field, value)
                    quality_data.processed_data = processed_data['processed_data']
                    quality_data.save()
                    records_updated += 1
                    continue
                
                if created:
                    records_created += 1
                else:
                    for field, value in processed_data.items():
                        if field != 'processed_data':
                            setattr(quality_data, field, value)
                    quality_data.processed_data = processed_data['processed_data']
                    quality_data.save()
                    records_updated += 1
                    
            except Exception as e:
                print(f"❌ Error procesando registro: {str(e)}")
                continue
        
        result = {
            'success': True,
            'message': f'Sincronización completada para {empresa}',
            'records_processed': len(external_data),
            'records_created': records_created,
            'records_updated': records_updated
        }
        
        print(f"✅ Sincronización completada: {result}")
        return result
    
    async def sync_quality_data_for_company_async(self, empresa: str, user=None) -> Dict[str, Any]:
        """
        Versión async para sincronizar datos de calidad para una empresa específica
        
        Args:
            empresa: Nombre de la empresa
            user: Usuario que realiza la sincronización
            
        Returns:
            Diccionario con el resultado de la sincronización
        """
        print(f"🔄 Iniciando sincronización async de datos para: {empresa}")
        
        # Obtener datos de la API externa de forma async
        # Obtener TODOS los datos usando paginación (se reutiliza la versión síncrona paginada por compatibilidad)
        external_data = self.get_all_quality_data_by_company(empresa)
        
        if not external_data:
            return {
                'success': False,
                'message': 'No se pudieron obtener datos de la API externa (async)',
                'records_processed': 0,
                'records_created': 0,
                'records_updated': 0
            }
        
        records_created = 0
        records_updated = 0
        
        # Procesar registros de forma async
        for data_item in external_data:
            try:
                # Procesar y mapear los datos
                processed_data = self._process_external_data(data_item)
                
                # Buscar registro existente o crear uno nuevo de forma async
                quality_data, created = await sync_to_async(QualityData.objects.get_or_create)(
                    empresa=empresa,
                    fecha_registro=processed_data['fecha_registro'],
                    defaults={
                        **processed_data,
                        'created_by': user,
                        'processed_data': processed_data['processed_data']  # Usar la estructura correcta
                    }
                )
                
                if created:
                    records_created += 1
                else:
                    # Actualizar registro existente de forma async
                    for field, value in processed_data.items():
                        if field != 'processed_data':  # No actualizar processed_data aquí
                            setattr(quality_data, field, value)
                    quality_data.processed_data = processed_data['processed_data']  # Usar la estructura correcta
                    await sync_to_async(quality_data.save)()
                    records_updated += 1
                    
            except Exception as e:
                print(f"❌ Error procesando registro (async): {str(e)}")
                continue
        
        result = {
            'success': True,
            'message': f'Sincronización async completada para {empresa}',
            'records_processed': len(external_data),
            'records_created': records_created,
            'records_updated': records_updated
        }
        
        print(f"✅ Sincronización async completada: {result}")
        return result
    
    def _process_external_data(self, data_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa y mapea los datos de la API externa al modelo QualityData
        
        Args:
            data_item: Datos crudos de la API externa
            
        Returns:
            Diccionario con datos procesados
        """
        processed = {}
        
        # Extraer datos del campo 'processed_data.data' según la estructura real
        if 'processed_data' in data_item and 'data' in data_item['processed_data']:
            data = data_item['processed_data']['data']
        elif 'data' in data_item:
            data = data_item['data']
        else:
            data = data_item
        
        # Mapear empresa
        processed['empresa'] = data.get('EMPRESA', data.get('PRODUCTOR', ''))
        
        # Mapear fecha de registro
        fecha_mp = data.get('FECHA DE MP')
        fecha_proceso = data.get('FECHA DE PROCESO')
        
        if fecha_mp:
            try:
                processed['fecha_registro'] = datetime.fromisoformat(fecha_mp.replace('Z', '+00:00'))
            except:
                processed['fecha_registro'] = datetime.now()
        elif fecha_proceso:
            try:
                processed['fecha_registro'] = datetime.fromisoformat(fecha_proceso.replace('Z', '+00:00'))
            except:
                processed['fecha_registro'] = datetime.now()
        else:
            processed['fecha_registro'] = datetime.now()
        
        # Mapear campos de calidad del producto
        processed['solidos_solubles'] = self._safe_decimal(data.get('BRIX'))
        processed['acidez_titulable'] = self._safe_decimal(data.get('ACIDEZ'))
        processed['calibre'] = str(data.get('CALIBRE', '')) if data.get('CALIBRE') is not None else ''
        
        # Mapear campos de defectos
        total_defectos = self._safe_decimal(data.get('TOTAL DE DEFECTOS DE CALIDAD'))
        total_no_exportable = self._safe_decimal(data.get('TOTAL DE NO EXPORTABLE'))
        
        # Calcular porcentaje de defectos
        if total_defectos is not None:
            processed['defectos_porcentaje'] = total_defectos
        elif total_no_exportable is not None:
            processed['defectos_porcentaje'] = total_no_exportable
        else:
            processed['defectos_porcentaje'] = None
        
        # Crear descripción de defectos
        defectos_desc = []
        defectos_campos = [
            'DESGARRO', 'RESTOS FLORALES', 'EXCRETA DE ABEJA', 'HERIDA ABIERTA',
            'HERIDA CICATRIZADA', 'FUMAGINA', 'MACHUCON', 'PICADO', 'RUSSET',
            'QUERESA', 'OTROS', 'POLVO', 'HONGOS', 'OTROS2', 'F.BLOOM',
            'EXUDACION', 'F. MOJADA', 'PUDRICION', 'HALO VERDE', 'SOBREMADURO',
            'BAJO CALIBRE', 'BLANDA SEVERA', 'BAYA COLAPSADA', 'BAYA REVENTADA',
            'DAÑO DE TRIPS', 'EXCRETA DE AVE', 'FRUTOS ROJIZOS', 'BLANDA MODERADO',
            'CHANCHITO BLANCO', 'PRESENCIA DE LARVA', 'DESHIDRATADO SEVERO',
            'FRUTOS CON PEDICELO', 'DESHIDRATACIÓN  LEVE', 'DESHIDRATACION MODERADO'
        ]
        
        for campo in defectos_campos:
            valor = data.get(campo)
            if valor and valor > 0:
                defectos_desc.append(f"{campo}: {valor}%")
        
        processed['defectos_descripcion'] = '; '.join(defectos_desc) if defectos_desc else ''
        
        # Mapear campos adicionales
        processed['color'] = data.get('VARIEDAD', '')
        processed['observaciones'] = data.get('OBSERVACIONES', '')
        
        # Determinar calidad general basada en porcentaje de defectos
        if processed['defectos_porcentaje'] is not None:
            if processed['defectos_porcentaje'] <= 2:
                processed['calidad_general'] = 'excelente'
            elif processed['defectos_porcentaje'] <= 5:
                processed['calidad_general'] = 'buena'
            elif processed['defectos_porcentaje'] <= 10:
                processed['calidad_general'] = 'regular'
            else:
                processed['calidad_general'] = 'mala'
        else:
            processed['calidad_general'] = 'regular'
        
        # Determinar aprobación basada en total exportable
        total_exportable = self._safe_decimal(data.get('TOTAL DE EXPORTABLE'))
        if total_exportable is not None:
            processed['aprobado'] = total_exportable >= 90.0  # Aprobado si >= 90% exportable
        else:
            processed['aprobado'] = processed['defectos_porcentaje'] is not None and processed['defectos_porcentaje'] <= 5
        
        # Campos que no están en el modelo actual pero podrían ser útiles
        # Los guardamos en processed_data para referencia futura
        additional_info = {
            'destino': data.get('DESTINO'),
            'variedad': data.get('VARIEDAD'),
            'presentacion': data.get('PRESENTACION'),
            'tipo_caja': data.get('TIPO DE CAJA'),
            'tipo_producto': data.get('TIPO DE PRODUCTO'),
            'trazabilidad': data.get('TRAZABILIDAD'),
            'peso_muestra': data.get('PESO DE MUESTRA (g)'),
            'total_exportable': data.get('TOTAL DE EXPORTABLE'),
            'total_no_exportable': data.get('TOTAL DE NO EXPORTABLE'),
            'total_condicion': data.get('TOTAL DE CONDICION'),
            'evaluador': data.get('EVALUADOR'),
            'fundo': data.get('FUNDO'),
            'linea': data.get('LINEA'),
            'modulo': data.get('MODULO'),
            'turno': data.get('TURNO'),
            'viaje': data.get('VIAJE'),
            'semana': data.get('SEMANA'),
            'hora': data.get('HORA'),
            'n_fcl': data.get('N° FCL'),
            'productor': data.get('PRODUCTOR'),
            'fecha_mp': data.get('FECHA DE MP'),
            'fecha_proceso': data.get('FECHA DE PROCESO'),
            'record_id': data_item.get('record_id') or data_item.get('id'),
            'row_index': data_item.get('processed_data', {}).get('row_index'),
            'processed_at': data_item.get('processed_data', {}).get('processed_at')
        }
        
        # Guardar información adicional en processed_data
        processed['processed_data'] = {
            'original_data': data_item,
            'additional_info': additional_info
        }
        
        return processed
    
    def _safe_decimal(self, value) -> Optional[float]:
        """
        Convierte un valor a decimal de forma segura
        
        Args:
            value: Valor a convertir
            
        Returns:
            Valor decimal o None si no se puede convertir
        """
        if value is None or value == '':
            return None
        
        try:
            return float(value)
        except (ValueError, TypeError):
            return None


class QualityDataService:
    """
    Servicio para gestionar datos de calidad en el sistema
    """
    
    @staticmethod
    def get_quality_data_for_user_company(user) -> List[QualityData]:
        """
        Obtiene datos de calidad para la empresa del usuario
        
        Args:
            user: Usuario autenticado
            
        Returns:
            Lista de datos de calidad
        """
        if not user or not user.company:
            return QualityData.objects.none()
        
        return QualityData.objects.filter(empresa=user.company.name).order_by('-fecha_registro')
    
    @staticmethod
    def get_quality_stats(user=None, empresa=None) -> Dict[str, Any]:
        """
        Obtiene estadísticas de calidad
        
        Args:
            user: Usuario autenticado
            empresa: Empresa específica (opcional)
            
        Returns:
            Diccionario con estadísticas
        """
        queryset = QualityData.objects.all()
        
        # Filtrar por empresa del usuario si no se especifica otra
        if empresa:
            queryset = queryset.filter(empresa=empresa)
        elif user and user.company:
            queryset = queryset.filter(empresa=user.company.name)
        
        total_registros = queryset.count()
        registros_aprobados = queryset.filter(aprobado=True).count()
        registros_rechazados = total_registros - registros_aprobados
        
        # Calcular promedios
        promedio_temperatura = queryset.aggregate(Avg('temperatura'))['temperatura__avg']
        promedio_humedad = queryset.aggregate(Avg('humedad'))['humedad__avg']
        promedio_ph = queryset.aggregate(Avg('ph'))['ph__avg']
        
        # Breakdown por calidad
        calidad_breakdown = dict(
            queryset.values('calidad_general')
            .annotate(count=Count('calidad_general'))
            .values_list('calidad_general', 'count')
        )
        
        # Contar empresas únicas
        empresas_count = queryset.values('empresa').distinct().count()
        
        return {
            'total_registros': total_registros,
            'registros_aprobados': registros_aprobados,
            'registros_rechazados': registros_rechazados,
            'promedio_temperatura': promedio_temperatura,
            'promedio_humedad': promedio_humedad,
            'promedio_ph': promedio_ph,
            'calidad_breakdown': calidad_breakdown,
            'empresas_count': empresas_count
        }
