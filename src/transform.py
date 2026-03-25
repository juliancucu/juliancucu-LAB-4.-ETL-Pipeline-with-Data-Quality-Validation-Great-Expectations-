import pandas as pd

def transform_data(df):
    print("\n--- INICIANDO TRANSFORMACIÓN DE DATOS (TASK E) ---")
    
    # Trabajamos sobre una copia
    df_transformed = df.copy()

    # Nos aseguramos de que la fecha sea tipo datetime
    df_transformed['invoice_date'] = pd.to_datetime(df_transformed['invoice_date'])

    # 1. Extraer características de la fecha
    df_transformed['year'] = df_transformed['invoice_date'].dt.year
    df_transformed['month'] = df_transformed['invoice_date'].dt.month
    df_transformed['day'] = df_transformed['invoice_date'].dt.day
    df_transformed['quarter'] = df_transformed['invoice_date'].dt.quarter

    # 2. Crear una categoría de ingresos (Revenue Category)
    # Por ejemplo: Low (< $500), Medium ($500 - $2000), High (> $2000)
    bins = [-float('inf'), 500, 2000, float('inf')]
    labels = ['Low', 'Medium', 'High']
    df_transformed['revenue_category'] = pd.cut(df_transformed['total_revenue'], bins=bins, labels=labels)

    # 3. Categoría de precio unitario (Unit Price Category)
    # Por ejemplo: Budget (< $100), Standard ($100 - $500), Premium (> $500)
    price_bins = [-float('inf'), 100, 500, float('inf')]
    price_labels = ['Budget', 'Standard', 'Premium']
    df_transformed['price_category'] = pd.cut(df_transformed['price'], bins=price_bins, labels=price_labels)

    print("Transformaciones aplicadas con éxito.")
    print("Nuevas columnas generadas:", ["year", "month", "day", "quarter", "revenue_category", "price_category"])
    
    return df_transformed