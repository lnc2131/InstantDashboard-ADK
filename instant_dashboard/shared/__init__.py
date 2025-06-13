# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Shared utilities and tools for InstantDashboard.

This module exports all the shared functionality that was migrated from data_science
to make instant_dashboard self-contained.
"""

# Import utility functions
from .utils import (
    get_env_var,
    extract_json_from_model_output,
    get_image_bytes,
)

# Import BigQuery tools
from .bigquery import (
    get_bq_client,
    get_database_settings,
    update_database_settings,
    get_bigquery_schema,
    initial_bq_nl2sql,
    cleanup_sql,
    run_bigquery_validation,
    MAX_NUM_ROWS,
    chase_sql_constants_dict,
)

# Import agent tools
from .tools import (
    database_agent,
    call_db_agent,
)

__all__ = [
    # Utility functions
    "get_env_var",
    "extract_json_from_model_output", 
    "get_image_bytes",
    # BigQuery tools
    "get_bq_client",
    "get_database_settings",
    "update_database_settings",
    "get_bigquery_schema",
    "initial_bq_nl2sql",
    "cleanup_sql",
    "run_bigquery_validation",
    "MAX_NUM_ROWS",
    "chase_sql_constants_dict",
    # Agent tools
    "database_agent",
    "call_db_agent",
] 