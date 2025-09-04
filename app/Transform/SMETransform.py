import pandas as pd
import numpy as np
import re
from datetime import datetime

class DataClean:
	def __init__(self, data: pd.DataFrame):
		"""
		Inicializa la clase DataClean con un DataFrame.
		Args:
			data (pd.DataFrame): Los datos a limpiar
		"""
		self.data = data.copy()
		self.original_shape = data.shape
		self.null_info = {}
		self.duplicates_info = {}
		self.outliers_info = {}
		self.quality_report = {}

	def remove_duplicates(self, subset=None, keep='first'):
		"""
		Elimina registros duplicados del dataset.
		Args:
			subset (list): Columnas a considerar para identificar duplicados
			keep (str): Qué duplicado mantener ('first', 'last', False)
		Returns:
			dict: Información sobre duplicados removidos
		"""
		initial_rows = len(self.data)
		
		# Identificar duplicados
		duplicates_mask = self.data.duplicated(subset=subset, keep=False)
		duplicates_count = duplicates_mask.sum()
		
		# Remover duplicados
		self.data = self.data.drop_duplicates(subset=subset, keep=keep)
		
		final_rows = len(self.data)
		removed_rows = initial_rows - final_rows
		
		self.duplicates_info = {
			'initial_rows': initial_rows,
			'final_rows': final_rows,
			'duplicates_found': duplicates_count,
			'duplicates_removed': removed_rows,
			'percentage_removed': (removed_rows / initial_rows) * 100 if initial_rows > 0 else 0
		}
		
		return self.duplicates_info

	def handle_missing_data(self, strategy='auto', threshold=0.5):
		"""
		Maneja datos ausentes con diferentes estrategias.
		Args:
			strategy (str): 'auto', 'drop', 'fill', 'interpolate'
			threshold (float): Umbral para eliminar columnas (% de datos faltantes)
		Returns:
			pd.DataFrame: Datos procesados
		"""
		if strategy == 'auto':
			# Estrategia automática basada en el porcentaje de datos faltantes
			null_percentages = (self.data.isnull().sum() / len(self.data))
			
			# Eliminar columnas con más del umbral de datos faltantes
			cols_to_drop = null_percentages[null_percentages > threshold].index
			if len(cols_to_drop) > 0:
				self.data = self.data.drop(columns=cols_to_drop)
				print(f"Columnas eliminadas por exceso de valores nulos: {list(cols_to_drop)}")
			
			# Aplicar limpieza estándar al resto
			return self.clean_data()
		
		elif strategy == 'drop':
			self.data = self.data.dropna()
		
		elif strategy == 'fill':
			return self.clean_data()
		
		elif strategy == 'interpolate':
			numeric_columns = self.data.select_dtypes(include=[np.number]).columns
			for col in numeric_columns:
				self.data[col] = self.data[col].interpolate()
		
		return self.data

	def remove_unwanted_values(self, remove_outliers=True, clean_text=True, standardize_formats=True):
		"""
		Elimina valores no deseados del dataset.
		Args:
			remove_outliers (bool): Si eliminar outliers
			clean_text (bool): Si limpiar texto
			standardize_formats (bool): Si estandarizar formatos
		Returns:
			dict: Resumen de limpieza
		"""
		initial_rows = len(self.data)
		outliers_removed = 0
		
		# 1. Eliminar outliers usando IQR
		if remove_outliers:
			numeric_columns = self.data.select_dtypes(include=[np.number]).columns
			for col in numeric_columns:
				Q1 = self.data[col].quantile(0.25)
				Q3 = self.data[col].quantile(0.75)
				IQR = Q3 - Q1
				lower_bound = Q1 - 1.5 * IQR
				upper_bound = Q3 + 1.5 * IQR
				
				outliers_mask = (self.data[col] < lower_bound) | (self.data[col] > upper_bound)
				outliers_count = outliers_mask.sum()
				outliers_removed += outliers_count
				
				# Remover outliers
				self.data = self.data[~outliers_mask]
		
		# 2. Limpiar texto
		if clean_text:
			text_columns = self.data.select_dtypes(include=['object']).columns
			for col in text_columns:
				if self.data[col].dtype == 'object':
					# Eliminar espacios extra
					self.data[col] = self.data[col].astype(str).str.strip()
					# Reemplazar múltiples espacios con uno solo
					self.data[col] = self.data[col].str.replace(r'\s+', ' ', regex=True)
					# Eliminar caracteres especiales no deseados (opcional)
					self.data[col] = self.data[col].str.replace(r'[^\w\s\-\.\,]', '', regex=True)
		
		# 3. Estandarizar formatos
		if standardize_formats:
			text_columns = self.data.select_dtypes(include=['object']).columns
			for col in text_columns:
				if self.data[col].dtype == 'object':
					# Convertir a título (primera letra mayúscula)
					self.data[col] = self.data[col].str.title()
		
		final_rows = len(self.data)
		
		self.outliers_info = {
			'initial_rows': initial_rows,
			'final_rows': final_rows,
			'outliers_removed': outliers_removed,
			'total_removed': initial_rows - final_rows,
			'percentage_removed': ((initial_rows - final_rows) / initial_rows) * 100 if initial_rows > 0 else 0
		}
		
		return self.outliers_info

	def quality_assessment(self):
		"""
		Realiza un control de calidad (QA) completo para Big Data.
		Returns:
			dict: Reporte completo de calidad de datos
		"""
		current_shape = self.data.shape
		
		# 1. Métricas básicas
		basic_metrics = {
			'total_rows': current_shape[0],
			'total_columns': current_shape[1],
			'total_cells': current_shape[0] * current_shape[1],
			'memory_usage_mb': self.data.memory_usage(deep=True).sum() / 1024 / 1024
		}
		
		# 2. Análisis de completitud
		null_counts = self.data.isnull().sum()
		completeness = {
			'total_nulls': null_counts.sum(),
			'null_percentage': (null_counts.sum() / basic_metrics['total_cells']) * 100,
			'complete_rows': len(self.data.dropna()),
			'completeness_score': (basic_metrics['total_cells'] - null_counts.sum()) / basic_metrics['total_cells'] * 100
		}
		
		# 3. Análisis de unicidad
		uniqueness = {}
		for col in self.data.columns:
			unique_count = self.data[col].nunique()
			total_count = len(self.data[col].dropna())
			uniqueness[col] = {
				'unique_values': unique_count,
				'uniqueness_ratio': unique_count / total_count if total_count > 0 else 0
			}
		
		# 4. Análisis de tipos de datos
		data_types = {
			'numeric_columns': len(self.data.select_dtypes(include=[np.number]).columns),
			'text_columns': len(self.data.select_dtypes(include=['object']).columns),
			'datetime_columns': len(self.data.select_dtypes(include=['datetime']).columns),
			'boolean_columns': len(self.data.select_dtypes(include=['bool']).columns)
		}
		
		# 5. Análisis de valores atípicos
		outliers_analysis = {}
		numeric_columns = self.data.select_dtypes(include=[np.number]).columns
		for col in numeric_columns:
			Q1 = self.data[col].quantile(0.25)
			Q3 = self.data[col].quantile(0.75)
			IQR = Q3 - Q1
			lower_bound = Q1 - 1.5 * IQR
			upper_bound = Q3 + 1.5 * IQR
			outliers_count = ((self.data[col] < lower_bound) | (self.data[col] > upper_bound)).sum()
			outliers_analysis[col] = {
				'outliers_count': outliers_count,
				'outliers_percentage': (outliers_count / len(self.data)) * 100
			}
		
		# 6. Score general de calidad
		quality_score = (
			completeness['completeness_score'] * 0.4 +  # 40% completitud
			min(100, (1 - completeness['null_percentage']/100) * 100) * 0.3 +  # 30% ausencia de nulos
			min(100, (current_shape[0] / max(1, self.original_shape[0])) * 100) * 0.3  # 30% preservación de datos
		)
		
		self.quality_report = {
			'timestamp': datetime.now().isoformat(),
			'basic_metrics': basic_metrics,
			'completeness': completeness,
			'uniqueness': uniqueness,
			'data_types': data_types,
			'outliers_analysis': outliers_analysis,
			'overall_quality_score': quality_score,
			'recommendations': self._generate_recommendations(completeness, outliers_analysis)
		}
		
		return self.quality_report

	def _generate_recommendations(self, completeness, outliers_analysis):
		"""
		Genera recomendaciones basadas en el análisis de calidad.
		"""
		recommendations = []
		
		if completeness['null_percentage'] > 10:
			recommendations.append("Considerar estrategias adicionales para manejar valores nulos")
		
		if completeness['completeness_score'] < 80:
			recommendations.append("La completitud de los datos es baja, revisar fuentes de datos")
		
		high_outlier_cols = [col for col, info in outliers_analysis.items() 
						   if info['outliers_percentage'] > 5]
		if high_outlier_cols:
			recommendations.append(f"Revisar outliers en columnas: {', '.join(high_outlier_cols)}")
		
		if len(recommendations) == 0:
			recommendations.append("Los datos tienen buena calidad general")
		
		return recommendations

	def comprehensive_clean(self, remove_duplicates=True, handle_missing=True, 
						  remove_unwanted=True, run_qa=True):
		"""
		Ejecuta un proceso completo de limpieza de datos.
		Args:
			remove_duplicates (bool): Eliminar duplicados
			handle_missing (bool): Manejar datos faltantes
			remove_unwanted (bool): Eliminar valores no deseados
			run_qa (bool): Ejecutar control de calidad
		Returns:
			dict: Resumen completo del proceso
		"""
		print("=== INICIANDO LIMPIEZA COMPLETA DE DATOS ===")
		
		results = {
			'initial_shape': self.original_shape,
			'steps_performed': []
		}
		
		# Paso 1: Eliminar duplicados
		if remove_duplicates:
			print("1. Eliminando duplicados...")
			dup_info = self.remove_duplicates()
			results['duplicates'] = dup_info
			results['steps_performed'].append('remove_duplicates')
			print(f"   Duplicados eliminados: {dup_info['duplicates_removed']}")
		
		# Paso 2: Manejar datos faltantes
		if handle_missing:
			print("2. Manejando datos faltantes...")
			self.handle_missing_data(strategy='auto')
			results['steps_performed'].append('handle_missing_data')
		
		# Paso 3: Eliminar valores no deseados
		if remove_unwanted:
			print("3. Eliminando valores no deseados...")
			unwanted_info = self.remove_unwanted_values()
			results['unwanted_values'] = unwanted_info
			results['steps_performed'].append('remove_unwanted_values')
			print(f"   Outliers eliminados: {unwanted_info['outliers_removed']}")
		
		# Paso 4: Control de calidad
		if run_qa:
			print("4. Ejecutando control de calidad...")
			qa_report = self.quality_assessment()
			results['quality_assessment'] = qa_report
			results['steps_performed'].append('quality_assessment')
			print(f"   Score de calidad: {qa_report['overall_quality_score']:.2f}%")
		
		results['final_shape'] = self.data.shape
		results['total_rows_removed'] = self.original_shape[0] - self.data.shape[0]
		results['total_columns_removed'] = self.original_shape[1] - self.data.shape[1]
		
		print("=== LIMPIEZA COMPLETADA ===")
		print(f"Forma original: {results['initial_shape']}")
		print(f"Forma final: {results['final_shape']}")
		print(f"Filas eliminadas: {results['total_rows_removed']}")
		print(f"Columnas eliminadas: {results['total_columns_removed']}")
		
		return results

	def print_quality_report(self):
		"""
		Imprime un reporte detallado de calidad de datos.
		"""
		if not self.quality_report:
			self.quality_assessment()
		
		report = self.quality_report
		print("=== REPORTE DE CALIDAD DE DATOS ===")
		print(f"Timestamp: {report['timestamp']}")
		print(f"Score General de Calidad: {report['overall_quality_score']:.2f}%")
		
		print("\n--- MÉTRICAS BÁSICAS ---")
		basic = report['basic_metrics']
		print(f"Filas: {basic['total_rows']:,}")
		print(f"Columnas: {basic['total_columns']}")
		print(f"Uso de memoria: {basic['memory_usage_mb']:.2f} MB")
		
		print("\n--- COMPLETITUD ---")
		comp = report['completeness']
		print(f"Valores nulos: {comp['total_nulls']:,} ({comp['null_percentage']:.2f}%)")
		print(f"Filas completas: {comp['complete_rows']:,}")
		print(f"Score de completitud: {comp['completeness_score']:.2f}%")
		
		print("\n--- RECOMENDACIONES ---")
		for i, rec in enumerate(report['recommendations'], 1):
			print(f"{i}. {rec}")

	def analyze_null_values(self):
		"""
		Analiza los valores nulos en el dataset.
		Returns:
			dict: Información detallada sobre valores nulos
		"""
		null_counts = self.data.isnull().sum()
		null_percentages = (null_counts / len(self.data)) * 100
		self.null_info = {
			'total_rows': len(self.data),
			'total_columns': len(self.data.columns),
			'columns_with_nulls': null_counts[null_counts > 0].to_dict(),
			'null_percentages': null_percentages[null_percentages > 0].to_dict(),
			'total_null_values': null_counts.sum(),
			'columns_names': list(self.data.columns)
		}
		return self.null_info

	def clean_specific_numeric_columns(self):
		"""
		🎵 Limpia columnas específicas que deben ser numéricas, reemplazando valores no numéricos con la mediana.
		
		Columnas a procesar:
		- artist_count, released_year, released_month, released_day
		- in_spotify_playlists, in_spotify_charts, streams
		- in_apple_playlists, in_apple_charts
		- in_deezer_playlists, in_deezer_charts, in_shazam_charts
		- bpm, danceability_%, valence_%, energy_%
		- acousticness_%, instrumentalness_%, liveness_%, speechiness_%
		
		Returns:
			dict: Resumen del proceso de limpieza
		"""
		print("🎵 Limpiando columnas numéricas específicas de Spotify...")
		
		# Lista de columnas que deben ser numéricas
		target_numeric_columns = [
			'artist_count',
			'released_year',
			'released_month', 
			'released_day',
			'in_spotify_playlists',
			'in_spotify_charts',
			'streams',
			'in_apple_playlists',
			'in_apple_charts',
			'in_deezer_playlists',
			'in_deezer_charts',
			'in_shazam_charts',
			'bpm',
			'danceability_%',
			'valence_%',
			'energy_%',
			'acousticness_%',
			'instrumentalness_%',
			'liveness_%',
			'speechiness_%'
		]
		
		cleaning_summary = {
			'columns_processed': [],
			'columns_not_found': [],
			'total_conversions': 0,
			'total_filled': 0,
			'column_details': {}
		}
		
		print(f"🎯 Procesando {len(target_numeric_columns)} columnas específicas...")
		
		for col in target_numeric_columns:
			# Verificar si la columna existe en el dataset
			if col not in self.data.columns:
				cleaning_summary['columns_not_found'].append(col)
				print(f"   ⚠️  Columna '{col}' no encontrada en el dataset")
				continue
			
			print(f"\n🔧 Procesando columna: '{col}'")
			
			# Estadísticas iniciales
			initial_nulls = self.data[col].isna().sum()
			initial_count = len(self.data[col])
			initial_dtype = str(self.data[col].dtype)
			
			print(f"   📊 Estado inicial: {initial_count:,} valores, {initial_nulls:,} nulos, tipo: {initial_dtype}")
			
			# Paso 1: Limpiar la columna si no es numérica
			if not pd.api.types.is_numeric_dtype(self.data[col]):
				print(f"   🔄 Convirtiendo columna de tipo {initial_dtype} a numérico...")
				
				# Convertir a string y limpiar caracteres especiales
				self.data[col] = self.data[col].astype(str)
				
				# Limpiar caracteres comunes que interfieren con la conversión numérica
				self.data[col] = self.data[col].str.replace(',', '', regex=False)  # Comas
				self.data[col] = self.data[col].str.replace(' ', '', regex=False)  # Espacios
				self.data[col] = self.data[col].str.replace('$', '', regex=False)  # Símbolos de moneda
				self.data[col] = self.data[col].str.replace('%', '', regex=False)  # Símbolos de porcentaje
				
				# Reemplazar valores como 'nan', 'None', etc.
				self.data[col] = self.data[col].replace(['nan', 'None', 'null', 'NULL', '', 'N/A', 'n/a', 'NaN'], np.nan)
				
				# Convertir a numérico
				self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
			
			# Paso 2: Contar conversiones
			after_conversion_nulls = self.data[col].isna().sum()
			conversions = after_conversion_nulls - initial_nulls
			
			if conversions > 0:
				print(f"   ⚠️  {conversions:,} valores no numéricos convertidos a NaN")
				cleaning_summary['total_conversions'] += conversions
			
			# Paso 3: Calcular mediana y rellenar nulos
			valid_values = self.data[col].dropna()
			if len(valid_values) > 0:
				median_value = valid_values.median()
				
				# Rellenar nulos con mediana
				filled_count = after_conversion_nulls
				self.data[col] = self.data[col].fillna(median_value)
				
				print(f"   ✅ {filled_count:,} valores rellenados con mediana: {median_value:.2f}")
				cleaning_summary['total_filled'] += filled_count
				
				# Estadísticas finales
				final_nulls = self.data[col].isna().sum()
				final_dtype = str(self.data[col].dtype)
				final_min = self.data[col].min()
				final_max = self.data[col].max()
				
				column_detail = {
					'initial_nulls': initial_nulls,
					'conversions': conversions,
					'filled_count': filled_count,
					'final_nulls': final_nulls,
					'median_used': median_value,
					'final_range': f"{final_min:.2f} - {final_max:.2f}",
					'final_dtype': final_dtype
				}
				
				cleaning_summary['column_details'][col] = column_detail
				cleaning_summary['columns_processed'].append(col)
				
				print(f"   📈 Rango final: {final_min:.2f} - {final_max:.2f}")
				
			else:
				print(f"   ❌ No hay valores numéricos válidos en '{col}'")
				cleaning_summary['columns_not_found'].append(col)
		
		# Resumen final
		processed_count = len(cleaning_summary['columns_processed'])
		not_found_count = len(cleaning_summary['columns_not_found'])
		
		print(f"\n📊 RESUMEN DE LIMPIEZA NUMÉRICA:")
		print(f"   ✅ Columnas procesadas exitosamente: {processed_count}")
		print(f"   ❌ Columnas no encontradas/problemáticas: {not_found_count}")
		print(f"   🔄 Total de conversiones: {cleaning_summary['total_conversions']:,}")
		print(f"   📝 Total de valores rellenados: {cleaning_summary['total_filled']:,}")
		
		if cleaning_summary['columns_not_found']:
			print(f"   ⚠️  Columnas problemáticas: {', '.join(cleaning_summary['columns_not_found'])}")
		
		return cleaning_summary
	
	def clean_data(self):
		"""
		Limpia los datos utilizando estrategias basadas en la mediana y moda.
		Incluye limpieza específica de columnas numéricas de Spotify.
		Returns:
			pd.DataFrame: Datos limpios
		"""
		print("🧹 Iniciando limpieza completa de datos...")
		
		# Paso 1: Limpiar columnas numéricas específicas de Spotify
		print("\n🎵 Paso 1: Limpieza de columnas numéricas específicas")
		specific_cleaning = self.clean_specific_numeric_columns()
		
		# Paso 2: Limpiar columnas numéricas restantes
		print("\n🔢 Paso 2: Limpieza de columnas numéricas restantes")
		numeric_columns = self.data.select_dtypes(include=[np.number]).columns
		processed_columns = specific_cleaning['columns_processed']
		
		remaining_numeric = [col for col in numeric_columns if col not in processed_columns]
		
		if remaining_numeric:
			print(f"   Procesando {len(remaining_numeric)} columnas numéricas adicionales...")
			for col in remaining_numeric:
				nulls_count = self.data[col].isna().sum()
				if nulls_count > 0:
					median_val = self.data[col].median()
					self.data[col] = self.data[col].fillna(median_val)
					print(f"   ✅ {col}: {nulls_count} nulos → mediana ({median_val:.2f})")
		else:
			print("   ✅ Todas las columnas numéricas ya fueron procesadas")

		# Paso 3: Limpiar columnas de texto
		print("\n📝 Paso 3: Limpieza de columnas de texto")
		non_numeric_columns = self.data.select_dtypes(exclude=[np.number]).columns
		
		if len(non_numeric_columns) > 0:
			print(f"   Procesando {len(non_numeric_columns)} columnas de texto...")
			for col in non_numeric_columns:
				nulls_count = self.data[col].isna().sum()
				if nulls_count > 0:
					most_frequent = self.data[col].mode()
					if len(most_frequent) > 0:
						mode_val = most_frequent[0]
						self.data[col] = self.data[col].fillna(mode_val)
						print(f"   ✅ {col}: {nulls_count} nulos → moda ('{mode_val}')")
		else:
			print("   ✅ No hay columnas de texto para procesar")

		print("\n🎯 Limpieza de datos completada exitosamente")
		return self.datas
	
	def validate_specific_numeric_columns(self):
		"""
		✅ Valida que las columnas específicas de Spotify estén correctamente convertidas a numéricas.
		
		Returns:
			dict: Resultado de la validación con detalles por columna
		"""
		print("✅ Validando columnas numéricas específicas...")
		
		target_columns = [
			'artist_count', 'released_year', 'released_month', 'released_day',
			'in_spotify_playlists', 'in_spotify_charts', 'streams',
			'in_apple_playlists', 'in_apple_charts',
			'in_deezer_playlists', 'in_deezer_charts', 'in_shazam_charts',
			'bpm', 'danceability_%', 'valence_%', 'energy_%',
			'acousticness_%', 'instrumentalness_%', 'liveness_%', 'speechiness_%'
		]
		
		validation_results = {
			'valid_columns': [],
			'invalid_columns': [],
			'missing_columns': [],
			'column_details': {},
			'overall_status': True
		}
		
		for col in target_columns:
			if col not in self.data.columns:
				validation_results['missing_columns'].append(col)
				validation_results['overall_status'] = False
				print(f"   ❌ Columna '{col}' no encontrada")
				continue
			
			# Verificar si es numérica
			is_numeric = pd.api.types.is_numeric_dtype(self.data[col])
			has_nulls = self.data[col].isna().any()
			null_count = self.data[col].isna().sum()
			
			# Verificar valores infinitos o problemáticos
			has_infinite = False
			infinite_count = 0
			if is_numeric:
				has_infinite = np.isinf(self.data[col]).any()
				infinite_count = np.isinf(self.data[col]).sum()
			
			column_validation = {
				'is_numeric': is_numeric,
				'has_nulls': has_nulls,
				'null_count': null_count,
				'has_infinite': has_infinite,
				'infinite_count': infinite_count,
				'dtype': str(self.data[col].dtype),
				'is_valid': is_numeric and not has_nulls and not has_infinite
			}
			
			if is_numeric:
				column_validation.update({
					'min_value': float(self.data[col].min()),
					'max_value': float(self.data[col].max()),
					'median_value': float(self.data[col].median())
				})
			
			validation_results['column_details'][col] = column_validation
			
			if column_validation['is_valid']:
				validation_results['valid_columns'].append(col)
				print(f"   ✅ {col}: Válida (rango: {column_validation.get('min_value', 'N/A'):.1f} - {column_validation.get('max_value', 'N/A'):.1f})")
			else:
				validation_results['invalid_columns'].append(col)
				validation_results['overall_status'] = False
				issues = []
				if not is_numeric:
					issues.append("no numérica")
				if has_nulls:
					issues.append(f"{null_count} nulos")
				if has_infinite:
					issues.append(f"{infinite_count} infinitos")
				print(f"   ❌ {col}: Problemática ({', '.join(issues)})")
		
		# Resumen final
		valid_count = len(validation_results['valid_columns'])
		invalid_count = len(validation_results['invalid_columns'])
		missing_count = len(validation_results['missing_columns'])
		total_target = len(target_columns)
		
		print(f"\n📊 RESUMEN DE VALIDACIÓN:")
		print(f"   ✅ Columnas válidas: {valid_count}/{total_target}")
		print(f"   ❌ Columnas problemáticas: {invalid_count}")
		print(f"   🔍 Columnas faltantes: {missing_count}")
		
		status_icon = "✅" if validation_results['overall_status'] else "❌"
		status_text = "EXITOSA" if validation_results['overall_status'] else "FALLÓ"
		print(f"   🎯 Validación general: {status_icon} {status_text}")
		
		return validation_results
	
	def get_numeric_columns_summary(self):
		"""
		📊 Obtiene un resumen estadístico de todas las columnas numéricas específicas.
		
		Returns:
			dict: Estadísticas detalladas por columna
		"""
		target_columns = [
			'artist_count', 'released_year', 'released_month', 'released_day',
			'in_spotify_playlists', 'in_spotify_charts', 'streams',
			'in_apple_playlists', 'in_apple_charts',
			'in_deezer_playlists', 'in_deezer_charts', 'in_shazam_charts',
			'bpm', 'danceability_%', 'valence_%', 'energy_%',
			'acousticness_%', 'instrumentalness_%', 'liveness_%', 'speechiness_%'
		]
		
		summary = {
			'column_statistics': {},
			'overall_stats': {
				'total_target_columns': len(target_columns),
				'found_columns': 0,
				'numeric_columns': 0,
				'complete_columns': 0
			}
		}
		
		print("📊 Generando resumen estadístico de columnas numéricas...")
		
		for col in target_columns:
			if col in self.data.columns:
				summary['overall_stats']['found_columns'] += 1
				
				if pd.api.types.is_numeric_dtype(self.data[col]):
					summary['overall_stats']['numeric_columns'] += 1
					
					# Estadísticas detalladas
					col_stats = {
						'count': len(self.data[col]),
						'non_null_count': self.data[col].notna().sum(),
						'null_count': self.data[col].isna().sum(),
						'null_percentage': (self.data[col].isna().sum() / len(self.data[col])) * 100,
						'dtype': str(self.data[col].dtype),
						'min': float(self.data[col].min()),
						'max': float(self.data[col].max()),
						'median': float(self.data[col].median()),
						'mean': float(self.data[col].mean()),
						'std': float(self.data[col].std()),
						'unique_values': self.data[col].nunique()
					}
					
					if col_stats['null_count'] == 0:
						summary['overall_stats']['complete_columns'] += 1
					
					summary['column_statistics'][col] = col_stats
				else:
					summary['column_statistics'][col] = {
						'error': 'Columna no numérica',
						'dtype': str(self.data[col].dtype)
					}
			else:
				summary['column_statistics'][col] = {'error': 'Columna no encontrada'}
		
		print(f"📈 Resumen completado: {summary['overall_stats']['numeric_columns']}/{summary['overall_stats']['found_columns']} columnas son numéricas")
		
		return summary

	def get_cleaning_summary(self):
		"""
		Obtiene un resumen del proceso de limpieza.
		Returns:
			dict: Resumen del proceso de limpieza
		"""
		current_shape = self.data.shape
		summary = {
			'original_shape': self.original_shape,
			'current_shape': current_shape,
			'rows_removed': self.original_shape[0] - current_shape[0],
			'columns_removed': self.original_shape[1] - current_shape[1],
			'remaining_nulls': self.data.isnull().sum().sum(),
			'data_quality_score': ((self.data.notna().sum().sum()) / (current_shape[0] * current_shape[1])) * 100
		}
		return summary

	def get_cleaned_data(self):
		"""
		Retorna los datos limpios.
		Returns:
			pd.DataFrame: Datos después de la limpieza
		"""
		return self.data

	def print_null_analysis(self):
		"""
		Imprime un análisis detallado de los valores nulos.
		"""
		info = self.analyze_null_values()
		print("=== ANÁLISIS DE VALORES NULOS ===")
		print(f"Total de filas: {info['total_rows']}")
		print(f"Total de columnas: {info['total_columns']}")
		print(f"Total de valores nulos: {info['total_null_values']}")
		print("\nColumnas con valores nulos:")
		if info['columns_with_nulls']:
			for col, count in info['columns_with_nulls'].items():
				percentage = info['null_percentages'][col]
				print(f"  - {col}: {count} nulos ({percentage:.2f}%)")
		else:
			print("  ¡No se encontraron valores nulos!")
		print(f"\nColumnas disponibles: {', '.join(info['columns_names'])}")
