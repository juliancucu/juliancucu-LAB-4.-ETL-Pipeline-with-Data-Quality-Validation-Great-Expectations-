import pandas as pd

def clean_data(df):
    print("\n--- INICIANDO LIMPIEZA DE DATOS (TASK D) ---")
    
    # Trabajamos sobre una copia para no alterar el original
    df_clean = df.copy()

    # UNICIDAD: Eliminar duplicados basados en el invoice_id
    df_clean = df_clean.drop_duplicates(subset=['invoice_id'], keep='first')

    # COMPLETITUD: Eliminar filas donde customer_id o invoice_date son nulos
    df_clean = df_clean.dropna(subset=['customer_id', 'invoice_date'])

    # VALIDEZ: Arreglar cantidades y precios
    # Convertimos a valor absoluto para quitar los negativos
    df_clean['quantity'] = df_clean['quantity'].abs()
    df_clean['price'] = df_clean['price'].abs()
    # Filtramos para asegurarnos de que no queden ceros
    df_clean = df_clean[(df_clean['quantity'] >= 1) & (df_clean['price'] >= 0.01)]

    # CONSISTENCIA: Estandarizar nombres de países
    # Convertimos todo a minúsculas y luego la primera letra en mayúscula (ej. 'ecuador' -> 'Ecuador')
    df_clean['country'] = df_clean['country'].str.title()
    # Reemplazamos abreviaturas
    country_map = {'Co': 'Colombia', 'Pe': 'Peru', 'Ec': 'Ecuador', 'Cl': 'Chile'}
    df_clean['country'] = df_clean['country'].replace(country_map)

    # PUNTUALIDAD/FORMATO: Arreglar fechas
    # Convertimos todas las fechas mezcladas a un objeto datetime real de pandas
    df_clean['invoice_date'] = pd.to_datetime(df_clean['invoice_date'], format="mixed", errors='coerce')
    # Filtramos fechas en el futuro (mayores a 2023-12-31)
    df_clean = df_clean[df_clean['invoice_date'] <= pd.Timestamp('2023-12-31')]
    # Volvemos a convertir al texto estricto YYYY-MM-DD que pide Great Expectations
    df_clean['invoice_date'] = df_clean['invoice_date'].dt.strftime('%Y-%m-%d')

    # CONSISTENCIA LÓGICA: Recalcular el total_revenue
    df_clean['total_revenue'] = df_clean['quantity'] * df_clean['price']

    print(f"Filas originales: {len(df)}")
    print(f"Filas después de la limpieza: {len(df_clean)}")
    
    return df_clean