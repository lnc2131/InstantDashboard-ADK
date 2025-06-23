# InstantDashboard

A multi-agent data analytics back end API that provides natural language interfaces to data insights. 

It is within the larger project called neuralWrite, which you can demo here: https://v0-reportwriter.vercel.app/. 

Or you can try out just the mock front-end for InstantDashboard here: https://instant-dashboard-adk-l9bz.vercel.app/

## Overview

InstantDashboard is built on Google's Agent Development Kit (ADK) and provides a sophisticated pipeline for turning natural language questions into actionable data insights:

```
Natural Language Question
    ↓ Phase 2: QueryPlannerAgent
Structured JSON Query Plan  
    ↓ Phase 3: BigQueryRunner
Generated SQL Query
    ↓ BigQuery Execution
Formatted JSON Results
    ↓ Phase 4: ChartGenerator 
Chart.js Visualizations
    ↓ Phase 5: InsightGenerator
Business Insights
```

## Features

- **Natural Language Interface**: Ask questions in plain English
- **Intelligent Query Planning**: Structured analysis of data requirements  
- **Safe SQL Execution**: Validated and sandboxed BigQuery operations
- **Real Business Data**: Works with actual BigQuery datasets
- **Multi-Agent Architecture**: Specialized agents for different pipeline stages

## Architecture
<img width="698" alt="Instant-Dashboard Architecture" src="https://github.com/user-attachments/assets/72b01fa0-763a-41ff-a9e6-047a25b2c21c" />

### Agent Structure
```
instant_dashboard/
├── agent.py                   # Main coordinator agent

├── prompts.py                 # Versioned prompt system
├── sub_agents/                # Specialized agents
│   ├── query_planner.py       # Phase 2: Query planning
│   ├── bigquery_runner.py     # Phase 3: SQL execution
│   ├── chart_generator.py     # Phase 4: Future
│   └── insight_generator.py   # Phase 5: Future
└── testing/                   # Comprehensive test suite
```


## Installation

### Prerequisites

- Python 3.11+
- Google Cloud Project with BigQuery API enabled
- Google Agent Development Kit 1.0+
- Poetry (recommended) or pip

### Setup

1. **Clone and Install Dependencies**:
   ```bash
   git clone [repository]
   cd instant-dashboard
   poetry install
   ```

2. **Configure Environment**:
   Create a `.env` file with your Google Cloud settings:
   ```bash
   # Copy example and customize
   cp .env.example .env
   ```

3. **Required Environment Variables**:
   ```
   # Model Configuration
   ROOT_AGENT_MODEL=gemini-2.0-flash-001
   
   # Google Cloud Settings
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   GOOGLE_GENAI_USE_VERTEXAI=1
   
   # BigQuery Configuration  
   BQ_PROJECT_ID=your-bigquery-project
   BQ_DATASET_ID=your-dataset
   ```

4. **Authenticate with Google Cloud**:
   ```bash
   gcloud auth application-default login
   ```

## Usage

### Command Line Interface

```bash
# Interactive mode
adk run instant_dashboard

# Web interface  
adk web
# Then select "instant_dashboard" from the dropdown
```

### API Server

```bash
# Start API server
adk api_server instant_dashboard

# Access API documentation
open http://127.0.0.1:8000/docs
```

### Example Queries

- "What are the top 5 countries by total sales?"
- "Show me sales trends by product over the last quarter"
- "Which stores have the highest customer satisfaction?"
- "Compare revenue between different product categories"

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific phase tests
python instant_dashboard/testing/test_phase_3.py

# Run integration tests
python test_real_adk_integration.py
```


## Support

For questions or issues:
1. Check the test suite for examples
2. Review phase documentation
3. Check ADK documentation
4. Create an issue with detailed reproduction steps
