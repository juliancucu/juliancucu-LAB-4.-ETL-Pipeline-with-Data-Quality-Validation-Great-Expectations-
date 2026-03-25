import pandas as pd
import great_expectations as gx
import re

# Cargamos el dataset
def extract_data():
    df = pd.read_csv("data/raw/retail_etl_dataset.csv")
    return df

# Funcion auxiliar para detectar formato de fecha
def detect_date_format(value):
    if pd.isna(value):
        return "null_like"

    # Convertir a texto y quitar espacios
    value = str(value).strip()

    # Detectar valores tipo nulos
    if value in ["", "NULL", "N/A", "NA", "null", "n/a"]:
        return "null_like"

    # Formato YYYY-MM-DD
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return "YYYY-MM-DD"

    # Formato YYYY/MM/DD
    if re.fullmatch(r"\d{4}/\d{2}/\d{2}", value):
        return "YYYY/MM/DD"

    # Formato DD-MM-YYYY
    if re.fullmatch(r"\d{2}-\d{2}-\d{4}", value):
        return "DD-MM-YYYY"

    # Cualquier otro formato
    return "other"

# Funcion para parsear fechas mixtas 
def parse_mixed_date(value):
    if pd.isna(value):
        return pd.NaT

    value = str(value).strip()

    if value in ["", "NULL", "N/A", "NA", "null", "n/a"]:
        return pd.NaT

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return pd.to_datetime(value, format="%Y-%m-%d", errors="coerce")

    if re.fullmatch(r"\d{4}/\d{2}/\d{2}", value):
        return pd.to_datetime(value, format="%Y/%m/%d", errors="coerce")

    if re.fullmatch(r"\d{2}-\d{2}-\d{4}", value):
        return pd.to_datetime(value, format="%d-%m-%Y", errors="coerce")

    return pd.NaT

# Profiling basico
def basic_profiling(df):
    # [x] shape
    print("\n- SHAPE -")
    print(df.shape)

    # [x] info
    print("\n- INFO -")
    df.info()

    # [x] memory
    print("\n- MEMORY USAGE -")
    print(df.memory_usage(deep=True))
    print("\nTotal memory usage:")
    print(df.memory_usage(deep=True).sum(), "bytes")

    # [x] missing count
    print("\n- MISSING COUNT -")
    print(df.isnull().sum())

    # [x] missing %
    print("\n- MISSING PERCENTAGE -")
    print(((df.isnull().sum() / len(df)) * 100).round(2))

    # [x] cardinality product
    print("\n- CARDINALITY: PRODUCT -")
    print(df["product"].nunique())

    # [x] cardinality country
    print("\n- CARDINALITY: COUNTRY -")
    print(df["country"].nunique())

    # [x] numeric stats
    print("\n- NUMERIC STATS -")
    numeric_stats = df[["quantity", "price", "total_revenue"]].agg(
        ["min", "max", "mean", "median", "std"]
    )
    print(numeric_stats)

    # [x] duplicate invoice_id
    duplicate_count = df["invoice_id"].duplicated().sum()
    print("\n- DUPLICATE invoice_id -")
    print(duplicate_count)

    # [x] total_revenue check
    calculated_total = df["quantity"] * df["price"]
    wrong_total_count = (abs(df["total_revenue"] - calculated_total) > 0.01).sum()
    print("\n- total_revenue != quantity * price (±0.01) -")
    print(wrong_total_count)

    # [x] date format distribution
    df["date_format"] = df["invoice_date"].apply(detect_date_format)
    print("\n- DATE FORMAT DISTRIBUTION -")
    print(df["date_format"].value_counts())

    # Parsear fechas para revisar futuras
    df["invoice_date_parsed"] = df["invoice_date"].apply(parse_mixed_date)

    # [x] future dates
    future_dates_count = (df["invoice_date_parsed"] > pd.Timestamp("2023-12-31")).sum()
    print("\n- FUTURE DATES (> 2023-12-31) -")
    print(future_dates_count)

    # [x] null-like dates
    null_like_count = (df["date_format"] == "null_like").sum()
    print("\n- NULL-LIKE DATE STRINGS -")
    print(null_like_count)

# Registramos en great expectations
def register_in_ge(df):
    # Creamos el contexto de Great Expectations
    context = gx.get_context()

    # Si el datasource ya existe, lo usamos. Si no existe, se crea
    try:
        data_source = context.get_datasource("retail_source")
    except Exception:
        data_source = context.sources.add_pandas(name="retail_source")

    # Si el asset ya existe, lo usamos. Si no existe, se crea
    try:
        data_asset = data_source.get_asset("retail_asset")
    except Exception:
        data_asset = data_source.add_dataframe_asset(name="retail_asset")

    # Crear batch request con el dataframe en memoria
    batch_request = data_asset.build_batch_request(dataframe=df)

    print("\nDataFrame registrado en Great Expectations.")
    return context, batch_request


#FUNCION DE VALIDACION 
def validate_raw_data(context, batch_request):
    print("\n--- INICIANDO VALIDACIÓN DE DATOS CRUDOS (TASK B) ---")
    suite_name = "raw_retail_data_suite"
    
    # Crear o recuperar la Expectation Suite
    try:
        context.get_expectation_suite(suite_name)
        print(f"Usando suite existente: {suite_name}")
    except gx.exceptions.DataContextError:
        context.add_expectation_suite(suite_name)
        print(f"Creada nueva suite: {suite_name}")

    # Obtener el Validator
    validator = context.get_validator(
        batch_request=batch_request,
        expectation_suite_name=suite_name
    )

    # Definir las Expectativas (Estas deben fallar a propósito por los problemas en el dataset)
    
    # Completeness (Completitud)
    validator.expect_column_values_to_not_be_null("customer_id")
    validator.expect_column_values_to_not_be_null("invoice_date")
    
    # Uniqueness (Unicidad)
    validator.expect_column_values_to_be_unique("invoice_id")
    
    # Validity (Validez - sin negativos ni ceros)
    validator.expect_column_values_to_be_between("quantity", min_value=1)
    validator.expect_column_values_to_be_between("price", min_value=0.01)
    
    # Consistency (Consistencia - nombres de países estandarizados)
    # De acuerdo a tu exploración inicial, estos deberían ser los únicos válidos
    validator.expect_column_values_to_be_in_set(
        "country", 
        ["Colombia", "Ecuador", "Peru", "Chile"]
    )
    
    # Timeliness (Puntualidad/Formato de fechas)
    # Esperamos que todo tenga formato YYYY-MM-DD estricto
    validator.expect_column_values_to_match_regex("invoice_date", r"^\d{4}-\d{2}-\d{2}$")

    #Guardar la suite asegurando que conservamos las expectativas que fallaron
    validator.save_expectation_suite(discard_failed_expectations=False)
    print(f"Expectation Suite '{suite_name}' guardada exitosamente.")

    # Configurar y Ejecutar un Checkpoint
    checkpoint_name = "raw_data_checkpoint"
    
    checkpoint_config = {
        "name": checkpoint_name,
        "config_version": 1,
        "class_name": "SimpleCheckpoint",
        "validations": [
            {
                "batch_request": batch_request,
                "expectation_suite_name": suite_name
            }
        ]
    }
    
    context.add_or_update_checkpoint(**checkpoint_config)
    print("Ejecutando validaciones...")
    checkpoint_result = context.run_checkpoint(checkpoint_name=checkpoint_name)
    
    # Construir y abrir los Data Docs (Abrirá una pestaña en tu navegador web)
    print("Generando y abriendo Data Docs para visualizar los resultados...")
    context.build_data_docs()
    context.open_data_docs()
    
    return checkpoint_result

# FUNCION DE VALIDACION FINAL
def validate_transformed_data(context, df_transformed):
    print("\n--- INICIANDO VALIDACIÓN DE DATOS TRANSFORMADOS (TASK F) ---")
    suite_name = "transformed_retail_data_suite"
    
    #Registrar el nuevo dataframe (ya transformado) como un nuevo asset
    data_source = context.get_datasource("retail_source")
    try:
        data_asset = data_source.get_asset("transformed_asset")
    except Exception:
        data_asset = data_source.add_dataframe_asset(name="transformed_asset")
        
    batch_request = data_asset.build_batch_request(dataframe=df_transformed)

    #Crear la nueva suite de expectativas
    try:
        context.get_expectation_suite(suite_name)
        print(f"Usando suite existente: {suite_name}")
    except gx.exceptions.DataContextError:
        context.add_expectation_suite(suite_name)
        print(f"Creada nueva suite: {suite_name}")

    validator = context.get_validator(
        batch_request=batch_request,
        expectation_suite_name=suite_name
    )

    #Definir las Expectativas (¡Estas deben pasar todas en verde!)
    validator.expect_column_values_to_not_be_null("customer_id")
    validator.expect_column_values_to_be_between("quantity", min_value=1)
    validator.expect_column_values_to_be_between("price", min_value=0.01)
    validator.expect_column_values_to_be_in_set(
        "country", 
        ["Colombia", "Ecuador", "Peru", "Chile"]
    )
    validator.expect_column_values_to_match_regex("invoice_date", r"^\d{4}-\d{2}-\d{2}$")
    
    # Validamos también las columnas nuevas que acabamos de crear
    validator.expect_column_values_to_not_be_null("revenue_category")
    validator.expect_column_values_to_be_in_set("revenue_category", ["Low", "Medium", "High"])

    validator.save_expectation_suite(discard_failed_expectations=False)

    #Ejecutar el Checkpoint
    checkpoint_name = "transformed_data_checkpoint"
    checkpoint_config = {
        "name": checkpoint_name,
        "config_version": 1,
        "class_name": "SimpleCheckpoint",
        "validations": [{"batch_request": batch_request, "expectation_suite_name": suite_name}]
    }
    context.add_or_update_checkpoint(**checkpoint_config)
    
    print("Ejecutando validaciones finales...")
    checkpoint_result = context.run_checkpoint(checkpoint_name=checkpoint_name)
    
    print("Generando y abriendo Data Docs de la validación final...")
    context.build_data_docs()
    context.open_data_docs()
    
    return checkpoint_result
