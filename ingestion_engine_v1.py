import os
import requests
import pandas as pd
import numpy as np
import sys
from dotenv import load_dotenv

# PASO CIENTÍFICO: Cargamos el archivo .env en la memoria del entorno
load_dotenv()

def fetch_market_data(symbol: str = "BTCUSDT", interval: str = "1m", limit: int = 1000) -> pd.DataFrame:
    """
    Se conecta a la API utilizando variables de entorno protegidas.
    """
    # En lugar de una cadena fija, el sistema operativo le entrega la URL al script
    url = os.getenv("BINANCE_API_URL")
    
    # Factor de seguridad: si el archivo .env no existe o la variable está vacía, frenamos el bot
    if not url:
        print("CRITICAL ERROR: BINANCE_API_URL environment variable is missing!")
        sys.exit(1)

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    
    print(f"--- INITIATING NETWORK REQUEST VIA SECURE PROXIMITY: {symbol} ---")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            print(f"CRITICAL ERROR: API responded with status code {response.status_code}")
            sys.exit(1)
            
        raw_data = response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"NETWORK EXCEPTION: Failed to establish connection. Details: {e}")
        sys.exit(1)

    # ... (El resto de tu código de procesamiento de matriz de abajo se queda exactamente igual) ...
    structured_data = {
        "timestamp": [pd.to_datetime(row[0], unit='ms') for row in raw_data],
        "close_price": [row[4] for row in raw_data],
        "volume_base": [row[5] for row in raw_data]
    }

    df = pd.DataFrame({
        "timestamp": structured_data["timestamp"],
        "close_price": np.array(structured_data["close_price"], dtype=np.float32),
        "volume_base": np.array(structured_data["volume_base"], dtype=np.float32)
    })
    
    return df

if __name__ == "__main__":
    df_live = fetch_market_data()
    print("\n=== SECURE INGESTION TELEMETRY ===")
    print(df_live.head())