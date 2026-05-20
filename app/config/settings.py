# from dotenv import load_dotenv
# from pydantic import BaseModel

# import os


# # Load values from the project's .env file into environment variables.
# # Environment variables keep deployment-specific values outside the code,
# # so the same codebase can run in development, testing, and production.
# load_dotenv()


# class Settings(BaseModel):
#     """Application settings loaded from environment variables."""

#     # Centralized settings management is important in enterprise apps because
#     # configuration becomes easier to audit, validate, reuse, and change safely.
#     APP_NAME: str = os.getenv("APP_NAME", "POC2")
#     APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
#     OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
#     QDRANT_URL: str = os.getenv("QDRANT_URL", "")
#     QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
#     QDRANT_COLLECTION_NAME: str = os.getenv(
#         "QDRANT_COLLECTION_NAME",
#         "servicenow_incidents",
#     )


# # A single shared settings object can be imported anywhere configuration is needed.
# settings = Settings()




from dotenv import load_dotenv
from pydantic import BaseModel

import os

load_dotenv()


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    APP_NAME: str = os.getenv("APP_NAME", "Similar Incidents AI")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.2.0")

    # LLM keys – both optional; the app falls back gracefully when absent.
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Qdrant – required for vector storage.
    QDRANT_URL: str = os.getenv("QDRANT_URL", "")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION_NAME: str = os.getenv(
        "QDRANT_COLLECTION_NAME",
        "servicenow_incidents",
    )

    # Controls which fields are returned in search / chat results.
    # Comma-separated list; remove a field name to exclude it from responses.
    RESULT_FIELDS: str = os.getenv(
        "RESULT_FIELDS",
        "number,short_description,description,assignment_group,"
        "priority,category,resolution_notes,servicenow_link,similarity_score",
    )

    @property
    def result_fields_set(self) -> set:
        return {f.strip() for f in self.RESULT_FIELDS.split(",") if f.strip()}


settings = Settings()