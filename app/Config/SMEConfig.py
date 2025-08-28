import os

# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ruta al archivo CSV original
CSV_PATH = os.path.join(BASE_DIR, 'Extract', 'files', 'spotify-2023.csv')

# Ruta para guardar datos limpios
CLEANED_DATA_PATH = os.path.join(BASE_DIR, 'data', 'spotify-2023-cleaned.csv')

# Puedes agregar más configuraciones aquí

