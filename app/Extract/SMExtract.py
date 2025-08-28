
import pandas as pd
import numpy as np
from app.Transform.SMETransform import DataClean

class SpotifyExtractor:
    def __init__(self, csv_path: str):
        self.csv = csv_path
        self.data = None

    def queries(self):
        self.data = pd.read_csv(self.csv)
        return self.data

    def response(self):
        if self.data is None:
            raise ValueError("Los datos no han sido cargados. Llama al método queries() primero.")
        return self.data.head(5)

    def extract_and_clean(self):
        """
        Extrae los datos del archivo CSV y los limpia utilizando la clase DataClean.
        
        Returns:
            pd.DataFrame: Datos limpios
        """
        # Extraer los datos
        self.queries()

        # Limpiar los datos
        cleaner = DataClean(self.data)
        cleaner.clean_data()

        # Actualizar los datos con los datos limpios
        self.data = cleaner.get_cleaned_data()
        return self.data