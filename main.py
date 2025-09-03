from app.Load.SMEloader import Loader
from app.Extract.SMExtract import SpotifyExtractor
from app.Transform.SMETransform import DataClean

def main():
	csv_path = 'app/Extract/Files/spotify-2023.csv'
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
	# Mostrar los primeros 5 registros limpios
	print("\n=== 5 REGISTROS LIMPIOS ===")
	print(cleaned_data.head(5))

	# Cargar los datos limpios
	loader = Loader(cleaned_data)
	loader.to_sqlite()

if __name__ == "__main__":
	main()
