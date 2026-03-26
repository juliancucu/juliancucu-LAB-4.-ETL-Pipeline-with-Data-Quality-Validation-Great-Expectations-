import pandas as pd
import numpy as np

def clean_data(df):
    print("\n--- INICIANDO LIMPIEZA DE DATOS E IMPUTACIÓN AVANZADA (TASK D) ---")
    
    # Trabajamos sobre una copia para no alterar el original
    df_clean = df.copy()

    # Eliminar duplicados basados en el invoice_id
    df_clean = df_clean.drop_duplicates(subset=['invoice_id'], keep='first')

    # COMPLETITUD E IMPUTACIÓN: 
    # Crear IDs únicos y secuenciales para los nulos
    max_id = df_clean['customer_id'].max()
    if pd.isna(max_id):
        max_id = 100000 # Valor base por si no hubiera ninguno
        
    missing_customers_mask = df_clean['customer_id'].isnull()
    num_missing = missing_customers_mask.sum()
    
    if num_missing > 0:
        nuevos_ids = np.arange(max_id + 1, max_id + 1 + num_missing)
        df_clean.loc[missing_customers_mask, 'customer_id'] = nuevos_ids

    # Rellenamos nulos con la transacción anterior/siguiente
    df_clean['invoice_date'] = df_clean['invoice_date'].ffill().bfill()

    # Arreglar cantidades y precios
    df_clean = df_clean[df_clean['price'] >= 0.01]
    df_clean = df_clean[df_clean['quantity'] >= 1]

    # Estandarizar nombres de países
    # Convertimos todo a minúsculas y luego la primera letra en mayúscula 
    df_clean['country'] = df_clean['country'].str.title()
    # Reemplazamos abreviaturas
    country_map = {'Co': 'Colombia', 'Pe': 'Peru', 'Ec': 'Ecuador', 'Cl': 'Chile'}
    df_clean['country'] = df_clean['country'].replace(country_map)

    #Arreglar fechas
    # Convertimos todas las fechas mezcladas a un objeto datetime real de pandas
    df_clean['invoice_date'] = pd.to_datetime(df_clean['invoice_date'], format="mixed", errors='coerce')
    
    # Por si algún formato raro falló y se volvió NaT al parsear, aplicamos ffill de nuevo
    df_clean['invoice_date'] = df_clean['invoice_date'].ffill().bfill()
    
    # Imputación de Fechas Futuras: Las "topamos" a la fecha máxima de corte (2023-12-31)
    max_valid_date = pd.Timestamp('2023-12-31')
    df_clean.loc[df_clean['invoice_date'] > max_valid_date, 'invoice_date'] = max_valid_date
    
    # Volvemos a convertir al texto estricto YYYY-MM-DD que pide Great Expectations
    df_clean['invoice_date'] = df_clean['invoice_date'].dt.strftime('%Y-%m-%d')

    # Recalcular el total_revenue
    df_clean['total_revenue'] = df_clean['quantity'] * df_clean['price']

    print(f"Filas originales: {len(df)}")
    print(f"Filas después de la limpieza e imputación: {len(df_clean)}")
    
    return df_clean
