import time
# Import data infrastructure functions from the specialized package
from data_persistence.data_persistence_v1 import extraer_ultima_ventana_sql, registrar_precio, inicializar_base_de_datos
# Import the quantitative analytical engine from Phase 1
from quant_engine_v1 import ejecutar_pipeline_cuant

def ejecutar_ciclo_automatizado(ticker: str, ventana_size: int = 3):
    """
    Orchestrates the data extraction from SQL, feeds the quantitative
    engine, and captures the final system execution signal.
    """
    try:
        print(f"\n[ORQUESTADOR] Requesting time window for {ticker} from SQL...")
        
        # 1. Fetch the latest price window using the data persistence module
        #    Passes 'ticker' and 'ventana_size' as arguments
        ventana_precios = extraer_ultima_ventana_sql(ticker, longitud_ventana=ventana_size)
        
        # 2. Output the retrieved 1D vector to the terminal for structural validation
        print(f"[ORQUESTADOR] Vector data successfully recovered: {ventana_precios}")
        
        # 3. Feed the clean vector into the quantitative processing engine
        #    Stores the resulting trading signal in the 'orden_final' variable
        orden_final = ejecutar_pipeline_cuant(ventana_precios)
        
        # 4. Output the definitive executive decision made by the system
        print(f"[LOG EJECUCIÓN] Order emitted by the system: {orden_final}")
        
    except ValueError as e:
        # Catch and handle data scarcity exceptions raised by the Phase 1 engine
        print(f"[ALERTA DE CONTROL] Cycle temporarily suspended: {e}")
    except Exception as general_error:
        # Catch unforeseen infrastructure, path localization, or database failures
        print(f"[ERROR CRÍTICO INFRAESTRUCTURA]: {general_error}")


if __name__ == "__main__":
    print("=== STARTING MASTER QUANT ORCHESTRATOR ===")
    
    # Ensure database and target tables are initialized on disk before operating
    inicializar_base_de_datos()
    
    ticker_monitoreado = "BTCUSDT"
    
    # --- SCENARIO 1: Robustness Test (Empty or insufficient database) ---
    # Evaluates how the pipeline reacts when there are not enough rows in disk.
    # The built-in try-except block prevents the system from crashing.
    ejecutar_ciclo_automatizado(ticker_monitoreado, ventana_size=3)
    
    # --- SCENARIO 2: Continuous Ingestion Simulation (Data Stream) ---
    print("\n[STREAM] Simulating the arrival of a new high-volatility price tick...")
    
    # Inyectamos dos precios de mercado previos para llenar la base de datos a 3 elementos
    registrar_precio(ticker_monitoreado, 102.0)
    registrar_precio(ticker_monitoreado, 101.0)
    
    # Ahora sí, llega el precio anómalo de alta volatilidad
    nuevo_precio_mercado = 195.0
    registrar_precio(ticker_monitoreado, nuevo_precio_mercado)
    
    # Re-run the cycle with the consolidated dataset now available on disk
    ejecutar_ciclo_automatizado(ticker_monitoreado, ventana_size=3)
    
    # --- SCENARIO 2: Continuous Ingestion Simulation (Data Stream) ---
    print("\n[STREAM] Simulating the arrival of a new high-volatility price tick...")
    nuevo_precio_mercado = 195.0
    registrar_precio(ticker_monitoreado, nuevo_precio_mercado)
    
    # Re-run the cycle with the consolidated dataset now available on disk
    ejecutar_ciclo_automatizado(ticker_monitoreado, ventana_size=3)