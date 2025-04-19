# Framework router

from src.models import RiskClassification
from .coso import map_to_coso
from .iso31000 import map_to_iso31000
from .sox import map_to_sox
from .gdpr import map_to_gdpr

def classify_across_frameworks(classification: RiskClassification) -> dict[str, list[str]]:
    """
    Classifies a RiskClassification across multiple frameworks.
    """
    framework_mappings = {}

    # Call each framework mapper
    framework_mappings["COSO"] = map_to_coso(classification)
    framework_mappings["ISO 31000"] = map_to_iso31000(classification)
    framework_mappings["SOX"] = map_to_sox(classification)
    framework_mappings["GDPR"] = map_to_gdpr(classification)

    return framework_mappings