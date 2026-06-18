import sqlite3
import pandas as pd

DB_NAME = "market_data.db"

def extract_regime_metrics():
    """
    Ejecuta Query Pushdown. SQL procesa el volumen y las medias móviles
    en el disco duro; Python solo recibe la matriz refinada para análisis.
    """
    conn = sqlite3.connect(DB_NAME)
    
    # Esta consulta utiliza una Función de Ventana de SQL (AVG() OVER)
    # Calificamos la velocidad del volumen directamente en el motor de C de SQLite.
    query = """
        WITH volume_calculations AS (
    -- Paso 1: SQL calcula la ventana móvil sobre la totalidad de los datos en el disco
    SELECT 
        timestamp,
        close_price,
        volume_base,
        volatility_zscore,
        AVG(volume_base) OVER (
            ORDER BY timestamp 
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS rolling_avg_volume
    FROM btc_candles
)
-- Paso 2: Ahora sí, filtramos los nulos sin alterar el pasado de la ventana móvil
SELECT * FROM volume_calculations
WHERE volatility_zscore IS NOT NULL
    """
    
    print("[ANALYTICS ENGINE] Executing Query Pushdown on disk...")
    
    # Pandas intercepta el flujo binario de SQL y lo convierte en un DataFrame
    df_analytics = pd.read_sql_query(query, conn)
    conn.close()
    
    if df_analytics.empty:
        print("[ANALYTICS WARNING] The database is empty or has insufficient rows.")
        return df_analytics
        
    # Python entra en acción para la lógica no lineal:
    # Identificamos anomalías de volumen cruzando el volumen real vs su media móvil SQL
    df_analytics['volume_anomaly_ratio'] = df_analytics['volume_base'] / df_analytics['rolling_avg_volume']
    
    return df_analytics

if __name__ == "__main__":
    print("--- RUNNING COGNITIVE EXTRACTION LOOP ---")
    results = extract_regime_metrics()
    
    if not results.empty:
        print("\n=== REFINED MARKET ANOMALIES (QUERY PUSHDOWN RESULTS) ===")
        # Mostramos las filas donde el Z-Score o el volumen muestran comportamiento extremo
        anomalies = results[(results['volatility_zscore'].abs() > 1.5) | (results['volume_anomaly_ratio'] > 2.0)]
        print(anomalies[['timestamp', 'close_price', 'volatility_zscore', 'volume_anomaly_ratio']].tail(10))