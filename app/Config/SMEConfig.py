import os

# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ruta al archivo CSV original
CSV_PATH = os.path.join(BASE_DIR, 'Extract', 'files', 'spotify-2023.csv')

# Ruta para guardar datos limpios
CLEANED_DATA_PATH = os.path.join(BASE_DIR, 'data', 'spotify-2023-cleaned.csv')

# Puedes agregar más configuraciones aquí

class Config:
    """
    Clase de configuración para rutas y parámetros del ETL.
    """
    INPUT_PATH = 'app/Extract/Files/spotify-2023.csv'
    SQLITE_DB_PATH = 'app/Extract/Files/etl_data.db'
    SQLITE_TABLE = 'spotify_data_clean'
