# ISO 31000 framework mapper

from src.models import RiskClassification

def map_to_iso31000(classification: RiskClassification) -> list[str]:
    """
    Maps a RiskClassification to relevant ISO 31000 framework principles/clauses.
    Enhances placeholder logic based on incident details.
    """
    iso_tags = set() # Use a set to avoid duplicate tags

    incident_lower = classification.incident_description.lower()
    root_cause_lower = classification.root_cause.lower()
    control_recs_lower = " ".join(classification.control_recommendations).lower() if isinstance(classification.control_recommendations, list) else ""

    # Mapping based on the provided blueprint descriptions
    if any(keyword in incident_lower or keyword in root_cause_lower for keyword in ["missed risk", "ignored risk", "failed to identify"]):
        iso_tags.add("ISO 31000 - Risk Identification")

    if any(keyword in incident_lower or keyword in root_cause_lower or keyword in control_recs_lower for keyword in ["poor escalation", "reporting failure", "lack of communication", "information sharing failure"]):
        iso_tags.add("ISO 31000 - Risk Communication")

    if any(keyword in incident_lower or keyword in root_cause_lower or keyword in control_recs_lower for keyword in ["control outdated", "unmanaged control", "review failure", "monitoring failure"]):
        iso_tags.add("ISO 31000 - Monitoring and Review")

    # Retain some of the original placeholder logic for broader coverage
    if "compliance" in incident_lower or "legal" in classification.basel_ii_category.lower():
         iso_tags.add("ISO 31000 - Clause 6: Process")
         iso_tags.add("ISO 31000 - Principle 4: Be part of decision making")

    if "security" in incident_lower or "technology" in classification.basel_ii_category.lower():
         iso_tags.add("ISO 31000 - Principle 6: Be dynamic, iterative and responsive to change")

    # Convert set back to list before returning
    return list(iso_tags)