from pydantic import BaseModel
from typing import Optional, Union, Any

class RiskClassification(BaseModel):
    incident_description: Optional[str] = "" 
    basel_ii_category: str
    severity_score: int
    root_cause: str
    control_recommendations: Union[str, list[str]]
    framework_tags: list[str] = []
    inherent_risk: Optional[str] = None
    residual_risk: Optional[str] = None
    likelihood: Optional[str] = None
    impact_type: list[str] = []

    def model_post_init(self, _context: Any) -> None:
        if isinstance(self.control_recommendations, str):
            self.control_recommendations = [
                line.strip("0123456789. ").strip()
                for line in self.control_recommendations.splitlines()
                if line.strip()
            ]
