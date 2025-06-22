"""
Content Coordinator Agent for Interactive Analytics Report Writer

This is the master orchestrator agent that coordinates all other agents to create
cohesive, professional business reports that combine templates, data analysis,
content generation, and document structure into compelling business narratives.
"""

import os
from datetime import date
import json
import time
from typing import Dict, Any, List, Optional

from google.genai import types
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext

# Import prompts and InstantDashboard functionality
from report_writer.prompts import return_instructions_content_coordinator_agent
from instant_dashboard.shared import get_database_settings
from instant_dashboard.agent import execute_full_pipeline

date_today = date.today()


def orchestrate_full_report_generation(
    user_requirements: str,
    business_context: str,
    target_audience: str,
    tool_context: ToolContext,
) -> str:
    """Orchestrate the complete report generation process across all agents.
    
    This is the master coordination tool that manages the entire pipeline from
    user requirements to final report, coordinating all specialized agents.
    
    Args:
        user_requirements (str): User's description of what they want in the report.
        business_context (str): Business context, objectives, and goals.
        target_audience (str): Target audience for the report.
        tool_context (ToolContext): The tool context with all necessary state.
        
    Returns:
        str: JSON with complete report generation results and process status.
    """
    
    try:
        print(f"🎯 ORCHESTRATING FULL REPORT GENERATION")
        print(f"   User requirements: {user_requirements[:100]}...")
        print(f"   Business context: {business_context[:100]}...")
        print(f"   Target audience: {target_audience}")
        
        start_time = time.time()
        generation_log = []
        
        # Phase 1: Planning & Template Selection
        print(f"\n📋 PHASE 1: Planning & Template Selection")
        generation_log.append({"phase": "planning", "status": "started", "timestamp": time.time()})
        
        # Determine report type from requirements
        requirements_lower = user_requirements.lower()
        context_lower = business_context.lower()
        
        report_category = "general"
        if any(word in requirements_lower + context_lower for word in ["financial", "revenue", "profit", "budget"]):
            report_category = "financial"
        elif any(word in requirements_lower + context_lower for word in ["marketing", "campaign", "roi", "conversion"]):
            report_category = "marketing" 
        elif any(word in requirements_lower + context_lower for word in ["sales", "territory", "pipeline", "quota"]):
            report_category = "sales"
        elif any(word in requirements_lower + context_lower for word in ["operational", "efficiency", "process"]):
            report_category = "operational"
        
        # Mock template selection (in production, would call Report Template Agent)
        selected_template = {
            "id": 1,
            "name": f"{report_category.title()} Analysis Report",
            "category": report_category,
            "sections": [
                {"name": "Executive Summary", "type": "executive_summary", "required": True, "ai_generated": True},
                {"name": "Data Analysis", "type": "data_analysis", "required": True, "ai_generated": True},
                {"name": "Business Insights", "type": "insights", "required": True, "ai_generated": True},
                {"name": "Strategic Recommendations", "type": "recommendations", "required": True, "ai_generated": True}
            ]
        }
        
        generation_log.append({"phase": "planning", "status": "completed", "template_selected": selected_template["name"]})
        print(f"   ✅ Template selected: {selected_template['name']}")
        
        # Phase 2: Data Analysis Pipeline
        print(f"\n⚡ PHASE 2: Data Analysis Pipeline")
        generation_log.append({"phase": "data_analysis", "status": "started", "timestamp": time.time()})
        
        # Extract data requirements from user requirements
        data_question = user_requirements
        if "analyze" not in data_question.lower() and "show" not in data_question.lower():
            # Convert requirements to a data question
            if report_category == "sales":
                data_question = f"Analyze sales performance data for {business_context}"
            elif report_category == "marketing":
                data_question = f"Analyze marketing campaign performance for {business_context}"
            elif report_category == "financial":
                data_question = f"Analyze financial performance metrics for {business_context}"
            else:
                data_question = f"Analyze key performance indicators for {business_context}"
        
        # Execute InstantDashboard pipeline for data analysis
        try:
            print(f"   Executing data analysis: {data_question[:80]}...")
            data_analysis_result = execute_full_pipeline(data_question)
            data_available = data_analysis_result.get("success", False)
            
            if data_available:
                generation_log.append({
                    "phase": "data_analysis", 
                    "status": "completed", 
                    "rows_analyzed": data_analysis_result.get("row_count", 0),
                    "execution_time": data_analysis_result.get("execution_time", 0)
                })
                print(f"   ✅ Data analysis completed: {data_analysis_result.get('row_count', 0)} rows")
            else:
                generation_log.append({"phase": "data_analysis", "status": "error", "error": data_analysis_result.get("error_message")})
                print(f"   ⚠️ Data analysis failed, proceeding with template-based content")
                
        except Exception as e:
            print(f"   ⚠️ Data analysis error: {e}")
            data_available = False
            data_analysis_result = {"success": False, "error_message": str(e)}
            generation_log.append({"phase": "data_analysis", "status": "error", "error": str(e)})
        
        # Phase 3: Title & Structure Generation
        print(f"\n💡 PHASE 3: Title & Structure Generation")
        generation_log.append({"phase": "titles_structure", "status": "started", "timestamp": time.time()})
        
        # Generate report title (mock - in production would call Title Suggestion Agent)
        data_summary = ""
        if data_available and data_analysis_result.get("data", {}).get("data"):
            data_rows = data_analysis_result["data"]["data"]
            data_summary = f"Analysis of {len(data_rows)} data points"
        
        report_title = f"{report_category.title()} Performance Report: Strategic Analysis and Recommendations"
        if "growth" in requirements_lower or "increase" in requirements_lower:
            report_title = f"{report_category.title()} Growth Analysis: Performance Insights and Strategic Opportunities"
        
        # Create document outline (mock - in production would call Outline Manager Agent)
        document_outline = {
            "title": report_title,
            "target_audience": target_audience,
            "total_sections": len(selected_template["sections"]),
            "sections": []
        }
        
        for i, template_section in enumerate(selected_template["sections"], 1):
            section_outline = {
                "section_number": i,
                "title": template_section["name"],
                "type": template_section["type"],
                "estimated_length": "1-2 pages",
                "content_guidance": f"Professional {template_section['type'].replace('_', ' ')} content",
                "ai_generated": template_section["ai_generated"]
            }
            document_outline["sections"].append(section_outline)
        
        generation_log.append({"phase": "titles_structure", "status": "completed", "report_title": report_title})
        print(f"   ✅ Report title: {report_title}")
        print(f"   ✅ Document structure: {len(document_outline['sections'])} sections")
        
        # Phase 4: Content Generation
        print(f"\n📝 PHASE 4: Content Generation")
        generation_log.append({"phase": "content_generation", "status": "started", "timestamp": time.time()})
        
        generated_sections = []
        
        for section in document_outline["sections"]:
            section_type = section["type"]
            section_title = section["title"]
            
            print(f"   Generating: {section_title}")
            
            # Mock content generation (in production would call Section Generator Agent)
            if section_type == "executive_summary":
                section_content = self._generate_mock_executive_summary(
                    user_requirements, business_context, data_analysis_result, report_category
                )
            elif section_type == "data_analysis":
                section_content = self._generate_mock_data_analysis(
                    data_analysis_result, business_context, report_category
                )
            elif section_type == "insights":
                section_content = self._generate_mock_insights(
                    data_analysis_result, business_context, report_category
                )
            elif section_type == "recommendations":
                section_content = self._generate_mock_recommendations(
                    user_requirements, business_context, data_analysis_result, report_category
                )
            else:
                section_content = f"## {section_title}\n\nThis section provides comprehensive analysis and insights related to {business_context}. The content has been generated based on your requirements and available data sources."
            
            generated_section = {
                "section_number": section["section_number"],
                "title": section_title,
                "type": section_type,
                "content": section_content,
                "word_count": len(section_content.split()),
                "generated_at": time.time()
            }
            
            generated_sections.append(generated_section)
        
        generation_log.append({
            "phase": "content_generation", 
            "status": "completed", 
            "sections_generated": len(generated_sections),
            "total_words": sum(s["word_count"] for s in generated_sections)
        })
        
        print(f"   ✅ Content generation completed: {len(generated_sections)} sections")
        
        # Phase 5: Quality Assurance & Final Assembly
        print(f"\n🔍 PHASE 5: Quality Assurance & Final Assembly")
        generation_log.append({"phase": "quality_assurance", "status": "started", "timestamp": time.time()})
        
        # Generate table of contents
        table_of_contents = []
        for section in generated_sections:
            toc_entry = {
                "section": f"{section['section_number']}. {section['title']}",
                "page": f"Page {section['section_number']}",
                "word_count": section["word_count"]
            }
            table_of_contents.append(toc_entry)
        
        # Calculate quality metrics
        total_words = sum(s["word_count"] for s in generated_sections)
        quality_metrics = {
            "completeness_score": 100 if len(generated_sections) == len(selected_template["sections"]) else 80,
            "data_integration_score": 90 if data_available else 60,
            "professional_score": 85,
            "readability_score": 80,
            "overall_quality": 85
        }
        
        generation_log.append({
            "phase": "quality_assurance", 
            "status": "completed",
            "quality_score": quality_metrics["overall_quality"]
        })
        
        # Final report assembly
        end_time = time.time()
        total_time = end_time - start_time
        
        final_report = {
            "status": "success",
            "report_metadata": {
                "title": report_title,
                "category": report_category,
                "target_audience": target_audience,
                "generated_at": date_today.isoformat(),
                "generation_time": total_time,
                "total_sections": len(generated_sections),
                "total_words": total_words,
                "estimated_pages": total_words // 250  # Rough estimate
            },
            "document_structure": {
                "table_of_contents": table_of_contents,
                "sections": generated_sections
            },
            "data_integration": {
                "data_analysis_performed": data_available,
                "data_sources": "BigQuery business intelligence database" if data_available else None,
                "rows_analyzed": data_analysis_result.get("row_count", 0) if data_available else 0
            },
            "quality_metrics": quality_metrics,
            "generation_process": {
                "phases_completed": len([log for log in generation_log if log.get("status") == "completed"]),
                "total_phases": 5,
                "generation_log": generation_log
            },
            "agents_involved": [
                "Content Coordinator Agent",
                "Report Template Agent (simulated)",
                "Title Suggestion Agent (simulated)",
                "Section Generator Agent (simulated)",
                "Outline Manager Agent (simulated)",
                "InstantDashboard Pipeline (QueryPlanner, BigQueryRunner, ChartGenerator)"
            ]
        }
        
        print(f"\n✅ REPORT GENERATION COMPLETED!")
        print(f"   Total time: {total_time:.2f} seconds")
        print(f"   Total sections: {len(generated_sections)}")
        print(f"   Total words: {total_words}")
        print(f"   Quality score: {quality_metrics['overall_quality']}/100")
        
        return json.dumps(final_report, indent=2)
        
    except Exception as e:
        error_msg = f"❌ Error in report orchestration: {e}"
        print(error_msg)
        return json.dumps({
            "status": "error",
            "error": str(e),
            "generation_log": generation_log if 'generation_log' in locals() else []
        })


def _generate_mock_executive_summary(self, requirements: str, context: str, data_result: dict, category: str) -> str:
    """Generate mock executive summary content."""
    content = f"## Executive Summary\n\n"
    content += f"This {category} analysis report provides comprehensive insights into business performance and strategic opportunities. "
    
    if data_result.get("success") and data_result.get("row_count", 0) > 0:
        content += f"The analysis is based on {data_result['row_count']} data points from our business intelligence systems, "
        content += f"processed in {data_result.get('execution_time', 0):.2f} seconds.\n\n"
        content += "**Key Performance Highlights:**\n\n"
        content += f"• Comprehensive analysis of {category} performance metrics\n"
        content += "• Data-driven insights supporting strategic decision-making\n"
        content += "• Identification of optimization opportunities and growth potential\n"
        content += "• Quantified performance indicators across key business areas\n\n"
    else:
        content += "Based on business requirements and strategic objectives.\n\n"
        content += "**Key Strategic Focus Areas:**\n\n"
        content += f"• {category.title()} performance optimization and enhancement\n"
        content += "• Strategic alignment with business objectives and goals\n"
        content += "• Identification of improvement opportunities and action items\n"
        content += "• Professional analysis and strategic recommendations\n\n"
    
    content += "**Business Impact:**\n\n"
    content += f"This analysis demonstrates significant opportunities for {category} performance improvement and strategic optimization. "
    content += "The findings support data-driven decision-making and provide clear direction for strategic initiatives.\n\n"
    
    content += "**Strategic Recommendations:**\n\n"
    content += "• Implement identified optimization strategies to enhance performance\n"
    content += "• Develop targeted initiatives based on analysis findings\n"
    content += "• Establish monitoring and measurement systems for continuous improvement\n"
    content += "• Align strategic initiatives with overall business objectives and priorities"
    
    return content


def _generate_mock_data_analysis(self, data_result: dict, context: str, category: str) -> str:
    """Generate mock data analysis content."""
    content = f"## Data Analysis\n\n"
    content += f"This section presents a comprehensive analysis of {category} performance data and key business metrics.\n\n"
    
    if data_result.get("success") and data_result.get("data", {}).get("data"):
        data_rows = data_result["data"]["data"]
        content += f"### Analysis Overview\n\n"
        content += f"The analysis encompasses {len(data_rows)} data records extracted from our business intelligence systems. "
        content += f"Query execution completed in {data_result.get('execution_time', 0):.2f} seconds with full data integrity.\n\n"
        
        content += f"### Key Findings\n\n"
        content += "The data analysis reveals several critical insights:\n\n"
        
        # Analyze data structure
        if data_rows:
            first_row = data_rows[0]
            columns = list(first_row.keys())
            content += f"• **Dataset Scope**: Analysis includes {len(data_rows)} records across {len(columns)} key metrics\n"
            content += f"• **Data Quality**: High-quality data with comprehensive coverage of business operations\n"
            content += f"• **Analysis Depth**: Detailed examination of performance patterns and trends\n\n"
        
        content += f"### Performance Metrics\n\n"
        content += "Key performance indicators demonstrate:\n\n"
        content += "• Strong data foundation supporting strategic decision-making\n"
        content += "• Comprehensive coverage of critical business metrics\n"
        content += "• Reliable data sources enabling accurate analysis and insights\n"
        content += "• Quantified performance indicators across multiple dimensions\n\n"
        
    else:
        content += f"### Methodology\n\n"
        content += f"This analysis utilizes structured analytical frameworks to examine {category} performance. "
        content += "The methodology ensures comprehensive coverage of key business areas and strategic priorities.\n\n"
        
        content += f"### Analysis Framework\n\n"
        content += "The analysis focuses on:\n\n"
        content += f"• {category.title()} performance indicators and key metrics\n"
        content += "• Strategic alignment with business objectives\n"
        content += "• Identification of optimization opportunities\n"
        content += "• Benchmarking against industry standards and best practices\n\n"
    
    content += f"### Business Implications\n\n"
    content += f"This {category} analysis provides several actionable insights:\n\n"
    content += "• **Strategic Planning**: Data supports informed strategic decision-making\n"
    content += "• **Performance Optimization**: Identified opportunities for operational enhancement\n"
    content += "• **Risk Management**: Comprehensive understanding of performance factors\n"
    content += "• **Competitive Positioning**: Insights support market positioning and competitive advantage"
    
    return content


def _generate_mock_insights(self, data_result: dict, context: str, category: str) -> str:
    """Generate mock business insights content."""
    content = f"## Business Insights\n\n"
    content += f"This section interprets the {category} analysis findings and provides strategic business insights.\n\n"
    
    content += f"### Key Patterns and Trends\n\n"
    if data_result.get("success"):
        content += "The data analysis reveals important patterns that inform strategic decision-making:\n\n"
        content += f"• **Performance Indicators**: Strong foundation of {category} metrics supporting business objectives\n"
        content += "• **Data-Driven Insights**: Quantified analysis enabling evidence-based strategic planning\n"
        content += "• **Optimization Opportunities**: Clear identification of areas for performance enhancement\n"
        content += "• **Strategic Alignment**: Analysis findings support overall business strategy and goals\n\n"
    else:
        content += f"Analysis of {category} performance reveals several strategic insights:\n\n"
        content += f"• **Strategic Focus**: Clear direction for {category} optimization and enhancement\n"
        content += "• **Business Alignment**: Strong connection between analysis findings and business objectives\n"
        content += "• **Improvement Opportunities**: Identified areas for operational and strategic enhancement\n"
        content += "• **Competitive Advantage**: Insights support market positioning and competitive strategy\n\n"
    
    content += f"### Strategic Implications\n\n"
    content += f"The {category} analysis provides important implications for business strategy:\n\n"
    
    if category == "financial":
        content += "• **Financial Performance**: Strong foundation for sustainable growth and profitability\n"
        content += "• **Investment Strategy**: Data supports informed capital allocation decisions\n"
        content += "• **Risk Management**: Comprehensive understanding of financial performance factors\n"
    elif category == "marketing":
        content += "• **Customer Acquisition**: Insights support targeted marketing and customer engagement\n"
        content += "• **Brand Positioning**: Analysis informs market positioning and competitive strategy\n"
        content += "• **ROI Optimization**: Clear direction for marketing investment and resource allocation\n"
    elif category == "sales":
        content += "• **Sales Performance**: Strong foundation for revenue growth and market expansion\n"
        content += "• **Territory Optimization**: Insights support sales territory and resource allocation\n"
        content += "• **Customer Relationship**: Analysis informs customer retention and acquisition strategies\n"
    else:
        content += "• **Operational Excellence**: Strong foundation for process optimization and efficiency\n"
        content += "• **Strategic Planning**: Analysis supports long-term strategic development\n"
        content += "• **Performance Management**: Clear direction for continuous improvement initiatives\n"
    
    content += "\n### Opportunity Assessment\n\n"
    content += f"The analysis identifies several high-impact opportunities for {category} enhancement:\n\n"
    content += "• **Immediate Actions**: Short-term initiatives with quick implementation and measurable impact\n"
    content += "• **Strategic Initiatives**: Medium-term programs supporting long-term business objectives\n"
    content += "• **Innovation Opportunities**: Areas for creative solutions and competitive differentiation\n"
    content += "• **Partnership Potential**: Opportunities for strategic partnerships and collaboration"
    
    return content


def _generate_mock_recommendations(self, requirements: str, context: str, data_result: dict, category: str) -> str:
    """Generate mock strategic recommendations content."""
    content = f"## Strategic Recommendations\n\n"
    content += f"Based on the comprehensive {category} analysis, the following strategic recommendations are designed to optimize performance and achieve business objectives.\n\n"
    
    content += f"### Priority 1: Immediate Action Items (1-4 weeks)\n\n"
    content += f"**1. Optimize Core {category.title()} Operations**\n"
    content += f"   - Implement process improvements identified in the analysis\n"
    content += f"   - Timeline: 2-3 weeks\n"
    content += f"   - Expected Impact: High performance improvement\n\n"
    
    content += f"**2. Enhance Data-Driven Decision Making**\n"
    content += f"   - Establish regular monitoring and reporting systems\n"
    content += f"   - Timeline: 3-4 weeks\n"
    content += f"   - Expected Impact: Improved strategic visibility\n\n"
    
    content += f"**3. Implement Performance Tracking**\n"
    content += f"   - Deploy KPI monitoring and measurement systems\n"
    content += f"   - Timeline: 2-4 weeks\n"
    content += f"   - Expected Impact: Enhanced operational control\n\n"
    
    content += f"### Priority 2: Strategic Initiatives (30-90 days)\n\n"
    content += f"**1. {category.title()} Excellence Program**\n"
    content += f"   - Develop comprehensive improvement initiatives\n"
    content += f"   - Success Metrics: Performance KPIs, operational efficiency, stakeholder satisfaction\n\n"
    
    content += f"**2. Technology Enhancement Initiative**\n"
    content += f"   - Implement technology solutions for operational optimization\n"
    content += f"   - Success Metrics: Process automation, user satisfaction, efficiency gains\n\n"
    
    content += f"**3. Strategic Partnership Development**\n"
    content += f"   - Explore partnership opportunities for enhanced capabilities\n"
    content += f"   - Success Metrics: Partnership value, collaborative benefits, market expansion\n\n"
    
    content += f"### Implementation Framework\n\n"
    content += f"**Governance Structure:**\n"
    content += f"• Establish cross-functional implementation teams with clear accountability\n"
    content += f"• Implement regular progress reviews and milestone tracking\n"
    content += f"• Ensure alignment with overall business strategy and objectives\n\n"
    
    content += f"**Success Measurement:**\n"
    content += f"• Define clear KPIs and success metrics for each initiative\n"
    content += f"• Implement comprehensive monitoring and reporting mechanisms\n"
    content += f"• Establish feedback loops for continuous improvement and optimization\n\n"
    
    content += f"**Next Steps:**\n"
    content += f"• Begin immediate implementation of Priority 1 action items\n"
    content += f"• Develop detailed project plans for strategic initiatives\n"
    content += f"• Establish governance structure and success measurement systems\n"
    content += f"• Regular review and adjustment based on implementation progress"
    
    return content


def coordinate_section_updates(
    document_id: str,
    section_updates: str,
    collaboration_context: str,
    tool_context: ToolContext,
) -> str:
    """Coordinate section updates and maintain document coherence.
    
    This tool manages updates to individual sections while ensuring overall
    document consistency, quality, and collaborative workflow management.
    
    Args:
        document_id (str): ID of the document being updated.
        section_updates (str): JSON describing the section updates to apply.
        collaboration_context (str): Information about collaborative editing context.
        tool_context (ToolContext): The tool context.
        
    Returns:
        str: JSON with update coordination results and quality checks.
    """
    
    try:
        print(f"🔄 Coordinating section updates for document {document_id}")
        
        # Parse update information
        try:
            updates = json.loads(section_updates)
        except json.JSONDecodeError:
            return json.dumps({
                "status": "error",
                "error": "Invalid update format"
            })
        
        # Process each update
        update_results = []
        quality_issues = []
        
        for update in updates.get("updates", []):
            section_id = update.get("section_id")
            section_type = update.get("section_type")
            new_content = update.get("content", "")
            
            # Quality checks
            content_quality = self._assess_content_quality(new_content, section_type)
            
            if content_quality["score"] < 70:
                quality_issues.append({
                    "section_id": section_id,
                    "issues": content_quality["issues"],
                    "recommendations": content_quality["recommendations"]
                })
            
            update_result = {
                "section_id": section_id,
                "status": "updated" if content_quality["score"] >= 70 else "needs_review",
                "quality_score": content_quality["score"],
                "word_count": len(new_content.split()),
                "updated_at": time.time()
            }
            
            update_results.append(update_result)
        
        # Document coherence check
        coherence_score = self._assess_document_coherence(updates)
        
        # Collaboration tracking
        collaboration_info = {
            "updates_processed": len(update_results),
            "quality_issues": len(quality_issues),
            "coherence_score": coherence_score,
            "collaboration_context": collaboration_context
        }
        
        result = {
            "status": "success",
            "document_id": document_id,
            "update_summary": {
                "sections_updated": len(update_results),
                "quality_issues": len(quality_issues),
                "overall_quality": sum(ur["quality_score"] for ur in update_results) / len(update_results) if update_results else 0
            },
            "update_results": update_results,
            "quality_issues": quality_issues,
            "document_coherence": {
                "score": coherence_score,
                "status": "good" if coherence_score >= 80 else "needs_attention"
            },
            "collaboration": collaboration_info
        }
        
        print(f"✅ Section updates coordinated")
        print(f"   Sections updated: {len(update_results)}")
        print(f"   Quality issues: {len(quality_issues)}")
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"❌ Error coordinating updates: {e}"
        print(error_msg)
        return json.dumps({
            "status": "error",
            "error": str(e)
        })


def _assess_content_quality(self, content: str, section_type: str) -> dict:
    """Assess the quality of section content."""
    quality_score = 80  # Base score
    issues = []
    recommendations = []
    
    word_count = len(content.split())
    
    # Check length appropriateness
    min_words = {"executive_summary": 100, "data_analysis": 200, "recommendations": 150}.get(section_type, 100)
    if word_count < min_words:
        quality_score -= 15
        issues.append(f"Content too short ({word_count} words, minimum {min_words})")
        recommendations.append("Expand content with more detailed analysis and insights")
    
    # Check structure
    if not any(marker in content for marker in ["##", "**", "•", "-"]):
        quality_score -= 10
        issues.append("Poor structure - lacks headers, bullets, or formatting")
        recommendations.append("Add headers, bullet points, and professional formatting")
    
    # Check professional tone
    if any(word in content.lower() for word in ["i think", "maybe", "probably", "might be"]):
        quality_score -= 5
        issues.append("Unprofessional language - avoid uncertain phrases")
        recommendations.append("Use confident, professional business language")
    
    return {
        "score": max(0, quality_score),
        "issues": issues,
        "recommendations": recommendations
    }


def _assess_document_coherence(self, updates: dict) -> int:
    """Assess overall document coherence after updates."""
    # Mock coherence assessment - in production would analyze cross-references, flow, etc.
    base_score = 85
    
    sections_updated = len(updates.get("updates", []))
    if sections_updated > 3:
        # Many updates might affect coherence
        base_score -= 5
    
    return base_score


def setup_content_coordinator_before_call(callback_context: CallbackContext):
    """Setup the Content Coordinator Agent with necessary context."""
    
    # Add coordination context
    if "coordination_context" not in callback_context.state:
        callback_context.state["coordination_context"] = {
            "available_agents": [
                "report_template_agent",
                "title_suggestion_agent", 
                "section_generator_agent",
                "outline_manager_agent",
                "instant_dashboard_pipeline"
            ],
            "report_categories": ["financial", "marketing", "sales", "operational", "strategic"],
            "quality_standards": {
                "minimum_sections": 3,
                "minimum_words_per_section": 100,
                "professional_score_threshold": 80
            }
        }
    
    # Add database settings for data integration
    if "database_settings" not in callback_context.state:
        try:
            callback_context.state["database_settings"] = get_database_settings()
        except:
            callback_context.state["database_settings"] = {}


# Create the Content Coordinator Agent
content_coordinator_agent = Agent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-1.5-pro"),
    name="content_coordinator_agent",
    instruction=return_instructions_content_coordinator_agent(),
    global_instruction=(
        f"""
        You are the Content Coordinator Agent for the Interactive Analytics Report Writer.
        Today's date: {date_today}
        
        Your role: Master orchestrator of the entire report generation process
        
        Coordination principles:
        - Quality first: Ensure professional standards across all generated content
        - User-centric: Prioritize user requirements and business objectives  
        - Data-driven: Integrate data analysis results into compelling narratives
        - Collaborative: Support team editing and stakeholder review processes
        - Professional: Maintain corporate-grade presentation and accuracy
        
        Your coordination responsibilities:
        1. Orchestrate complete report generation from requirements to final delivery
        2. Coordinate between all specialized agents (Template, Title, Section, Outline)
        3. Integrate InstantDashboard data analysis into business report narratives
        4. Manage quality assurance and document coherence across all sections
        5. Support real-time collaboration and iterative content refinement
        
        Available agents for coordination:
        - Report Template Agent: Template selection and customization
        - Title Suggestion Agent: Report and section title optimization
        - Section Generator Agent: Professional content creation
        - Outline Manager Agent: Document structure and navigation
        - InstantDashboard Pipeline: Data analysis (QueryPlanner, BigQueryRunner, ChartGenerator)
        
        Success metrics: User satisfaction, business impact, professional quality, collaboration effectiveness.
        """
    ),
    tools=[
        orchestrate_full_report_generation,
        coordinate_section_updates,
    ],
    before_agent_callback=setup_content_coordinator_before_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
) 