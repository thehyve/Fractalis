from enum import Enum
from typing import Dict
from pydantic import BaseModel


class Handler(Enum):
    """
    Etl handler name
    """
    TRANSMART = "transmart"
    ADA = "ada"
    PICSURE = "pic-sure"

    DEMO_TCGA_COAD = "demo_tcga_coad"
    DEMO_WINE_QUALITY = "demo_wine_quality"
    TEST = "test"


class DataService(BaseModel):
    handler: Handler
    server: str


class DataServices(BaseModel):
    data_services: Dict[str, DataService]
