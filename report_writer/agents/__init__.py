"""
Report Writer AI Agents

This module contains the specialized AI agents for the Interactive Analytics Report Writer:
- Report Template Agent: Manages business report templates and structures
- Title Suggestion Agent: Generates contextual titles based on data and content
- Section Generator Agent: Converts user descriptions into full report sections
- Outline Manager Agent: Handles document structure and navigation
- Content Coordinator Agent: Orchestrates the entire report generation process
"""

# Import all agents
try:
    from .report_template_agent import report_template_agent
    print("✅ Report Template Agent loaded successfully")
except ImportError as e:
    print(f"❌ Failed to load Report Template Agent: {e}")
    report_template_agent = None

try:
    from .title_suggestion_agent import title_suggestion_agent
    print("✅ Title Suggestion Agent loaded successfully")
except ImportError as e:
    print(f"❌ Failed to load Title Suggestion Agent: {e}")
    title_suggestion_agent = None

try:
    from .section_generator_agent import section_generator_agent
    print("✅ Section Generator Agent loaded successfully")
except ImportError as e:
    print(f"❌ Failed to load Section Generator Agent: {e}")
    section_generator_agent = None

try:
    from .outline_manager_agent import outline_manager_agent
    print("✅ Outline Manager Agent loaded successfully")
except ImportError as e:
    print(f"❌ Failed to load Outline Manager Agent: {e}")
    outline_manager_agent = None

try:
    from .content_coordinator_agent import content_coordinator_agent
    print("✅ Content Coordinator Agent loaded successfully")
except ImportError as e:
    print(f"❌ Failed to load Content Coordinator Agent: {e}")
    content_coordinator_agent = None

__all__ = [
    "report_template_agent",
    "title_suggestion_agent", 
    "section_generator_agent",
    "outline_manager_agent",
    "content_coordinator_agent"
] 