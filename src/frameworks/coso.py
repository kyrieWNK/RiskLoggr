# COSO framework mapper

from src.models import RiskClassification

def map_to_coso(classification: RiskClassification) -> list[str]:
    """
    Maps a RiskClassification to relevant COSO framework principles/components.
    Enhances placeholder logic based on incident details.
    """
    coso_tags = set() # Use a set to avoid duplicate tags

    incident_lower = classification.incident_description.lower()
    root_cause_lower = classification.root_cause.lower()
    control_recs_lower = " ".join(classification.control_recommendations).lower() if isinstance(classification.control_recommendations, list) else ""

    # Mapping based on the provided blueprint descriptions
    if any(keyword in incident_lower or keyword in root_cause_lower for keyword in ["incomplete analysis", "missing analysis", "inadequate assessment"]):
        coso_tags.add("COSO - Risk Assessment")

    if any(keyword in incident_lower or keyword in root_cause_lower or keyword in control_recs_lower for keyword in ["control not followed", "misconfigured control", "control failure", "policy violation"]):
        coso_tags.add("COSO - Control Activities")

    if any(keyword in incident_lower or keyword in root_cause_lower for keyword in ["not detected", "issue missed", "monitoring failure", "untimely detection"]):
        coso_tags.add("COSO - Monitoring Activities")

    # Retain some of the original placeholder logic for broader coverage
    if "fraud" in incident_lower or "fraud" in classification.basel_ii_category.lower():
         coso_tags.add("COSO - Control Environment")
         coso_tags.add("COSO - Risk Assessment") # Keep Risk Assessment as fraud often implies assessment failure

    if "system" in incident_lower or "technology" in classification.basel_ii_category.lower():
         coso_tags.add("COSO - Information & Communication")
         coso_tags.add("COSO - Monitoring Activities") # Keep Monitoring as system issues can be detection failures

    # Convert set back to list before returning
    return list(coso_tags)