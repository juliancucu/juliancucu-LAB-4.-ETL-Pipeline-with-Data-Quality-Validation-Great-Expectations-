from extract import extract_data, basic_profiling, register_in_ge, validate_raw_data, validate_transformed_data
from clean import clean_data
from transform import transform_data
from load import load_data

def main():
    print("=== TASK A: Extracción y Perfilado ===")
    df = extract_data()
    basic_profiling(df)
    
    context, batch_request = register_in_ge(df)

    print("\n=== TASK B: Validación de Datos Crudos ===")
    validate_raw_data(context, batch_request)

    print("\n=== TASK D: Limpieza de Datos ===")
    df_cleaned = clean_data(df)

    print("\n=== TASK E: Transformación de Datos ===")
    df_transformed = transform_data(df_cleaned)

    print("\n=== TASK F: Segunda Validación ===")
    validate_transformed_data(context, df_transformed)

    print("\n=== TASK G: Carga de Datos ===")
    load_data(df_transformed)

if __name__ == "__main__":
    main()