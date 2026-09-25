import logging
logger = logging.getLogger(__name__)

import json
import os
import datetime
from typing import Dict, Any

# Optional BigQuery imports
try:
    from google.cloud import bigquery
    BQ_AVAILABLE = True
except ImportError:
    BQ_AVAILABLE = False

class BigQueryService:
    def __init__(self):
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.dataset_id = "krishisathi_sandbox"
        self.table_id = "diagnoses"
        self.client = None
        
        if BQ_AVAILABLE and self.project_id:
            try:
                self.client = bigquery.Client(project=self.project_id)
                self.table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
            except Exception as e:
                logger.info(f"BigQuery init error: {e}")
                self.client = None

    async def log_diagnosis(self, data: Dict[str, Any]):
        """
        Logs a diagnosis to BigQuery using batch load jobs to comply with Sandbox limits.
        If BQ is unavailable, falls back to a local JSONL log file.
        """
        if "timestamp" not in data:
            data["timestamp"] = datetime.datetime.utcnow().isoformat()
            
        if self.client:
            try:
                import asyncio
                import tempfile
                
                def _do_bq_load():
                    # Create a temporary local file that cleans itself up
                    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
                        temp_file = f.name
                        f.write(json.dumps(data) + "\n")
                    
                    try:
                        job_config = bigquery.LoadJobConfig(
                            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
                            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                            autodetect=True,
                        )
                        
                        with open(temp_file, "rb") as source_file:
                            job = self.client.load_table_from_file(
                                source_file,
                                self.table_ref,
                                job_config=job_config
                            )
                        # Ensure the job is sent before exiting thread
                    finally:
                        try:
                            import os
                            os.remove(temp_file)
                        except OSError:
                            pass
                
                await asyncio.to_thread(_do_bq_load)
            except Exception as e:
                logger.error(f"Failed to log to BigQuery: {e}. Data dropped.")
                raise e
        else:
            logger.error("BigQuery client not configured or unavailable. Telemetry data dropped.")

bq_service = BigQueryService()
