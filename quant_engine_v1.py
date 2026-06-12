"""
Phase 1: Quantitative Processing Engine.
Calculates robust non-parametric statistics (Median & MAD) to detect
high-volatility anomalies and emit trading signals while filtering outliers.
"""

def calcular_mediana(valores: list) -> float:
    """Calculates the statistical median of a clean numerical array."""
    valores_ordenados = sorted(valores)
    n = len(valores_ordenados)
    mitad = n // 2
    
    if n % 2 != 0:
        return float(valores_ordenados[mitad])
    else:
        return (valores_ordenados[mitad - 1] + valores_ordenados[mitad]) / 2.0


def calcular_mad(valores: list, mediana: float) -> float:
    """Calculates the Median Absolute Deviation (MAD) as a robust volatility proxy."""
    desviaciones_absolutas = [abs(x - mediana) for x in valores]
    return calcular_mediana(desviaciones_absolutas)


def ejecutar_pipeline_cuant(precios: list) -> str:
    """
    Processes the incoming 1D price vector, checks for data scarcity,
    filters outliers, and outputs the final execution signal.
    """
    # Defensive programming: Enforce structural data constraints
    if len(precios) < 3:
        raise ValueError("Microstructure Error: Insufficient data points to calculate MAD.")
        
    # Calculate robust central tendency and dispersion metrics
    mediana_mercado = calcular_mediana(precios)
    mad_mercado = calcular_mad(precios, mediana_mercado)
    
    # Establish dynamic protection thresholds (3x MAD rule)
    umbral_tolerancia = 3 * mad_mercado
    ultimo_precio = precios[-1]
    
    # Analyze microstructure variation against the last valid tick
    desviacion_actual = abs(ultimo_precio - precios[-2])
    
    # Execution decision logic
    if desviacion_actual > umbral_tolerancia and mad_mercado > 0:
        # High volatility anomaly detected: Trigger outlier neutralization
        return "SELL"
    else:
        # Market structure within regular parameters
        return "HOLD"


# --- Local Development Verification Block ---
if __name__ == "__main__":
    print("=== RUNNING LOCAL QUANT ENGINE UNIT TEST ===")
    try:
        test_vector = [100.0, 102.0, 101.0, 100.0, 195.0]
        signal = ejecutar_pipeline_cuant(test_vector)
        print(f"Test Vector: {test_vector} -> Signal Issued: {signal}")
    except ValueError as e:
        print(f"Test Interrupted: {e}")