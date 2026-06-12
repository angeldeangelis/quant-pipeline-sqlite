Modular Quantitative Data Pipeline with SQLite Persistency
A robust, production-ready micro-pipeline designed to ingest asset price streams, persist financial data using a relational database, and execute statistical anomaly detection to emit execution signals. Built from scratch using Python and SQL.

🏗️ System Architecture & Data Flow
The project applies the Separation of Concerns (SoC) principle, isolating data infrastructure from mathematical analysis through a master orchestrator:

[Data Stream]
│
▼ (Parameterized INSERT)
[Data Persistence Module] ──► Writes to SQLite (.db)
│
▼ (Extracts 2D Matrix & flattens to 1D Vector via List Comprehension)
[Master Orchestrator]
│
▼ (Feeds clean vector)
[Quantitative Engine] ──► Calculates Median & MAD ──► Filters Outliers ──► Emits [BUY/SELL/HOLD]

⚡ Key Engineering Features
Loose Coupling Architecture: Financial logic is completely agnostic of the storage layer. Database engines can be swapped without affecting the quantitative models.

Fault-Tolerant Ingestion: Built-in exception handling (try-except) managing data-scarcity scenarios during stream execution without system failure.

Robust Statistics: Outlier filtering using Median and Median Absolute Deviation (MAD) instead of standard deviation, preventing signal distortion from high-volatility spikes.

Dynamic Enrouting: Portability secured across multiple OS environments using Python's pathlib for dynamic database localization.

🚀 How To Run
Clone this repository:
git clone https://github.com/angeldeangelis/quant-pipeline-sqlite.git

Navigate to the project root:
cd quant-pipeline-sqlite

Run the master orchestrator to initialize the database and trigger the execution simulation:
python orchestrator_pipeline.py

🛠️ Tech Stack
Language: Python 3.x

Database: SQLite3 (SQL)

Core Libraries: pathlib, datetime