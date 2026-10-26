from dataclasses import dataclass
from typing import Optional

@dataclass
class DataIngestionArtifact:
    train_file_path: str
    test_file_path: str