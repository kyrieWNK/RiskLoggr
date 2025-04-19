import openai
from typing import Optional
from typing import Union
import json # Import json for parsing the response
from ..config.config import settings # Import settings from the config module
from src.models import RiskClassification

# Configure the OpenAI API key
openai.api_key = settings.OPENAI_API_KEY

def classify_incident(incident_description: str) -> Optional[RiskClassification]:
    from src.frameworks.framework_router import classify_across_frameworks

    """
    Classifies an operational risk incident using an LLM.

    Args:
        incident_description: The description of the incident.

    Returns:
        A RiskClassification object if successful, None otherwise.
    """
    if not openai.api_key:
        print("OpenAI API key is not configured.")
        return None

    try:
        # Craft a prompt for the LLM
        prompt = f"""
        Classify the following operational risk incident, executive summary style.
        Additionally, estimate the inherent risk, residual risk (assuming control recommendations are implemented), likelihood, and impact type.
        Return the result as valid JSON with the following keys:
        - basel_ii_category: string (Based on Basel II operational risk categories)
        - severity_score: integer (1-5, 1=Low, 5=High)
        - root_cause: string (natural, plain English)
        - control_recommendations: list of clearly written, full-sentence recommendations in natural language. DO NOT number them or return an object with keys like 0, 1, 2. Just return a clean JSON list.
        - inherent_risk: string (Estimate the risk level before controls, e.g., "Low", "Medium", "High", "Very High")
        - residual_risk: string (Estimate the risk level after implementing control recommendations, e.g., "Low", "Medium", "High", "Very High")
        - likelihood: string (Estimate the likelihood based on the scale: "Rare", "Unlikely", "Possible", "Likely", "Certain")
        - impact_type: list of strings (Identify relevant impact types from: "Financial", "Legal", "Reputational", "Operational")
        Respond only with valid JSON.
        Incident:
        {incident_description}
        """

        # Use the chat completions endpoint
        response = openai.chat.completions.create(
            model="gpt-4o", # Using a recent model that supports JSON mode
            messages=[
                {"role": "system", "content": "You are an expert in operational risk classification. Provide output strictly as a JSON object."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"} # Request JSON output
        )

        # Extract the JSON string from the response
        json_output = response.choices[0].message.content

        # Parse and validate the JSON output using Pydantic
        classification_data = RiskClassification.model_validate_json(json_output)
        # Normalize to list if it's a string
        if isinstance(classification_data.control_recommendations, str):
            classification_data.control_recommendations = [
                line.strip("0123456789. ").strip()
                for line in classification_data.control_recommendations.splitlines()
                if line.strip()
            ]
        if isinstance(classification_data.control_recommendations, str):
            classification_data.control_recommendations = [
                rec.strip("0123456789. ").strip()
                for rec in classification_data.control_recommendations.splitlines()
                if rec.strip()
            ]
        # Perform framework classification
        framework_mappings = classify_across_frameworks(classification_data)
        classification_data.framework_tags = [f"{k}: {', '.join(v)}" for k, v in framework_mappings.items() if v] # Store as list of strings

        return classification_data

    except Exception as e:
        print(f"Error during classification: {e}")
        return None