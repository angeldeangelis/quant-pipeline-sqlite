import requests
import pandas as pd
import numpy as np
import sys

def fetch_market_data(symbol: str = "BTCUSDT", interval: str = "1m", limit: int = 1000) -> pd.DataFrame:
    """
    Se conecta a la API pública de Binance, extrae la microestructura de mercado
    y devuelve un DataFrame optimizado estructuralmente en memoria RAM.
    """
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    
    print(f"--- INITIATING NETWORK REQUEST: {symbol} ({interval}) ---")
    
    try:
        # Ejecución de la solicitud HTTP con un timeout estricto de 10 segundos
        response = requests.get(url, params=params, timeout=10)
        
        # Auditoría del código de estado HTTP
        if response.status_code != 200:
            print(f"CRITICAL ERROR: API responded with status code {response.status_code}")
            sys.exit(1)
            
        raw_data = response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"NETWORK EXCEPTION: Failed to establish connection. Details: {e}")
        sys.exit(1)

    print(f"Data successfully downloaded. Processing {len(raw_data)} records...")

    # El formato crudo de la API es una lista de listas. 
    # Extraemos las posiciones: [0]=Timestamp, [4]=Close Price, [5]=Volume
    structured_data = {
        "timestamp": [pd.to_datetime(row[0], unit='ms') for row in raw_data],
        "close_price": [row[4] for row in raw_data],
        "volume_base": [row[5] for row in raw_data]
    }

    # INYECCIÓN OPTIMIZADA DESDE EL ORIGEN (Tu firma de diseño)
    df = pd.DataFrame({
        "timestamp": structured_data["timestamp"],
        "close_price": np.array(structured_data["close_price"], dtype=np.float32),
        "volume_base": np.array(structured_data["volume_base"], dtype=np.float32)
    })
    
    return df

if __name__ == "__main__":
    # Prueba de aislamiento del motor de ingesta
    df_live = fetch_market_data()
    print("\n=== INGESTION ENGINE TELEMETRY ===")
    print(df_live.info(memory_usage='deep'))
    print("\n=== FIRST 5 ROWS OF REAL MARKET DATA ===")
    print(df_live.head())