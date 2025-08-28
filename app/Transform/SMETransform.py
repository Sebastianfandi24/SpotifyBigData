

import pandas as pd
import numpy as np

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

	def clean_data(self):
		"""
		Limpia los datos utilizando estrategias basadas en la media, mediana y moda.
		Returns:
			pd.DataFrame: Datos limpios
		"""
		# Rellenar valores faltantes con la mediana en columnas numéricas
		numeric_columns = self.data.select_dtypes(include=[np.number]).columns
		for col in numeric_columns:
			self.data[col] = self.data[col].fillna(self.data[col].median())

		# Rellenar valores faltantes con la moda en columnas no numéricas
		non_numeric_columns = self.data.select_dtypes(exclude=[np.number]).columns
		for col in non_numeric_columns:
			most_frequent = self.data[col].mode()
			if len(most_frequent) > 0:
				self.data[col] = self.data[col].fillna(most_frequent[0])

		return self.data

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
