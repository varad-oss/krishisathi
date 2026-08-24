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
        # Add timestamp if missing
        if "timestamp" not in data:
            data["timestamp"] = datetime.datetime.utcnow().isoformat()
            
        if self.client:
            try:
                # BigQuery Sandbox does not support streaming inserts.
                # In production, we'd batch these in memory or a queue and write them via LoadJob
                # For this demo hackathon, we simulate a batch load by writing a temp JSON file
                # and triggering a load job, or we just write to a local log if BQ fails.
                
                # Create a temporary local file
                temp_file = f"/tmp/bq_batch_{datetime.datetime.utcnow().timestamp()}.jsonl"
                with open(temp_file, "w") as f:
                    f.write(json.dumps(data) + "\n")
                    
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
                # We don't await job.result() to keep the API fast, it runs in background
                # But for the hackathon prototype, we will just silently pass
            except Exception as e:
                logger.info(f"Failed to log to BigQuery, falling back to local: {e}")
                self._fallback_log(data)
        else:
            self._fallback_log(data)
            
    def _fallback_log(self, data: Dict[str, Any]):
        """Fallback logging to local file when BigQuery Sandbox is not configured."""
        try:
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            with open(f"{log_dir}/diagnoses.jsonl", "a") as f:
                f.write(json.dumps(data) + "\n")
        except Exception as e:
            logger.info(f"Fallback logging failed: {e}")

bq_service = BigQueryService()
