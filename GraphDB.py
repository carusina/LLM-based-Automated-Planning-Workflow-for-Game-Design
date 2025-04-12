from neo4j import GraphDatabase, basic_auth
from neo4j.time import Date

class Neo4jConnection:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            "",
            auth=basic_auth("", ""))


    def close(self):
        if self.driver:
            self.driver.close()

    def query(self, query, title=None):
        with self.driver.session() as session:
            result = session.run(query, title)
            return result
        
    def get_node_datatype(self, value):
        if isinstance(value, str):
            return "STRING"
        elif isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "FLOAT"
        elif isinstance(value, bool):
            return "BOOLEAN"
        elif isinstance(value, list):
            return f"LIST[{self.get_node_datatype(value[0])}]" if value else "LIST"
        elif isinstance(value, Date):
            return "DATE"
        else:
            return "UNKNOWN"

    def get_schema(self):
        """
            Graph DB의 정보를 받아 노드 및 관계의 프로퍼티를 추출하고 스키마 딕셔너리를 반환하는 함수
        """
        with self.driver.session() as session:
            # 노드 프로퍼티 및 타입 추출
            node_query = """
            MATCH (n)
            WITH DISTINCT labels(n) AS node_labels, keys(n) AS property_keys, n
            UNWIND node_labels AS label
            UNWIND property_keys AS key
            RETURN label, key, n[key] AS sample_value
            """
            nodes = session.run(node_query)

            # 관계 프로퍼티 및 타입 추출
            rel_query = """
            MATCH ()-[r]->()
            WITH DISTINCT type(r) AS rel_type, keys(r) AS property_keys, r
            UNWIND property_keys AS key
            RETURN rel_type, key, r[key] AS sample_value
            """
            relationships = session.run(rel_query)

            # 관계 유형 및 방향 추출
            rel_direction_query = """
            MATCH (a)-[r]->(b)
            RETURN DISTINCT labels(a) AS start_label, type(r) AS rel_type, labels(b) AS end_label
            ORDER BY start_label, rel_type, end_label
            """
            rel_directions = session.run(rel_direction_query)

            # 스키마 딕셔너리 생성
            schema = {"nodes": {}, "relationships": {}, "relations": []}

            for record in nodes:
                label = record["label"]
                key = record["key"]
                sample_value = record["sample_value"] # 데이터 타입을 추론하기 위한 샘플 데이터
                inferred_type = self.get_node_datatype(sample_value)
                if label not in schema["nodes"]:
                    schema["nodes"][label] = {}
                schema["nodes"][label][key] = inferred_type

            for record in relationships:
                rel_type = record["rel_type"]
                key = record["key"]
                sample_value = record["sample_value"] # 데이터 타입을 추론하기 위한 샘플 데이터
                inferred_type = self.get_node_datatype(sample_value)
                if rel_type not in schema["relationships"]:
                    schema["relationships"][rel_type] = {}
                schema["relationships"][rel_type][key] = inferred_type

            for record in rel_directions:
                start_label = record["start_label"][0]
                rel_type = record["rel_type"]
                end_label = record["end_label"][0]
                schema["relations"].append(f"(:{start_label})-[:{rel_type}]->(:{end_label})")

            return schema

    def format_schema(self, schema):
        """
            스키마 딕셔너리를 LLM에 제공하기 위해 원하는 형태로 formatting 하는 함수
        """
        result = []

        # 노드 프로퍼티 출력
        result.append("Node properties:")
        for label, properties in schema["nodes"].items():
            props = ", ".join(f"{k}: {v}" for k, v in properties.items())
            result.append(f"{label} {{{props}}}")

        # 관계 프로퍼티 출력
        result.append("Relationship properties:")
        for rel_type, properties in schema["relationships"].items():
            props = ", ".join(f"{k}: {v}" for k, v in properties.items())
            result.append(f"{rel_type} {{{props}}}")

        # 관계 프로퍼티 출력
        result.append("The relationships:")
        for relation in schema["relations"]:
            result.append(relation)

        return "\n".join(result)  

    def schema_get(self):  
        schema = self.get_schema()
        return self.format_schema(schema)



