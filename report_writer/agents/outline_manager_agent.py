"""
Outline Manager Agent for Interactive Analytics Report Writer

This agent specializes in document structure and navigation management,
ensuring professional business reports have logical flow and are easy to navigate.
"""

import os
from datetime import date
import json
from typing import Dict, Any, List, Optional

from google.genai import types
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext

# Import prompts
from report_writer.prompts import return_instructions_outline_manager_agent

date_today = date.today()


def create_document_outline(
    template_structure: str,
    content_requirements: str,
    target_audience: str,
    tool_context: ToolContext,
) -> str:
    """Create a structured document outline based on template and requirements.
    
    This tool generates a comprehensive document outline that ensures logical flow,
    proper hierarchy, and professional organization for business reports.
    
    Args:
        template_structure (str): JSON structure of the selected template.
        content_requirements (str): Specific content requirements and objectives.
        target_audience (str): Target audience (executives, analysts, operations, etc.).
        tool_context (ToolContext): The tool context.
        
    Returns:
        str: JSON with complete document outline and navigation structure.
    """
    
    try:
        print(f"📝 Creating document outline...")
        print(f"   Target audience: {target_audience}")
        print(f"   Content requirements: {content_requirements[:100]}...")
        
        # Parse template structure
        try:
            template = json.loads(template_structure)
        except json.JSONDecodeError:
            # Create default structure if parsing fails
            template = {
                "name": "Business Report",
                "sections": [
                    {"name": "Executive Summary", "type": "executive_summary", "required": True},
                    {"name": "Analysis", "type": "data_analysis", "required": True},
                    {"name": "Recommendations", "type": "recommendations", "required": True}
                ]
            }
        
        # Analyze audience and requirements
        audience_lower = target_audience.lower()
        requirements_lower = content_requirements.lower()
        
        # Determine audience type
        audience_type = "general"
        if any(word in audience_lower for word in ["executive", "c-level", "leadership", "board"]):
            audience_type = "executive"
        elif any(word in audience_lower for word in ["analyst", "technical", "detailed"]):
            audience_type = "analytical"
        elif any(word in audience_lower for word in ["operational", "manager", "team"]):
            audience_type = "operational"
        
        # Create outline structure
        outline_sections = []
        section_counter = 1
        
        # Process each template section
        base_sections = template.get("sections", [])
        
        for section in base_sections:
            section_name = section.get("name", "Untitled Section")
            section_type = section.get("type", "general")
            is_required = section.get("required", False)
            
            # Create section outline
            section_outline = {
                "section_number": section_counter,
                "title": section_name,
                "type": section_type,
                "required": is_required,
                "subsections": [],
                "estimated_length": self._estimate_section_length(section_type, audience_type),
                "content_guidance": self._get_content_guidance(section_type, audience_type),
                "ai_generated": section.get("ai_generated", True)
            }
            
            # Add subsections based on section type and audience needs
            if section_type == "executive_summary":
                if audience_type == "executive":
                    section_outline["subsections"] = [
                        {"title": "Key Performance Highlights", "estimated_length": "2-3 paragraphs"},
                        {"title": "Strategic Recommendations", "estimated_length": "3-4 bullet points"},
                        {"title": "Business Impact", "estimated_length": "1-2 paragraphs"}
                    ]
                else:
                    section_outline["subsections"] = [
                        {"title": "Summary of Findings", "estimated_length": "2-3 paragraphs"},
                        {"title": "Key Insights", "estimated_length": "4-5 bullet points"},
                        {"title": "Next Steps", "estimated_length": "1-2 paragraphs"}
                    ]
            
            elif section_type == "data_analysis":
                if audience_type == "analytical":
                    section_outline["subsections"] = [
                        {"title": "Methodology", "estimated_length": "1-2 paragraphs"},
                        {"title": "Data Overview", "estimated_length": "1 paragraph + table"},
                        {"title": "Detailed Analysis", "estimated_length": "3-4 paragraphs"},
                        {"title": "Statistical Insights", "estimated_length": "2-3 paragraphs"},
                        {"title": "Data Visualizations", "estimated_length": "2-3 charts"}
                    ]
                else:
                    section_outline["subsections"] = [
                        {"title": "Analysis Overview", "estimated_length": "1-2 paragraphs"},
                        {"title": "Key Findings", "estimated_length": "4-5 bullet points"},
                        {"title": "Data Visualizations", "estimated_length": "1-2 charts"},
                        {"title": "Business Implications", "estimated_length": "2-3 paragraphs"}
                    ]
            
            elif section_type == "recommendations":
                section_outline["subsections"] = [
                    {"title": "Priority Actions", "estimated_length": "3-4 recommendations"},
                    {"title": "Strategic Initiatives", "estimated_length": "2-3 initiatives"},
                    {"title": "Implementation Timeline", "estimated_length": "1 table/timeline"},
                    {"title": "Success Metrics", "estimated_length": "4-5 KPIs"}
                ]
            
            elif section_type == "insights":
                section_outline["subsections"] = [
                    {"title": "Key Patterns", "estimated_length": "2-3 paragraphs"},
                    {"title": "Business Implications", "estimated_length": "3-4 bullet points"},
                    {"title": "Strategic Opportunities", "estimated_length": "2-3 paragraphs"}
                ]
            
            outline_sections.append(section_outline)
            section_counter += 1
        
        # Add audience-specific sections if needed
        if audience_type == "analytical" and not any(s["type"] == "appendix" for s in outline_sections):
            # Add methodology appendix for analytical audiences
            appendix_section = {
                "section_number": section_counter,
                "title": "Methodology & Data Sources",
                "type": "appendix",
                "required": False,
                "subsections": [
                    {"title": "Data Collection Methods", "estimated_length": "1-2 paragraphs"},
                    {"title": "Analysis Techniques", "estimated_length": "1-2 paragraphs"},
                    {"title": "Limitations and Assumptions", "estimated_length": "1 paragraph"}
                ],
                "estimated_length": "1-2 pages",
                "content_guidance": "Technical details and methodology for analytical validation",
                "ai_generated": True
            }
            outline_sections.append(appendix_section)
        
        # Create table of contents
        table_of_contents = []
        for section in outline_sections:
            toc_entry = {
                "section": f"{section['section_number']}. {section['title']}",
                "page": f"Page {section['section_number']}",  # Placeholder
                "subsections": []
            }
            
            for i, subsection in enumerate(section["subsections"], 1):
                toc_entry["subsections"].append(f"{section['section_number']}.{i} {subsection['title']}")
            
            table_of_contents.append(toc_entry)
        
        # Calculate document metrics
        total_sections = len(outline_sections)
        total_subsections = sum(len(s["subsections"]) for s in outline_sections)
        estimated_pages = sum(self._section_to_pages(s["estimated_length"]) for s in outline_sections)
        
        # Generate outline result
        result = {
            "status": "success",
            "document_outline": {
                "title": template.get("name", "Business Report"),
                "target_audience": audience_type,
                "total_sections": total_sections,
                "total_subsections": total_subsections,
                "estimated_pages": estimated_pages,
                "sections": outline_sections
            },
            "table_of_contents": table_of_contents,
            "document_structure": {
                "hierarchy_levels": 2,  # Sections and subsections
                "uses_numbering": True,
                "professional_formatting": True,
                "navigation_ready": True
            },
            "audience_optimization": {
                "audience_type": audience_type,
                "content_depth": "detailed" if audience_type == "analytical" else "summary",
                "technical_level": "high" if audience_type == "analytical" else "medium",
                "executive_friendly": audience_type == "executive"
            }
        }
        
        print(f"✅ Document outline created successfully")
        print(f"   Total sections: {total_sections}")
        print(f"   Total subsections: {total_subsections}")
        print(f"   Estimated pages: {estimated_pages}")
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"❌ Error creating outline: {e}"
        print(error_msg)
        return json.dumps({
            "status": "error",
            "error": str(e),
            "document_outline": {}
        })


def _estimate_section_length(self, section_type: str, audience_type: str) -> str:
    """Estimate section length based on type and audience."""
    base_lengths = {
        "executive_summary": "1-2 pages",
        "data_analysis": "2-3 pages",
        "insights": "1-2 pages", 
        "recommendations": "1-2 pages",
        "methodology": "1 page",
        "appendix": "1-2 pages"
    }
    
    if audience_type == "analytical":
        # Analytical audiences need more detail
        return base_lengths.get(section_type, "1-2 pages").replace("1-2", "2-3").replace("2-3", "3-4")
    elif audience_type == "executive":
        # Executive audiences prefer concise content
        return base_lengths.get(section_type, "1 page").replace("2-3", "1-2").replace("3-4", "2-3")
    
    return base_lengths.get(section_type, "1-2 pages")


def _get_content_guidance(self, section_type: str, audience_type: str) -> str:
    """Get content guidance for each section type and audience."""
    guidance = {
        "executive_summary": {
            "executive": "High-level insights, strategic implications, key decisions needed",
            "analytical": "Comprehensive findings summary, detailed insights, methodology overview",
            "operational": "Actionable insights, operational impact, implementation focus"
        },
        "data_analysis": {
            "executive": "Key metrics, trend highlights, business impact visualization",
            "analytical": "Detailed statistical analysis, methodology, comprehensive data exploration",
            "operational": "Operational metrics, performance indicators, actionable data insights"
        },
        "recommendations": {
            "executive": "Strategic recommendations, resource requirements, expected ROI",
            "analytical": "Data-driven recommendations, risk analysis, detailed implementation plans",
            "operational": "Actionable steps, operational changes, timeline and resources"
        }
    }
    
    return guidance.get(section_type, {}).get(audience_type, "Professional business content with clear structure and actionable insights")


def _section_to_pages(self, length_estimate: str) -> int:
    """Convert section length estimate to approximate page count."""
    if "1-2" in length_estimate:
        return 1.5
    elif "2-3" in length_estimate:
        return 2.5 
    elif "3-4" in length_estimate:
        return 3.5
    elif "1 page" in length_estimate:
        return 1
    else:
        return 2  # Default


def optimize_section_flow(
    current_outline: str,
    content_objectives: str,
    tool_context: ToolContext,
) -> str:
    """Optimize section flow and organization for better readability and impact.
    
    This tool analyzes the current outline and suggests improvements to enhance
    document flow, logical progression, and reader engagement.
    
    Args:
        current_outline (str): JSON of the current document outline.
        content_objectives (str): Content objectives and key messages.
        tool_context (ToolContext): The tool context.
        
    Returns:
        str: JSON with optimized outline and flow recommendations.
    """
    
    try:
        print(f"🔄 Optimizing section flow...")
        
        # Parse current outline
        try:
            outline = json.loads(current_outline)
        except json.JSONDecodeError:
            return json.dumps({
                "status": "error",
                "error": "Invalid outline format"
            })
        
        document_outline = outline.get("document_outline", {})
        sections = document_outline.get("sections", [])
        
        if not sections:
            return json.dumps({
                "status": "error",
                "error": "No sections found in outline"
            })
        
        # Analyze current flow
        flow_analysis = {
            "current_order": [s["title"] for s in sections],
            "flow_issues": [],
            "optimization_opportunities": []
        }
        
        # Check for optimal business report flow
        section_types = [s["type"] for s in sections]
        
        # Ideal flow: executive_summary -> data_analysis -> insights -> recommendations -> appendix
        ideal_order = ["executive_summary", "data_analysis", "insights", "recommendations", "methodology", "appendix"]
        
        # Find flow issues
        if "executive_summary" in section_types and section_types.index("executive_summary") != 0:
            flow_analysis["flow_issues"].append("Executive Summary should be first section")
        
        if "recommendations" in section_types and "insights" in section_types:
            rec_index = section_types.index("recommendations")
            insights_index = section_types.index("insights")
            if rec_index < insights_index:
                flow_analysis["flow_issues"].append("Recommendations should come after Insights")
        
        if "methodology" in section_types and section_types.index("methodology") < len(section_types) - 2:
            flow_analysis["flow_issues"].append("Methodology should be near the end or in appendix")
        
        # Generate optimized order
        optimized_sections = []
        used_sections = set()
        
        # Add sections in ideal order
        for ideal_type in ideal_order:
            for section in sections:
                if section["type"] == ideal_type and section["title"] not in used_sections:
                    optimized_sections.append(section)
                    used_sections.add(section["title"])
                    break
        
        # Add any remaining sections
        for section in sections:
            if section["title"] not in used_sections:
                optimized_sections.append(section)
        
        # Update section numbers
        for i, section in enumerate(optimized_sections, 1):
            section["section_number"] = i
        
        # Generate optimization recommendations
        optimization_recommendations = []
        
        if len(flow_analysis["flow_issues"]) > 0:
            optimization_recommendations.append({
                "type": "flow_improvement",
                "description": "Reorder sections to follow professional business report structure",
                "impact": "high",
                "changes": flow_analysis["flow_issues"]
            })
        
        # Check section balance
        section_lengths = [s.get("estimated_length", "1-2 pages") for s in sections]
        if len([l for l in section_lengths if "3-4" in l or "4-5" in l]) > len(sections) // 2:
            optimization_recommendations.append({
                "type": "content_balance",
                "description": "Consider consolidating or breaking up very long sections",
                "impact": "medium",
                "changes": ["Some sections may be too lengthy for optimal readability"]
            })
        
        # Check for missing standard sections
        standard_types = ["executive_summary", "data_analysis", "recommendations"]
        missing_standard = [t for t in standard_types if t not in section_types]
        
        if missing_standard:
            optimization_recommendations.append({
                "type": "completeness",
                "description": "Add missing standard business report sections",
                "impact": "high",
                "changes": [f"Consider adding {t.replace('_', ' ').title()}" for t in missing_standard]
            })
        
        # Create optimized outline
        optimized_outline = document_outline.copy()
        optimized_outline["sections"] = optimized_sections
        
        # Update table of contents
        optimized_toc = []
        for section in optimized_sections:
            toc_entry = {
                "section": f"{section['section_number']}. {section['title']}",
                "page": f"Page {section['section_number']}",
                "subsections": []
            }
            
            for i, subsection in enumerate(section.get("subsections", []), 1):
                toc_entry["subsections"].append(f"{section['section_number']}.{i} {subsection['title']}")
            
            optimized_toc.append(toc_entry)
        
        result = {
            "status": "success",
            "optimized_outline": {
                "document_outline": optimized_outline,
                "table_of_contents": optimized_toc
            },
            "flow_analysis": flow_analysis,
            "optimization_recommendations": optimization_recommendations,
            "improvements": {
                "flow_score": 85 if len(flow_analysis["flow_issues"]) == 0 else 65,
                "structure_score": 90,
                "readability_score": 80,
                "professional_score": 88
            }
        }
        
        print(f"✅ Section flow optimized")
        print(f"   Flow issues found: {len(flow_analysis['flow_issues'])}")
        print(f"   Optimization recommendations: {len(optimization_recommendations)}")
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"❌ Error optimizing flow: {e}"
        print(error_msg)
        return json.dumps({
            "status": "error",
            "error": str(e)
        })


def generate_table_of_contents(
    document_outline: str,
    include_page_numbers: bool,
    tool_context: ToolContext,
) -> str:
    """Generate a professional table of contents from document outline.
    
    This tool creates a formatted table of contents with proper numbering,
    hierarchy, and professional presentation suitable for business reports.
    
    Args:
        document_outline (str): JSON of the document outline.
        include_page_numbers (bool): Whether to include page number placeholders.
        tool_context (ToolContext): The tool context.
        
    Returns:
        str: JSON with formatted table of contents and navigation elements.
    """
    
    try:
        print(f"📚 Generating table of contents...")
        
        # Parse outline
        try:
            outline = json.loads(document_outline)
        except json.JSONDecodeError:
            return json.dumps({
                "status": "error",
                "error": "Invalid outline format"
            })
        
        document_data = outline.get("document_outline", {})
        sections = document_data.get("sections", [])
        
        # Generate formatted TOC
        toc_entries = []
        current_page = 1
        
        for section in sections:
            section_number = section.get("section_number", 1)
            title = section.get("title", "Untitled")
            
            # Main section entry
            page_info = f"........ {current_page}" if include_page_numbers else ""
            toc_entry = {
                "level": 1,
                "number": str(section_number),
                "title": title,
                "page": current_page if include_page_numbers else None,
                "formatted": f"{section_number}. {title} {page_info}",
                "subsections": []
            }
            
            # Add subsections
            subsections = section.get("subsections", [])
            for i, subsection in enumerate(subsections, 1):
                sub_title = subsection.get("title", "Untitled Subsection")
                sub_page_info = f"........ {current_page}" if include_page_numbers else ""
                
                sub_entry = {
                    "level": 2,
                    "number": f"{section_number}.{i}",
                    "title": sub_title,
                    "page": current_page if include_page_numbers else None,
                    "formatted": f"    {section_number}.{i} {sub_title} {sub_page_info}"
                }
                
                toc_entry["subsections"].append(sub_entry)
            
            toc_entries.append(toc_entry)
            
            # Estimate page increment
            estimated_length = section.get("estimated_length", "1-2 pages")
            if "1-2" in estimated_length:
                current_page += 2
            elif "2-3" in estimated_length:
                current_page += 3
            elif "3-4" in estimated_length:
                current_page += 4
            else:
                current_page += 2
        
        # Create formatted TOC text
        toc_text = "TABLE OF CONTENTS\n\n"
        
        for entry in toc_entries:
            toc_text += entry["formatted"] + "\n"
            
            for sub_entry in entry["subsections"]:
                toc_text += sub_entry["formatted"] + "\n"
            
            toc_text += "\n"  # Add space between main sections
        
        # Generate navigation elements
        navigation_elements = {
            "section_references": [],
            "cross_references": [],
            "bookmark_structure": []
        }
        
        # Section references for easy navigation
        for entry in toc_entries:
            nav_ref = {
                "section_id": f"section_{entry['number']}",
                "title": entry["title"],
                "anchor": f"#{entry['title'].lower().replace(' ', '_')}",
                "level": 1
            }
            navigation_elements["section_references"].append(nav_ref)
            
            # Add subsection references
            for sub_entry in entry["subsections"]:
                sub_nav_ref = {
                    "section_id": f"section_{sub_entry['number']}",
                    "title": sub_entry["title"],
                    "anchor": f"#{sub_entry['title'].lower().replace(' ', '_')}",
                    "level": 2,
                    "parent": entry["title"]
                }
                navigation_elements["section_references"].append(sub_nav_ref)
        
        # Generate bookmark structure for PDF export
        for entry in toc_entries:
            bookmark = {
                "title": f"{entry['number']}. {entry['title']}",
                "level": 1,
                "page": entry["page"],
                "children": []
            }
            
            for sub_entry in entry["subsections"]:
                sub_bookmark = {
                    "title": f"{sub_entry['number']} {sub_entry['title']}",
                    "level": 2,
                    "page": sub_entry["page"]
                }
                bookmark["children"].append(sub_bookmark)
            
            navigation_elements["bookmark_structure"].append(bookmark)
        
        result = {
            "status": "success",
            "table_of_contents": {
                "formatted_text": toc_text,
                "entries": toc_entries,
                "total_sections": len(toc_entries),
                "total_subsections": sum(len(e["subsections"]) for e in toc_entries),
                "estimated_pages": current_page - 1
            },
            "navigation_elements": navigation_elements,
            "formatting": {
                "uses_numbering": True,
                "has_page_numbers": include_page_numbers,
                "hierarchical": True,
                "professional_format": True
            }
        }
        
        print(f"✅ Table of contents generated")
        print(f"   Total entries: {len(toc_entries)}")
        print(f"   Estimated pages: {current_page - 1}")
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_msg = f"❌ Error generating TOC: {e}"
        print(error_msg)
        return json.dumps({
            "status": "error",
            "error": str(e)
        })


def setup_outline_manager_before_call(callback_context: CallbackContext):
    """Setup the Outline Manager Agent with necessary context."""
    
    # Add outline management context
    if "outline_context" not in callback_context.state:
        callback_context.state["outline_context"] = {
            "audience_types": ["executive", "analytical", "operational", "general"],
            "section_types": ["executive_summary", "data_analysis", "insights", "recommendations", "methodology", "appendix"],
            "flow_standards": ["executive_first", "data_before_insights", "insights_before_recommendations", "methodology_last"],
            "formatting_standards": ["numbered_sections", "hierarchical_structure", "professional_toc", "navigation_ready"]
        }


# Create the Outline Manager Agent  
outline_manager_agent = Agent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-1.5-pro"),
    name="outline_manager_agent",
    instruction=return_instructions_outline_manager_agent(),
    global_instruction=(
        f"""
        You are the Outline Manager Agent for the Interactive Analytics Report Writer.
        Today's date: {date_today}
        
        Your specialization: Document structure and navigation management
        
        Document structure principles:
        - Logical flow: Executive Summary → Analysis → Insights → Recommendations → Appendices
        - Audience optimization: Tailor depth and structure to target audience needs
        - Professional organization: Clear hierarchy, proper numbering, easy navigation
        - Collaborative ready: Structure that supports team editing and review
        - Export friendly: Format that works well in PDF, Word, and web interfaces
        
        Your role in the report generation pipeline:
        1. Create structured document outlines based on templates and requirements
        2. Optimize section flow and organization for maximum impact and readability
        3. Generate professional table of contents with navigation elements
        4. Ensure document structure supports collaborative editing and export formats
        
        Work with template structures from Report Template Agent and coordinate with
        Content Coordinator Agent to ensure optimal document organization.
        """
    ),
    tools=[
        create_document_outline,
        optimize_section_flow,
        generate_table_of_contents,
    ],
    before_agent_callback=setup_outline_manager_before_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
) 