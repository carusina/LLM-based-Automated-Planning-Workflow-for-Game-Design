import json
import os
import asyncio
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.experimental.components.kg_writer import Neo4jWriter
from neo4j_graphrag.experimental.components.types import Neo4jGraph
from neo4j_graphrag.generation.prompts import ERExtractionTemplate
from neo4j_graphrag.generation import GraphRAG
from neo4j_graphrag.retrievers import Text2CypherRetriever
from GraphDB import Neo4jConnection
from Chat import ChatBot

os.environ["OPENAI_API_KEY"] = ""

llm = OpenAILLM(model_name="gpt-4o", model_params={"temperature": 0})

conn = Neo4jConnection()
chatbot = ChatBot()
prompt_template = ERExtractionTemplate()
# LLM INPUT / QUERY 예시 제공
examples = [
    "USER INPUT: '지금 기획 중인 게임이 뭐야??' QUERY: MATCH (n:Title) RETURN n",
    "USER INPUT: '이 title의 게임의 기획 내용을을 알려줘?' QUERY: MATCH (n {title: $title})-[r]-(m) RETURN n, r, m"
]

# Text2CypherRetriever
retriever = Text2CypherRetriever(
    driver= conn.driver,
    llm=llm,  # type: ignore
    neo4j_schema= conn.schema_get(),
    examples= examples,
)
# RAG 파이프라인 초기화
rag = GraphRAG(retriever=retriever, llm=llm)

# def fetch_graph_by_title(title):
#     result = conn.query("""
#         MATCH (n)-[r]-(m)
#         WHERE n.title = $title
#         RETURN n, r, m
#     """, title=title)

#     nodes, relationships = [], []
#     for record in result:
#         for node in [record["n"], record["m"]]:
#             if node.id not in [n.get("id") for n in nodes]:
#                 nodes.append({"id": node.id, "labels": list(node.labels), "properties": dict(node.items())})
#         rel = record["r"]
#         relationships.append({
#             "startNode": rel.start_node.id,
#             "endNode": rel.end_node.id,
#             "type": rel.type,
#             "properties": dict(rel.items())
#         })
#     return {"nodes": nodes, "relationships": relationships}

def intent_detection(message):
    prompt_text = f"""
    주어진 query_text 가 게임 기획을 하기 위한 본격적인 질문으로 보이면 True를 반환하고, 그렇지 않으면 False를 반환해줘.
    예시 : [("query_text": "안녕 반가워", "answer": "False"), ("query_text": "네가 게임 기획을 그렇게 잘한다며?", "answer": "False"), ("query_text": "게임 기획 방법에 대해 말해줘?", "answer": "False"), ("query_text": "이 세계관에 대해 게임을 기획해줘", "answer": "True")
    ("query_text": "이 기획을 이렇게 수정해줘", "answer": "True"), ("query_text": "이 기획을 더 확장해줘", "answer": "True")]
    query_text : {message}
    """
    return llm.invoke(prompt_text).content == 'True'

async def main():
    graph_history = ''
    graph_json = {"nodes": [], "relationships": []}  # 초기 그래프
    while True:
        user_input = input("\n사용자: ")

        if user_input == "완성":
            writer = Neo4jWriter(conn.driver)
            graph = Neo4jGraph(
                nodes=graph_json['nodes'],
                relationships=graph_json['relationships']
            )
            await writer.run(graph)
            break

        else:
            try:
                rag_prompt = "당신은 게임 기획을 해주는 한국어로 말하는 AI입니다."
                response = rag.search(user_input)
                ai_output = chatbot.ask(rag_prompt + response.answer + user_input)
                print("chatbot: " + ai_output)
            except Exception as e:
                response = chatbot.ask(user_input)
                ai_output = rag_prompt + response
                print("chatbot: " + ai_output)

            if(intent_detection(user_input) == True):
                prompt = prompt_template.format(
                    schema='',
                    text= ai_output + """\n(Continue extracting the graph based on the following input.
                    Keep existing nodes and relationships from graph history and only add new ones.\n
                    Graph History:\n""" + graph_history + ")",
                    examples=''
                )

                res = llm.invoke(prompt)
                print(res.content)

                graph_history = res.content
                graph_json = json.loads(graph_history[graph_history.find("{"):graph_history.rfind("}")+1])

if __name__ == "__main__":
    asyncio.run(main())