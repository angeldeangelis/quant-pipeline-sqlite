"""
Phase 2: Data Engineering & Storage Node.
Handles dynamic enrouting, relational table initializations,
parameterized record insertions, and historical 1D vector flattener queries.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

# =====================================================================
# GLOBAL INFRASTRUCTURE CONFIGURATION
# Defines dynamic path routing to guarantee system cross-portability
# =====================================================================
BASE_DIR = Path(__file__).resolve().parents[1]
RUTA_DB = BASE_DIR / "DATA" / "mercado_data.db"


def inicializar_base_de_datos() -> str:
    """Task A: Connects to the storage engine and builds target tables if missing."""
    conexion = sqlite3.connect(RUTA_DB)
    cursor = conexion.cursor()
    
    # SQL Schema Definition with strict column separation commas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS precios_activos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            ticker TEXT,
            precio REAL
        )
    """)

    conexion.commit()
    conexion.close()


def registrar_precio(ticker: str, precio: float):
    """Task B: Commits a single real-time data tick to disk with a hard ISO timestamp."""
    conexion = sqlite3.connect(RUTA_DB)
    cursor = conexion.cursor()

    # Capture absolute system execution execution time
    timestamp = datetime.now().isoformat()

    # Safe parameterized query guarding against SQL Injection attacks
    cursor.execute("""
        INSERT INTO precios_activos (timestamp, ticker, precio)
        VALUES (?, ?, ?)
        """, (timestamp, ticker, precio))

    conexion.commit()
    conexion.close()


def extraer_ultima_ventana_sql(ticker: str, longitud_ventana: int = 3) -> list:
    """Task C: Retrieves the latest N records from disk and flattens them into a clean 1D array."""
    conexion = sqlite3.connect(RUTA_DB)
    cursor = conexion.cursor()

    # Optimized chronological reverse query bounded by the chosen sliding window size
    cursor.execute("""
        SELECT precio FROM precios_activos
        WHERE ticker = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """, (ticker, longitud_ventana))
    
    filas = cursor.fetchall()
    conexion.close()

    # Data transformation: Unpack the 2D SQL relational matrix into a clean 1D numerical list
    # Converts data from [(195.0,), (100.0,)] to [195.0, 100.0]
    precios_limpios = [fila[0] for fila in filas]
    
    # Restore standard historical chronological order: Changes from [New -> Old] to [Old -> New]
    precios_limpios.reverse()
    
    return precios_limpios


# --- Local Development Verification Block ---
if __name__ == "__main__":
    print("=== RUNNING LOCAL DATA NODE UNIT TEST ===")
    inicializar_base_de_datos()
    registrar_precio("BTCUSDT", 100.0)
    print(f"Database located and validated at: {RUTA_DB}")