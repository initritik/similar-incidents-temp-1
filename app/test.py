from qdrant_client import QdrantClient

qdrant_client = QdrantClient(
    url="https://7c267e0a-78fc-4174-aacd-66c96d43f491.us-west-1-0.aws.cloud.qdrant.io:6333", 
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6ZTk2ZDllYmEtN2I1OS00YTA2LTkxMGYtMGZjMjM1YmRjZDIzIn0.AU6Dt-aTsseKqvGCMZS19JNSR3YO1WqJLpvnIPden20",
)

print(qdrant_client.get_collections())