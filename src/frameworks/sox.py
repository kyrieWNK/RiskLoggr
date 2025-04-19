# SOX framework mapper

from src.models import RiskClassification

def map_to_sox(classification: RiskClassification) -> list[str]:
    """
    Maps a RiskClassification to relevant SOX framework sections.
    Enhances placeholder logic based on incident details.
    """
    sox_tags = set() # Use a set to avoid duplicate tags

    incident_lower = classification.incident_description.lower()
    root_cause_lower = classification.root_cause.lower()
    control_recs_lower = " ".join(classification.control_recommendations).lower() if isinstance(classification.control_recommendations, list) else ""

    # Mapping based on the provided blueprint descriptions
    if any(keyword in incident_lower or keyword in root_cause_lower or keyword in control_recs_lower for keyword in ["disclosure control", "unauthorized access", "data leak"]):
        sox_tags.add("SOX - Section 302")

    if any(keyword in incident_lower or keyword in root_cause_lower or keyword in control_recs_lower for keyword in ["financial control failure", "lack of testing", "control weakness", "audit finding"]):
        sox_tags.add("SOX - Section 404")

    # Retain some of the original placeholder logic for broader coverage
    if "financial" in incident_lower or "financial" in classification.basel_ii_category.lower():
         sox_tags.add("SOX - Section 302")
         sox_tags.add("SOX - Section 404")

    if "reporting" in incident_lower:
         sox_tags.add("SOX - Section 906") # Section 906 relates to corporate responsibility for financial reports

    # Convert set back to list before returning
    return list(sox_tags)