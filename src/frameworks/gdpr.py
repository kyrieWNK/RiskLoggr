# GDPR framework mapper

from src.models import RiskClassification

def map_to_gdpr(classification: RiskClassification) -> list[str]:
    """
    Maps a RiskClassification to relevant GDPR articles/principles.
    Enhances placeholder logic based on incident details.
    """
    gdpr_tags = set() # Use a set to avoid duplicate tags

    incident_lower = classification.incident_description.lower()
    root_cause_lower = classification.root_cause.lower()
    control_recs_lower = " ".join(classification.control_recommendations).lower() if isinstance(classification.control_recommendations, list) else ""

    # Mapping based on the provided blueprint descriptions
    if any(keyword in incident_lower or keyword in root_cause_lower for keyword in ["access breach", "confidentiality breach", "data leak", "unauthorized access"]):
        gdpr_tags.add("GDPR - Article 5: Integrity & Confidentiality")

    if any(keyword in incident_lower or keyword in root_cause_lower for keyword in ["unauthorized processing", "lack of consent", "non-compliant processing"]):
        gdpr_tags.add("GDPR - Article 6: Lawful Basis")

    if any(keyword in incident_lower or keyword in root_cause_lower or keyword in control_recs_lower for keyword in ["security failure", "no encryption", "inadequate security measures"]):
        gdpr_tags.add("GDPR - Article 32: Security of Processing")

    # Retain some of the original placeholder logic for broader coverage
    if "data breach" in incident_lower or "privacy" in classification.basel_ii_category.lower():
         gdpr_tags.add("GDPR - Article 33: Notification of a personal data breach to the supervisory authority")
         gdpr_tags.add("GDPR - Article 34: Communication of a personal data breach to the data subject")

    if "personal data" in incident_lower:
         gdpr_tags.add("GDPR - Article 5: Principles relating to processing of personal data") # Keep for broader Article 5 relevance

    # Convert set back to list before returning
    return list(gdpr_tags)