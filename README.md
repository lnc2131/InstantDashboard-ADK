# InstantDashboard

A multi-agent data analytics assistant that provides natural language interfaces to data insights.

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
    ↓ Phase 4: ChartGenerator (Future)
Chart.js Visualizations
    ↓ Phase 5: InsightGenerator (Future)
Business Insights
```

## Features

- **Natural Language Interface**: Ask questions in plain English
- **Intelligent Query Planning**: Structured analysis of data requirements  
- **Safe SQL Execution**: Validated and sandboxed BigQuery operations
- **Real Business Data**: Works with actual BigQuery datasets
- **Multi-Agent Architecture**: Specialized agents for different pipeline stages

## Phase Status

- ✅ **Phase 1**: Foundation (Database integration, environment setup)
- ✅ **Phase 2**: QueryPlannerAgent (Natural language → structured query plans)  
- ✅ **Phase 3**: BigQueryRunner (Query plans → SQL → data execution)
- 🔲 **Phase 4**: ChartGenerator (Data → Chart.js visualizations)
- 🔲 **Phase 5**: InsightGenerator (Data → business insights)

## Architecture

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

### Shared Infrastructure
```
shared/
├── bigquery/                  # BigQuery tools and agents
├── utils/                     # Utility functions  
└── tools.py                   # Shared agent tools
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

## Development

### Project Structure

The project follows a **learning-focused, incremental development** approach:

- **Phase-by-Phase Development**: Each phase builds on the previous
- **Comprehensive Testing**: All components have test coverage
- **Documentation First**: Clear documentation for each feature
- **Reusable Components**: Shared infrastructure across phases

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific phase tests
python instant_dashboard/testing/test_phase_3.py

# Run integration tests
python test_real_adk_integration.py
```

### Adding New Features

1. **Design**: Plan the new agent/tool functionality
2. **Implement**: Create the agent in `sub_agents/`
3. **Test**: Add comprehensive tests in `testing/`
4. **Integrate**: Add to main coordinator in `agent.py`
5. **Document**: Update README and create phase documentation

## API Reference

### Main Coordinator Tools

- `call_db_agent`: Direct SQL generation and execution
- `call_query_planner_agent`: Structured query planning  
- `call_bigquery_runner_agent`: Query plan execution
- `execute_full_pipeline`: Complete Phase 2 + 3 workflow

### Agent Architecture Patterns

Each agent follows consistent patterns:
- **Prompt versioning**: `prompts.py` with version history
- **Tool composition**: Reusable functions
- **Error handling**: Comprehensive error management
- **State management**: Context preservation across calls

## Contributing

### Development Principles

1. **Learning First**: Prioritize understanding over speed
2. **Incremental**: Build one small piece at a time  
3. **Test Everything**: Comprehensive test coverage required
4. **Document Everything**: Clear explanations for all features
5. **Safety First**: Validation and sandboxing for all operations

### Code Conventions

- **Imports**: Local imports in functions to avoid circular dependencies
- **Error Handling**: Use consistent error messages with clear context
- **Prompt Management**: Version all prompts with clear change history
- **Testing**: Each phase has its own comprehensive test suite

## Deployment

### Production Checklist

- [ ] Environment variables configured
- [ ] Google Cloud authentication set up
- [ ] BigQuery permissions verified
- [ ] All tests passing
- [ ] Performance benchmarks met

### Monitoring

The system includes comprehensive logging and error tracking:
- Agent execution logs
- BigQuery query performance
- Error rates and types
- User interaction patterns

## License

Apache License 2.0. See LICENSE file for details.

## Support

For questions or issues:
1. Check the test suite for examples
2. Review phase documentation
3. Check ADK documentation
4. Create an issue with detailed reproduction steps
