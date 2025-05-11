# test_neo4j.py
from models.knowledge_graph_service import KnowledgeGraphService

if __name__ == "__main__":
    kg = KnowledgeGraphService()
    print("✔ Neo4j 연결 OK")
    kg.close()
