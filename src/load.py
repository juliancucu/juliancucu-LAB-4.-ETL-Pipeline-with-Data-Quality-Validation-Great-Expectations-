import os

def load_data(df):
    print("\n--- INICIANDO CARGA DE DATOS (TASK G) ---")
    
    # Nos aseguramos de que la carpeta de destino exista
    output_dir = "data/processed"
    os.makedirs(output_dir, exist_ok=True)
    
    # Definimos el nombre del archivo final
    output_path = f"{output_dir}/clean_retail_data.csv"
    
    # Guardamos el DataFrame en un archivo CSV 
    df.to_csv(output_path, index=False)
    
    print(f"¡Éxito! Datos limpios y transformados guardados en: {output_path}")
    print(f"Total de filas finales: {len(df)}")