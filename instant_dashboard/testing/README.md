# InstantDashboard Testing Suite

This folder contains all testing files and demos for the InstantDashboard multi-agent system.

## Testing Structure

### Foundation & Phase Tests
- `test_foundation.py` - Comprehensive test suite covering foundation setup and all implemented phases
  - Foundation tests (imports, environment, database settings, prompts, agent creation)  
  - Phase 2 tests (QueryPlannerAgent functionality)
  - Will be extended for future phases

### Demo & Manual Testing
- `test_phase_2_demo.py` - Interactive demo of Phase 2 QueryPlannerAgent functionality
  - Shows direct tool calling
  - Demonstrates structured query plan generation
  - Useful for manual testing and verification

## Running Tests

### Full Test Suite
```bash
cd /path/to/data-science
python instant_dashboard/testing/test_foundation.py
```

### Interactive Demo
```bash  
cd /path/to/data-science
python instant_dashboard/testing/test_phase_2_demo.py
```

## Test Results History

### Phase 1: Foundation (COMPLETED ✅)
- All foundation tests passing
- Integration with existing BigQuery infrastructure working
- Environment setup verified

### Phase 2: QueryPlannerAgent (COMPLETED ✅) 
- QueryPlannerAgent imports and creation working
- Prompt system updated from placeholders  
- Coordinator integration successful
- Direct tool functionality verified
- Structured JSON query plans generated correctly

### Future Phases
- Phase 3: BigQueryRunner (Planned)
- Phase 4: ChartGenerator (Planned) 
- Phase 5: InsightGenerator (Planned)

## Test Output Examples

Latest successful run (Phase 2):
```
🚀 InstantDashboard Foundation & Phase 2 Tests
==================================================
🏗️  Foundation: 5/5 passed
🚀 Phase 2:    5/5 passed  
📊 Overall:    10/10 passed

🎉 All tests passed! (10/10)
✅ Phase 2 QueryPlannerAgent is working correctly!
💡 Ready to proceed to Phase 3: BigQueryRunner
```

## Dependencies Verified

Required packages for testing:
- `sqlglot` - SQL parsing and analysis
- `db-dtypes` - BigQuery data type support  
- `pandas` - Data manipulation
- `jsonschema` - JSON validation
- `requests` - HTTP requests
- `pydantic` - Data validation

All dependencies automatically installed and verified during test runs. 