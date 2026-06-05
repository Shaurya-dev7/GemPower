import json
from typing import Dict, List

class DatasetManager:
    def __init__(self, dataset_path: str = "backend/evaluation/test_dataset.json"):
        self.dataset_path = dataset_path
        
    def load_dataset(self) -> Dict[str, List[str]]:
        try:
            with open(self.dataset_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return {"normal": [], "edge_cases": [], "determinism_benchmarks": []}
