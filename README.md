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


## Proceso detallado de limpieza y llenado de datos

La limpieza de datos se realiza en el módulo `Transform/SMETransform.py` mediante la clase `DataClean`. El proceso sigue estos pasos:

1. **Análisis de valores nulos**
  - Se identifican todas las columnas que contienen valores nulos.
  - Se calcula el número y porcentaje de valores nulos por columna.
  - Se genera un reporte con el total de filas, columnas, columnas afectadas y el porcentaje de nulos.

2. **Llenado de valores nulos**
  - **Columnas numéricas:**  Los valores nulos se rellenan usando la mediana de cada columna. Esto ayuda a evitar que valores extremos (outliers) afecten el resultado, ya que la mediana es menos sensible a ellos que la media.
  - **Columnas categóricas (no numéricas):**  Los valores nulos se rellenan usando la moda (el valor más frecuente) de cada columna. Esto asegura que los datos faltantes se completan con el valor más representativo de la columna.

3. **Resumen de limpieza**
  - Se calcula la forma original y final del DataFrame (filas y columnas).
  - Se reporta cuántos valores nulos quedan tras la limpieza (debería ser cero si todas las columnas fueron tratadas).
  - Se calcula un “score de calidad de datos”, que representa el porcentaje de datos no nulos tras la limpieza.

4. **Visualización y validación**
  - El pipeline muestra en consola el análisis de nulos antes de limpiar, el resumen de limpieza y los primeros 5 registros limpios para validar el resultado.

### Ejemplo de código usado para limpiar los datos

```python
# Rellenar valores faltantes con la mediana en columnas numéricas
numeric_columns = df.select_dtypes(include=[np.number]).columns
for col in numeric_columns:
   df[col] = df[col].fillna(df[col].median())

# Rellenar valores faltantes con la moda en columnas no numéricas
non_numeric_columns = df.select_dtypes(exclude=[np.number]).columns
for col in non_numeric_columns:
   most_frequent = df[col].mode()
   if len(most_frequent) > 0:
      df[col] = df[col].fillna(most_frequent[0])
```

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
