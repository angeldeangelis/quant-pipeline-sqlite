import sqlite3
import pandas as pd
import os

DB_NAME = "market_data.db"

def init_db():
    """
    Inicializa el archivo de base de datos y define el esquema relacional
    con restricciones estrictas de clave primaria.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Creamos la tabla definiendo el timestamp como PRIMARY KEY.
    # Esto impide físicamente que el mismo minuto se almacene dos veces en el disco duro.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS btc_candles (
            timestamp TEXT PRIMARY KEY,
            close_price REAL NOT NULL,
            volume_base REAL NOT NULL,
            log_return REAL,
            volatility_zscore REAL
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"[DATABASE INFO] Relational schema initialized in: {DB_NAME}")

def save_data_defensively(df: pd.DataFrame):
    """
    Inserta registros en la base de datos aplicando una estrategia
    de programación defensiva contra colisiones de datos duplicados.
    """
    init_db() # Nos aseguramos de que la tabla exista
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Clonamos el DataFrame para no alterar los tipos de datos de la RAM original
    df_db = df.copy()
    df_db['timestamp'] = df_db['timestamp'].astype(str) # SQL prefiere strings para fechas indexadas
    
    print(f"[DATABASE OVERSEER] Preparing ingestion of {len(df_db)} rows...")
    
    rows_inserted = 0
    
    # Recorremos la matriz fila por fila ejecutando control de colisiones
    for _, row in df_db.iterrows():
        try:
            # INSERT OR IGNORE: Si el timestamp ya existe, SQL descarta la fila silenciosamente
            # protegiendo la base de datos de contaminación y duplicación de datos.
            cursor.execute("""
                INSERT OR IGNORE INTO btc_candles (timestamp, close_price, volume_base, log_return, volatility_zscore)
                VALUES (?, ?, ?, ?, ?)
            """, (
                row['timestamp'], 
                float(row['close_price']), 
                float(row['volume_base']),
                None if pd.isna(row['log_return']) else float(row['log_return']),
                None if pd.isna(row['volatility_zscore']) else float(row['volatility_zscore'])
            ))
            if cursor.rowcount > 0:
                rows_inserted += 1
        except sqlite3.Error as e:
            print(f"[DATABASE ERROR] Critical write failure: {e}")
            
    conn.commit()
    conn.close()
    
    print(f"[DATABASE SUCCESS] Ingestion pipeline closed. New rows written to disk: {rows_inserted}")

if __name__ == "__main__":
    print("--- DATABASE LAYER ISOLATION TEST ---")
    init_db()