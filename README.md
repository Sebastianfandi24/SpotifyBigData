# SpotifyBigData

Pipeline ETL modular para procesar datos de Spotify, inspirado en el proyecto ETLProject y usando código de Spotify-Most-Streamed.

## Estructura del proyecto

```
SpotifyBigData/
├── app/
│   ├── Config/
│   │   └── SMEConfig.py           # Configuración de rutas y parámetros
│   ├── Extract/
│   │   ├── SMExtract.py           # Extracción de datos desde CSV
│   │   ├── Files/
│   │   │   └── spotify-2023.csv   # Archivo original de datos
│   ├── Transform/
│   │   └── SMETransform.py        # Limpieza y transformación de datos
│   ├── Load/
│   │   └── SMEloader.py           # Carga de datos procesados
├── data/                          # Archivos procesados
├── main.py                        # Orquestador del pipeline ETL
├── requirements.txt               # Dependencias
├── .gitignore                     # Exclusión de archivos
```

## Descripción de cada módulo

- **Config/SMEConfig.py**: Define rutas y parámetros globales para el pipeline.
- **Extract/SMExtract.py**: Lee el archivo CSV y lo carga en un DataFrame usando pandas.
- **Transform/SMETransform.py**: Limpia los datos usando la clase `DataClean`, que analiza valores nulos y los rellena con mediana (numéricos) o moda (categóricos). También genera un resumen de limpieza y calidad de datos.
- **Load/SMEloader.py**: Prepara los datos limpios para su uso o exportación.
- **main.py**: Ejecuta el flujo ETL completo, mostrando análisis de nulos, resumen de limpieza y los primeros 5 registros limpios.

## Proceso de limpieza de datos

La clase `DataClean` realiza:
- Análisis de valores nulos por columna.
- Relleno de nulos en columnas numéricas con la mediana.
- Relleno de nulos en columnas categóricas con la moda.
- Generación de un resumen de limpieza y score de calidad de datos.

## Configuración y dependencias

Instala las dependencias usando:
```sh
pip install -r requirements.txt
```

Principales librerías usadas:
- pandas
- numpy

## Ejecución del pipeline

Ejecuta el pipeline desde la raíz del proyecto:
```sh
python3 main.py
```

## Pruebas

- Verifica que el archivo `app/Extract/Files/spotify-2023.csv` exista y tenga datos.
- Al ejecutar `main.py`, se debe mostrar:
  - Análisis de valores nulos
  - Resumen de limpieza
  - 5 registros limpios
- Si hay errores de importación, revisa que las rutas sean correctas y que las dependencias estén instaladas.

## Recomendaciones

- Mantén actualizado el archivo `requirements.txt` usando `pip freeze > requirements.txt`.
- Usa ramas Feature para nuevas funcionalidades y Release para preparar versiones de producción.
- Documenta cualquier cambio importante en el README.md.

## Autor
- Sebastián Fandiño
