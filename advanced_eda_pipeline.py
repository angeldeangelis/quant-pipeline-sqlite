import pandas as pd
import numpy as np
import time

# 1. GENERACIÓN DE DATOS A ESCALA DE PRODUCCIÓN
print("=== GENERATING 1,000,000 ROWS OF FINANCIAL MICROSTRUCTURE ===")
start_time = time.time()

np.random.seed(42)
n_rows = 1_000_000

# Generate a synthetic random walk for asset prices
price_changes = np.random.normal(loc=0.0001, scale=0.02, size=n_rows)
initial_price = 100.0
prices = initial_price * np.exp(np.cumsum(price_changes))

# Generate high-frequency volumes with intentional structural anomalies (zeroes and negatives)
volumes = np.random.lognormal(mean=10, sigma=1.5, size=n_rows)
volumes[np.random.choice(n_rows, size=5000, replace=False)] = 0.0  # Liquidity drops

# 1. GENERACIÓN DE DATOS CON DOWNCASTING NATIVO DESDE EL ORIGEN
df = pd.DataFrame({
    'timestamp': pd.date_range(start='2026-01-01', periods=n_rows, freq='s'),
    'close_price': prices.astype(np.float32),  # Inyectamos directamente como float32
    'volume_base': volumes.astype(np.float32)   # Inyectamos directamente como float32
})

print(f"Dataset generated in: {time.time() - start_time:.4f} seconds.")
print(f"Initial Memory Usage: {df.memory_usage(deep=True).sum() / (1024**2):.2f} MB")
print("-" * 60)

# =====================================================================
# LABORATERIO DE OPTIMIZACIÓN Y FEATURE ENGINEERING
# =====================================================================


# TAREA 2: FEATURE ENGINEERING (ROLLING Z-SCORE VECTORIZADO)
print("\n--- CALCULATING LOG RETURNS & ROLLING Z-SCORE (WINDOW=20) ---")

# 1. Retornos logarítmicos vectorizados: ln(P_t) - ln(P_t-1)
df['log_return'] = np.log(df['close_price']) - np.log(df['close_price'].shift(1))

# 2. Ventanas móviles para Media y Desviación Estándar de los retornos
rolling_window = df['log_return'].rolling(window=20)
df['rolling_mean'] = rolling_window.mean()
df['rolling_std'] = rolling_window.std()

# 3. Cálculo del Z-Score dinámico de volatilidad
df['volatility_zscore'] = (df['log_return'] - df['rolling_mean']) / df['rolling_std']


# AUDITORÍA DE RESULTADOS
print("\n=== FIRST 25 ROWS OF HIGH-FREQUENCY STRUCTURE ===")
# Mostramos las columnas clave para verificar los cálculos y los NaN iniciales de la ventana
print(df[['timestamp', 'close_price', 'log_return', 'volatility_zscore']].head(25))