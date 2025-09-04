from app.Load.SMEloader import Loader
from app.Extract.SMExtract import SpotifyExtractor
from app.Transform.SMETransform import DataClean
import pandas as pd

def main():
	csv_path = 'app/Extract/Files/spotify-2023.csv'
	
	# Mostrar la cantidad de datos nulos en el CSV original
	original_data = pd.read_csv(csv_path)
	print()
	print("Datos nulos en el CSV original:")
	print(original_data.isnull().sum())
	print()
	
	extractor = SpotifyExtractor(csv_path)
	# Extraer datos originales
	df = extractor.queries()
	# Instanciar DataClean y mostrar análisis de nulos
	data_cleaner = DataClean(df)
	data_cleaner.print_null_analysis()
	# Limpiar datos
	cleaned_data = data_cleaner.clean_data()
	# Mostrar resumen de limpieza
	summary = data_cleaner.get_cleaning_summary()
	print("\n=== RESUMEN DE LIMPIEZA ===")
	print(summary)
	print()
	# Mostrar los primeros 5 registros limpios
	print("\n=== 5 REGISTROS LIMPIOS ===")
	print(cleaned_data.head(5))
	print()

	# Cargar los datos limpios
	loader = Loader(cleaned_data)
	loader.to_sqlite()

if __name__ == "__main__":
	main()
