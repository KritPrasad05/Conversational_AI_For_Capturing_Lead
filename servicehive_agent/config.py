from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
import os


@dataclass(frozen=True)
class Settings:
    project_root: Path
    knowledge_base_path: Path
    vector_store_dir: Path
    faiss_index_path: Path
    faiss_meta_path: Path
    gemini_api_key: str | None
    chat_model: str = "gemini-2.5-flash"
    embedding_model: str = "gemini-embedding-001"
    chunk_size: int = 320
    chunk_overlap: int = 60
    top_k: int = 3

    @property
    def llm_enabled(self) -> bool:
        return bool(self.gemini_api_key)


def get_settings() -> Settings:
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")

    vector_store_dir = project_root / "servicehive_agent" / "data" / "vector_store"
    return Settings(
        project_root=project_root,
        knowledge_base_path=project_root / "servicehive_agent" / "data" / "knowledge_base.json",
        vector_store_dir=vector_store_dir,
        faiss_index_path=vector_store_dir / "servicehive.index",
        faiss_meta_path=vector_store_dir / "servicehive.index.json",
        gemini_api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
    )
