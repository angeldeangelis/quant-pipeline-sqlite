import pandas as pd
import numpy as np
# Importamos la función de tu motor de ingesta real desde el otro archivo
from ingestion_engine_v1 import fetch_market_data

# =====================================================================
# 1. INGESTA DE DATOS REALES DESDE BINANCE
# =====================================================================
# Traemos las últimas 1,000 velas de 1 minuto de Bitcoin directamente a la RAM
df = fetch_market_data(symbol="BTCUSDT", interval="1m", limit=1000)


# =====================================================================
# 2. FEATURE ENGINEERING (CÁLCULO MATEMÁTICO VECTORIZADO)
# =====================================================================
print("\n--- CALCULATING LOG RETURNS & ROLLING Z-SCORE (WINDOW=20) ---")

# Retornos logarítmicos vectorizados sobre precios reales
df['log_return'] = np.log(df['close_price']) - np.log(df['close_price'].shift(1))

# Ventanas móviles de volatilidad
rolling_window = df['log_return'].rolling(window=20)
df['rolling_mean'] = rolling_window.mean()
df['rolling_std'] = rolling_window.std()

# Z-Score dinámico de volatilidad en tiempo real
df['volatility_zscore'] = (df['log_return'] - df['rolling_mean']) / df['rolling_std']


# =====================================================================
# 3. TRATAMIENTO DEFENSIVO DE ANOMALÍAS (MÁSCARAS BOOLEANAS)
# =====================================================================
# Evaluamos de forma paralela si el mercado real arrojó baches de liquidez
zero_volume_mask = (df['volume_base'] == 0.0)
anomaly_count = zero_volume_mask.sum()

if anomaly_count > 0:
    print(f"\n[ALERT] Anomalies detected in live volume_base: {anomaly_count}")
    volume_median = df['volume_base'].median()
    df.loc[zero_volume_mask, 'volume_base'] = volume_median
    print(f"Imputation successful. New minimum volume: {df['volume_base'].min():.2f}")
else:
    print("\n[OK] No liquidity anomalies detected in the live data stream.")


# =====================================================================
# 4. AUDITORÍA DE RESULTADOS EN PRODUCCIÓN
# =====================================================================
print("\n=== LIVE MARKET PIPELINE TELEMETRY (LAST 15 ROWS) ===")
# Mostramos las últimas 15 filas para auditar los datos más recientes del mercado real
print(df[['timestamp', 'close_price', 'log_return', 'volatility_zscore']].tail(15))