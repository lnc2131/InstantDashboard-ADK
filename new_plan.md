# Agentic Dashboard Project – Technical Overview and Requirements

## 🎯 Project Objective

We are developing **InstantDashboard**, a multi-agent data analytics assistant that enables users to query, explore, and visualize business metrics using natural language. Inspired by Looker Studio, the application is built using **Google's Agent Development Kit (ADK)**, and focuses on intelligent automation of SQL-based analysis, BigQuery integration, and real-time chart generation.

Unlike traditional BI tools that require manual dashboard creation, this platform offers a **chat-first**, intelligent, and highly modular user experience.

---

## ✅ Functional Scope

### Core Capabilities

* Accepts natural language queries (e.g., “Show me sessions by country for the last 7 days”).
* Translates user input to structured SQL queries using LLM-based agents.
* Executes queries securely on BigQuery.
* Visualizes results with JSON-based chart specifications (e.g., bar, line, pie).
* Generates accompanying textual summaries and simple insights.
* Orchestrates the entire analysis workflow via multi-agent cooperation.

### Architectural Highlights

* Built on **Google ADK** with modular, testable agents.
* Employs a **multi-agent system** comprising specialized sub-agents:

  * `QueryPlannerAgent`: Parses NL → SQL plan.
  * `BigQueryRunnerAgent`: Executes SQL on BigQuery and returns tabular data.
  * `ChartGeneratorAgent`: Transforms tabular data into chart config.
  * `InsightGeneratorAgent`: Extracts textual insights (e.g., trends, top-k, growth).
* Designed to be extensible for other data sources (e.g., Stripe, GA4, Mixpanel).
* Compatible with **ADK Web UI** and CLI.

---

## 📁 File Structure (Iterative Development)

**UPDATED APPROACH:** Iterative development sharing infrastructure with existing data_science agent.

```plaintext
/data-science/  (existing ADK sample)
│
├── instant_dashboard/              # 🆕 New agent (same level as data_science)
│   ├── __init__.py                # Basic agent setup
│   ├── agent.py                   # Simple coordinator agent
│   └── sub_agents/                # Add agents incrementally
│       ├── __init__.py            
│       ├── query_planner.py       # Phase 2: First agent to build
│       ├── bigquery_runner.py     # Phase 3: Add after query_planner works
│       ├── chart_generator.py     # Phase 4: Add visualization
│       └── insight_generator.py   # Phase 5: Add insights
│
├── data_science/                  # 📋 Original Google agent (unchanged)
│   └── sub_agents/
│       └── bigquery/              # 🔄 Reference for building our agents
│
├── pyproject.toml                 # ✅ Shared poetry dependencies
├── .env                          # ✅ Shared environment variables
└── ... (existing files)
```

**Key Benefits:**
- ✅ Shares existing poetry/env setup
- ✅ Can reference/import from data_science agent
- ✅ Iterative development (one feature at a time)
- ✅ No disruption to existing system

---

## 🔄 Current Status & Migration Notes

We are currently **refactoring Google’s Data Science Agent** (from ADK samples) to isolate only the relevant components required for this MVP.

### 🚨 Step 1: Remove Unnecessary Features

The original agent includes features such as:

* `nl2python` code generation and execution (via Code Interpreter)
* BQML (BigQuery ML) forecasting and model training agents
* RAG pipelines for document search and schema assistance

These features are not aligned with our current goals and will be removed to simplify the codebase. The focus will be:

* SQL-centric querying and summarization
* Lightweight chart generation
* Agent-to-agent orchestration only

---

## 🚀 Step 2: Build the Core Dashboard Experience

With the excess components removed, we will shift focus toward enabling basic dashboard functionality.

### Dashboard Feature Goals

* Users can run queries and receive formatted, embeddable chart responses
* Chart responses should include a short textual insight or summary
* Results should be structured to support future enhancements like saving, refreshing, or sharing charts

### Required Agents and Systems

* `QueryPlannerAgent`: Parses query intent and fields
* `BigQueryRunnerAgent`: Executes queries using BigQuery client (mock/testable)
* `ChartGeneratorAgent`: Outputs a structured chart spec (e.g., for Chart.js)
* `InsightGeneratorAgent`: Uses heuristics or prompting to generate insight text

Optional (Phase 2+):

* `DashboardStateManager`: Manages session-based dashboards or saved queries
* `ExporterAgent`: Outputs results to Slack, email, or other formats

---

## 🔧 Technical Focus Areas (MVP Build)

### Agent Isolation and Customization

We are focused on extracting and refactoring:

* SQL planning modules (Prompt → SQL)
* BigQuery client configuration (auth + secure execution)
* Chart and insight generation templates (pure Python)

### Prompt Engineering

* Create structured prompt templates for `QueryPlannerAgent`
* Support multi-intent queries (e.g., “Compare revenue and churn by country”)
* Add support for field aliasing, table mapping, and fallback patterns

### Dashboard & Output Features

* Return result in a composable format (e.g., JSON)
* Allow charts to be saved, refreshed, or embedded (React frontend or Slack export)
* Build a summary message layer (e.g., Slack-style card with chart and bullet point insights)

### Data Source Integration (Future Phases)

* Build modular connectors for:

  * Google Analytics API (GA4)
  * Stripe API (subscriptions, revenue)
  * Mixpanel/Amplitude (user events)
* Allow agent dispatching to route queries by source or data type

---

## 🗺️ Strategic Roadmap (UPDATED - Iterative)

| Phase        | Deliverable                    | Description                                                                    |
| ------------ | ------------------------------ | ------------------------------------------------------------------------------ |
| **Phase 1**  | Foundation Setup               | Create instant_dashboard folder, basic coordinator, test integration          |
| **Phase 2**  | QueryPlannerAgent              | Adapt BigQuery NL2SQL functionality, test with existing infrastructure        |
| **Phase 3**  | BigQueryRunnerAgent            | Add query execution, validate results                                          |
| **Phase 4**  | ChartGeneratorAgent            | Build JSON chart specifications (Chart.js compatible)                         |
| **Phase 5**  | InsightGeneratorAgent          | Add text insights and summaries                                                |
| **V1**       | End-to-end dashboard           | Complete pipeline: NL → SQL → Results → Charts → Insights                     |
| **V2**       | Multi-source agents            | Add SaaS APIs (GA4, Stripe, Mixpanel) with agent dispatching                  |
| **V3**       | Schedule & share insights      | Slack/email reports, recurring summaries                                       |
| **V4**       | Embedded assistant             | Use app as a copilot via REST API or React SDK                                |

**Current Status:** Ready to start Phase 1 - Foundation Setup

---

## 🧠 Final Statement

We are building a modern, modular alternative to Looker Studio — not a reporting tool, but a **data analysis assistant** that can:

* Understand questions
* Run accurate queries
* Visualize intelligently
* Evolve with your stack

By leveraging Google ADK and focusing on real-world needs, this agentic dashboard system aims to eliminate the complexity of dashboarding for founders, analysts, and operators alike.
