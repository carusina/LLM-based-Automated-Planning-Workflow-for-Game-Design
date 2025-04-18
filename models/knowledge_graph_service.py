# models/knowledge_graph_service.py
import os
import json
from neo4j import GraphDatabase
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# Neo4j 연결 정보
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

class KnowledgeGraphService:
    """Neo4j 그래프 데이터베이스와 상호작용하는 서비스 클래스"""
    
    def __init__(self, uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD):
        """Neo4j 데이터베이스에 연결합니다."""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        """데이터베이스 연결을 종료합니다."""
        self.driver.close()
    
    def run_query(self, query, parameters=None):
        """Cypher 쿼리를 실행합니다."""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return list(result)
    
    def get_graph_overview(self):
        """현재 그래프 데이터베이스의 개요 정보를 반환합니다."""
        try:
            # 게임 정보 조회
            game_query = """
            MATCH (g:Game) 
            RETURN g.title AS title
            """
            games = self.run_query(game_query)
            
            # 챕터 정보 조회
            chapter_query = """
            MATCH (g:Game)-[:HAS_CHAPTER]->(c:Chapter)
            RETURN g.title AS game, c.number AS number, c.title AS title, c.description AS description
            ORDER BY c.number
            """
            chapters = self.run_query(chapter_query)
            
            # 캐릭터 정보 조회
            character_query = """
            MATCH (g:Game)-[:HAS_CHARACTER]->(c:Character)
            RETURN g.title AS game, c.name AS name, c.role AS role, c.background AS background
            """
            characters = self.run_query(character_query)
            
            # 위치 정보 조회
            location_query = """
            MATCH (g:Game)-[:HAS_CHAPTER]->(ch:Chapter)-[:TAKES_PLACE_AT]->(l:Location)
            RETURN g.title AS game, ch.number AS chapter, l.name AS name, l.type AS type
            """
            locations = self.run_query(location_query)
            
            # 사건 정보 조회
            event_query = """
            MATCH (g:Game)-[:HAS_CHAPTER]->(ch:Chapter)-[:CONTAINS_EVENT]->(e:Event)
            RETURN g.title AS game, ch.number AS chapter, e.name AS name, e.description AS description
            """
            events = self.run_query(event_query)
            
            # 결과 구성
            result = {
                "games": [{"title": game["title"]} for game in games],
                "chapters": [
                    {
                        "game": chapter["game"],
                        "number": chapter["number"],
                        "title": chapter["title"],
                        "description": chapter["description"]
                    } for chapter in chapters
                ],
                "characters": [
                    {
                        "game": character["game"],
                        "name": character["name"],
                        "role": character["role"],
                        "background": character["background"]
                    } for character in characters
                ],
                "locations": [
                    {
                        "game": location["game"],
                        "chapter": location["chapter"],
                        "name": location["name"],
                        "type": location["type"]
                    } for location in locations
                ],
                "events": [
                    {
                        "game": event["game"],
                        "chapter": event["chapter"],
                        "name": event["name"],
                        "description": event["description"]
                    } for event in events
                ]
            }
            
            return result
        except Exception as e:
            print(f"그래프 데이터베이스 조회 중 오류: {str(e)}")
            return {"error": str(e)}
    
    def delete_chapter(self, filename, chapter_number):
        """해당 챕터 관련 노드를 삭제합니다."""
        try:
            # 파일명에서 게임 제목 추출
            game_title = os.path.splitext(os.path.basename(filename))[0]
            if '_' in game_title:
                game_title = ' '.join(word.capitalize() for word in game_title.split('_'))
            
            # 챕터 번호로 노드 찾기
            query = """
            MATCH (g:Game {title: $game_title})-[:HAS_CHAPTER]->(c:Chapter {number: $chapter_number})
            OPTIONAL MATCH (c)-[r1]->(n1)
            OPTIONAL MATCH (n1)-[r2]->(n2)
            DELETE r1, r2, n1, n2, c
            """
            self.run_query(query, {"game_title": game_title, "chapter_number": chapter_number})
            
            print(f"챕터 {chapter_number} 삭제 완료")
            return True
        
        except Exception as e:
            print(f"챕터 삭제 중 오류 발생: {str(e)}")
            return False
    
    def get_related_elements(self, game_title, chapter_number=None, element_type=None):
        """게임 혹은 특정 챕터에 관련된 요소들을 검색합니다."""
        try:
            if chapter_number and element_type:
                # 특정 챕터, 특정 유형의 요소 검색
                if element_type.lower() == "character":
                    query = """
                    MATCH (g:Game {title: $game_title})-[:HAS_CHARACTER]->(c:Character)
                    RETURN c.name AS name, c.role AS role, c.background AS background
                    """
                    results = self.run_query(query, {"game_title": game_title})
                    
                elif element_type.lower() == "location":
                    query = """
                    MATCH (g:Game {title: $game_title})-[:HAS_CHAPTER]->(ch:Chapter {number: $chapter_number})
                    -[:TAKES_PLACE_AT]->(l:Location)
                    RETURN l.name AS name, l.type AS type
                    """
                    results = self.run_query(query, {"game_title": game_title, "chapter_number": chapter_number})
                    
                elif element_type.lower() == "event":
                    query = """
                    MATCH (g:Game {title: $game_title})-[:HAS_CHAPTER]->(ch:Chapter {number: $chapter_number})
                    -[:CONTAINS_EVENT]->(e:Event)
                    RETURN e.name AS name, e.description AS description
                    """
                    results = self.run_query(query, {"game_title": game_title, "chapter_number": chapter_number})
                
                else:
                    results = []
            
            elif chapter_number:
                # 특정 챕터의 모든 요소 검색
                query = """
                MATCH (g:Game {title: $game_title})-[:HAS_CHAPTER]->(ch:Chapter {number: $chapter_number})
                OPTIONAL MATCH (ch)-[:TAKES_PLACE_AT]->(l:Location)
                OPTIONAL MATCH (ch)-[:CONTAINS_EVENT]->(e:Event)
                OPTIONAL MATCH (ch)-[:HAS_GOAL]->(goal:Goal)
                OPTIONAL MATCH (ch)-[:PRESENTS_CHALLENGE]->(challenge:Challenge)
                RETURN
                    ch.title AS chapter_title,
                    ch.description AS chapter_description,
                    collect(distinct l.name) AS locations,
                    collect(distinct e.name) AS events,
                    collect(distinct goal.description) AS goals,
                    collect(distinct challenge.name) AS challenges
                """
                results = self.run_query(query, {"game_title": game_title, "chapter_number": chapter_number})
            
            else:
                # 게임 전체 요소 검색
                query = """
                MATCH (g:Game {title: $game_title})-[:HAS_CHAPTER]->(ch:Chapter)
                RETURN ch.number AS chapter_number, ch.title AS chapter_title
                ORDER BY ch.number
                """
                chapters = self.run_query(query, {"game_title": game_title})
                
                query = """
                MATCH (g:Game {title: $game_title})-[:HAS_CHARACTER]->(c:Character)
                RETURN c.name AS name, c.role AS role
                """
                characters = self.run_query(query, {"game_title": game_title})
                
                results = {"chapters": chapters, "characters": characters}
            
            return results
        
        except Exception as e:
            print(f"관련 요소 검색 중 오류 발생: {str(e)}")
            return []
    
    def get_chapter_neighbors(self, game_title, chapter_number):
        """특정 챕터의 이전/다음 챕터를 가져옵니다."""
        try:
            # 이전 챕터 조회
            prev_query = """
            MATCH (g:Game {title: $game_title})-[:HAS_CHAPTER]->(c1:Chapter)-[:FOLLOWED_BY]->(c2:Chapter {number: $chapter_number})
            RETURN c1.number AS number, c1.title AS title
            """
            prev_chapters = self.run_query(prev_query, {"game_title": game_title, "chapter_number": chapter_number})
            
            # 다음 챕터 조회
            next_query = """
            MATCH (g:Game {title: $game_title})-[:HAS_CHAPTER]->(c1:Chapter {number: $chapter_number})-[:FOLLOWED_BY]->(c2:Chapter)
            RETURN c2.number AS number, c2.title AS title
            """
            next_chapters = self.run_query(next_query, {"game_title": game_title, "chapter_number": chapter_number})
            
            return {
                "previous": [{"number": chapter["number"], "title": chapter["title"]} for chapter in prev_chapters],
                "next": [{"number": chapter["number"], "title": chapter["title"]} for chapter in next_chapters]
            }
        
        except Exception as e:
            print(f"이웃 챕터 검색 중 오류 발생: {str(e)}")
            return {"previous": [], "next": []}