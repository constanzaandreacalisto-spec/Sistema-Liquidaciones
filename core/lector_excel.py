import pandas as pd

class LectorExcel:
    def __init__(self, archivo_path):
        self.archivo_path = archivo_path

    def leer_datos(self, sheet_name=0):
        """Lee el archivo Excel y limpia las columnas vacías o de parámetros anexos."""
        try:
            df = pd.read_excel(self.archivo_path, sheet_name=sheet_name)
            
            # Eliminar columnas que comiencen con 'Unnamed' o que correspondan a bloques de parámetros
            df = df.loc[:, ~df.columns.str.contains('^Unnamed|PARÁMETROS', case=False, na=False)]
            
            # Filtrar filas totalmente vacías
            df = df.dropna(how='all')
            
            return df
        except Exception as e:
            raise Exception(f"Error al leer el archivo Excel: {e}")