"""
knowledge_graph_service.py

Neo4j 지식 그래프 변환 및 저장 모듈
- 생성된 GDD 및 스토리 내용을 Neo4j 지식 그래프로 변환
- 챕터, 장소, 캐릭터, 종족, 관계, 서식지 정보 저장
"""

import os
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv
from neo4j import GraphDatabase

class KnowledgeGraphService:
    """
    Neo4j 지식 그래프 서비스
    
    게임 디자인 문서(GDD)와 스토리라인 데이터를 Neo4j 그래프 데이터베이스에 저장하고 관리합니다.
    """
    
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        """
        Neo4j 연결 초기화
        
        Args:
            uri (str, optional): Neo4j 연결 URI
            user (str, optional): Neo4j 사용자명
            password (str, optional): Neo4j 비밀번호
            
        Raises:
            ValueError: 연결 정보가 없는 경우
        """
        # .env 파일에서 연결 정보 로드
        load_dotenv()
        load_uri = uri or os.getenv('NEO4J_URI')
        load_user = user or os.getenv('NEO4J_USER')
        load_pass = password or os.getenv('NEO4J_PASSWORD')
        
        if not all([load_uri, load_user, load_pass]):
            raise ValueError("Neo4j connection info missing in environment.")
        
        # Neo4j 드라이버 초기화
        self.driver = GraphDatabase.driver(load_uri, auth=(load_user, load_pass))
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Initialized Neo4j connection")
    
    def close(self):
        """Neo4j 연결 종료"""
        if self.driver:
            self.driver.close()
            self.logger.info("Closed Neo4j connection")
    
    def clear_graph(self):
        """
        그래프 데이터 전체 삭제
        
        특정 게임 데이터를 새로 생성할 때 사용
        """
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            self.logger.info("Cleared all graph data")
    
    def create_game_node(self, game_data: Dict[str, Any]) -> str:
        """
        게임 노드 생성
        
        Args:
            game_data (Dict[str, Any]): 게임 메타데이터
                
        Returns:
            str: 생성된 게임 노드 ID
        """
        with self.driver.session() as session:
            # Game 노드 생성
            result = session.run(
                """
                CREATE (g:Game {
                    title: $title,
                    genre: $genre,
                    target_audience: $target_audience,
                    concept: $concept
                })
                RETURN ID(g) AS node_id
                """,
                title=game_data.get("title", "Untitled Game"),
                genre=game_data.get("genre", ""),
                target_audience=game_data.get("target_audience", ""),
                concept=game_data.get("concept", "")
            )
            
            record = result.single()
            node_id = str(record["node_id"]) if record else None
            
            self.logger.info(f"Created Game node: {game_data.get('title', 'Untitled Game')}")
            return node_id

    def add_levels(self, game_id: str, levels: List[Dict[str, Any]]):
        """
        게임에 레벨 정보 추가
        
        Args:
            game_id (str): 게임 노드 ID
            levels (List[Dict[str, Any]]): 레벨 정보 리스트
        """
        try:
            with self.driver.session() as session:
                # 게임 노드 확인
                game_result = session.run(
                    "MATCH (g:Game) WHERE ID(g) = $node_id RETURN g", 
                    node_id=int(game_id)
                )
                
                game_node = game_result.single()
                if not game_node:
                    self.logger.error(f"Game node with ID {game_id} not found")
                    return
                
                # 레벨 노드 생성 및 게임과 연결
                for i, level in enumerate(levels):
                    # 레벨 노드 생성
                    level_result = session.run(
                        """
                        CREATE (l:Level {
                            name: $name,
                            order: $order,
                            theme: $theme,
                            atmosphere: $atmosphere
                        })
                        RETURN ID(l) AS node_id
                        """,
                        name=level.get("name", f"Level {i+1}"),
                        order=i+1,
                        theme=level.get("theme", ""),
                        atmosphere=level.get("atmosphere", "")
                    )
                    
                    level_node_id = level_result.single()["node_id"]
                    
                    # 게임과 레벨 연결
                    session.run(
                        """
                        MATCH (g:Game), (l:Level) 
                        WHERE ID(g) = $game_id AND ID(l) = $level_id
                        CREATE (g)-[:HAS_LEVEL]->(l)
                        """,
                        game_id=int(game_id),
                        level_id=level_node_id
                    )
                    
                    # 메커니즘 추가
                    if "mechanics" in level and level["mechanics"]:
                        for mechanic in level["mechanics"]:
                            # 메커니즘 노드 생성 또는 찾기
                            session.run(
                                """
                                MERGE (m:Mechanic {name: $name})
                                WITH m
                                MATCH (l:Level) WHERE ID(l) = $level_id
                                MERGE (l)-[:HAS_MECHANIC]->(m)
                                """,
                                name=mechanic,
                                level_id=level_node_id
                            )
                    
                    # 재미 요소 추가
                    if "fun_elements" in level and level["fun_elements"]:
                        for element in level["fun_elements"]:
                            # 재미 요소 노드 생성 또는 찾기
                            session.run(
                                """
                                MERGE (f:FunElement {description: $desc})
                                WITH f
                                MATCH (l:Level) WHERE ID(l) = $level_id
                                MERGE (l)-[:HAS_FUN_ELEMENT]->(f)
                                """,
                                desc=element,
                                level_id=level_node_id
                            )
                
                self.logger.info(f"Added {len(levels)} levels to game node {game_id}")
        except Exception as e:
            self.logger.error(f"Error adding levels to game: {e}")
            raise
    
    def create_chapters(self, chapters_data: List[Dict[str, Any]]):
        """
        챕터 노드 생성 및 관계 설정
        
        Args:
            chapters_data (List[Dict[str, Any]]): 챕터 정보 리스트
                [
                    {
                        "order": 챕터 순서,
                        "title": 챕터 제목,
                        "location": 장소,
                        "characters": 등장인물 리스트
                    },
                    ...
                ]
        """
        with self.driver.session() as session:
            # Game 노드 찾기
            game_result = session.run("MATCH (g:Game) RETURN g LIMIT 1")
            game_node = game_result.single()
            
            if not game_node:
                self.logger.error("Game node not found. Create game metadata first.")
                return
            
            # 챕터 노드 생성 및 Game과 연결
            for chapter in chapters_data:
                # 챕터 노드 생성
                chapter_result = session.run(
                    """
                    CREATE (c:Chapter {
                        order: $order,
                        title: $title
                    })
                    RETURN c
                    """,
                    order=chapter.get("order", 0),
                    title=chapter.get("title", f"Chapter {chapter.get('order', 0)}")
                )
                
                # Game과 Chapter 연결
                session.run(
                    """
                    MATCH (g:Game), (c:Chapter {order: $order})
                    CREATE (g)-[:HAS_CHAPTER]->(c)
                    """,
                    order=chapter.get("order", 0)
                )
                
                # 장소 노드 생성 및 연결
                location = chapter.get("location", "")
                if location:
                    # 여러 장소가 쉼표로 구분되어 있을 수 있음
                    locations = [loc.strip() for loc in location.split(',')]
                    
                    for loc in locations:
                        if not loc:
                            continue
                            
                        # 장소 노드 생성 (없으면)
                        session.run(
                            """
                            MERGE (l:Location {name: $name})
                            """,
                            name=loc
                        )
                        
                        # Chapter와 Location 연결
                        session.run(
                            """
                            MATCH (c:Chapter {order: $order}), (l:Location {name: $name})
                            MERGE (c)-[:TAKES_PLACE_IN]->(l)
                            """,
                            order=chapter.get("order", 0),
                            name=loc
                        )
                
                # 캐릭터 노드 생성 및 연결
                for character in chapter.get("characters", []):
                    if not character:
                        continue
                        
                    # 캐릭터 노드 생성 (없으면)
                    session.run(
                        """
                        MERGE (ch:Character {name: $name})
                        """,
                        name=character
                    )
                    
                    # Chapter와 Character 연결
                    session.run(
                        """
                        MATCH (c:Chapter {order: $order}), (ch:Character {name: $name})
                        MERGE (c)-[:FEATURES]->(ch)
                        """,
                        order=chapter.get("order", 0),
                        name=character
                    )
            
            self.logger.info(f"Created {len(chapters_data)} chapter nodes with locations and characters")
    
    def create_races(self, races_data: List[Dict[str, Any]]):
        """
        종족 노드 생성 및 관계 설정
        
        Args:
            races_data (List[Dict[str, Any]]): 종족 정보 리스트
                [
                    {
                        "name": 종족 이름,
                        "characters": 해당 종족 캐릭터 리스트,
                        "habitat": 종족 서식지
                    },
                    ...
                ]
        """
        with self.driver.session() as session:
            for race in races_data:
                # 종족 노드 생성
                session.run(
                    """
                    MERGE (r:Race {name: $name})
                    """,
                    name=race.get("name", "")
                )
                
                # 캐릭터와 종족 연결
                for character in race.get("characters", []):
                    session.run(
                        """
                        MATCH (ch:Character {name: $char_name}), (r:Race {name: $race_name})
                        MERGE (ch)-[:BELONGS_TO]->(r)
                        """,
                        char_name=character,
                        race_name=race.get("name", "")
                    )
                
                # 서식지(장소)와 종족 연결
                habitat = race.get("habitat", "")
                if habitat:
                    # 여러 서식지가 쉼표로 구분되어 있을 수 있음
                    habitats = [h.strip() for h in habitat.split(',')]
                    
                    for hab in habitats:
                        if not hab:
                            continue
                            
                        # 장소 노드 생성 (없으면)
                        session.run(
                            """
                            MERGE (l:Location {name: $name})
                            """,
                            name=hab
                        )
                        
                        # Race와 Location(서식지) 연결
                        session.run(
                            """
                            MATCH (r:Race {name: $race_name}), (l:Location {name: $loc_name})
                            MERGE (r)-[:INHABITS]->(l)
                            """,
                            race_name=race.get("name", ""),
                            loc_name=hab
                        )
            
            self.logger.info(f"Created {len(races_data)} race nodes with character relationships and habitats")
    
    def create_character_relationships(self, relationships_data: Dict[str, Dict[str, str]]):
        """
        캐릭터 간 관계 생성
        
        Args:
            relationships_data (Dict[str, Dict[str, str]]): 캐릭터 관계 정보
                {
                    "character1": {
                        "character2": "friendly",
                        "character3": "hostile",
                        ...
                    },
                    ...
                }
        """
        # 관계 타입 매핑
        relationship_types = {
            "신뢰": "TRUSTS",
            "우호적": "FRIENDLY_WITH",
            "중립": "NEUTRAL_WITH",
            "적대적": "HOSTILE_WITH",
            "증오": "HATES",
            "trust": "TRUSTS",
            "friendly": "FRIENDLY_WITH",
            "neutral": "NEUTRAL_WITH",
            "hostile": "HOSTILE_WITH",
            "hatred": "HATES"
        }
        
        with self.driver.session() as session:
            for char1, relations in relationships_data.items():
                for char2, rel_type in relations.items():
                    # 관계 타입 매핑
                    neo4j_rel_type = relationship_types.get(rel_type.lower(), "RELATED_TO")
                    
                    # 캐릭터 간 관계 생성
                    session.run(
                        f"""
                        MATCH (c1:Character {{name: $char1}}), (c2:Character {{name: $char2}})
                        MERGE (c1)-[:{neo4j_rel_type}]->(c2)
                        """,
                        char1=char1,
                        char2=char2
                    )
            
            self.logger.info("Created character relationship edges")
    
    def create_race_relationships(self, race_relations: Dict[str, Dict[str, str]]):
        """
        종족 간 관계 생성
        
        Args:
            race_relations (Dict[str, Dict[str, str]]): 종족 관계 정보
                {
                    "race1": {
                        "race2": "friendly",
                        "race3": "hostile",
                        ...
                    },
                    ...
                }
        """
        # 관계 타입 매핑
        relationship_types = {
            "신뢰": "TRUSTS",
            "우호적": "ALLIED_WITH",
            "중립": "NEUTRAL_WITH",
            "적대적": "HOSTILE_WITH",
            "증오": "AT_WAR_WITH",
            "trust": "TRUSTS",
            "friendly": "ALLIED_WITH",
            "neutral": "NEUTRAL_WITH",
            "hostile": "HOSTILE_WITH",
            "hatred": "AT_WAR_WITH"
        }
        
        with self.driver.session() as session:
            for race1, relations in race_relations.items():
                for race2, rel_type in relations.items():
                    # 관계 타입 매핑
                    neo4j_rel_type = relationship_types.get(rel_type.lower(), "RELATED_TO")
                    
                    # 종족 간 관계 생성
                    session.run(
                        f"""
                        MATCH (r1:Race {{name: $race1}}), (r2:Race {{name: $race2}})
                        MERGE (r1)-[:{neo4j_rel_type}]->(r2)
                        """,
                        race1=race1,
                        race2=race2
                    )
            
            self.logger.info("Created race relationship edges")
    
    def create_game_graph(self, game_data: Dict[str, Any], chapters_data: List[Dict[str, Any]]):
        """
        게임 그래프 전체 생성
        
        Args:
            game_data (Dict[str, Any]): 게임 메타데이터
            chapters_data (List[Dict[str, Any]]): 챕터별 데이터
        """
        try:
            # 새 그래프 생성 전 기존 데이터 삭제
            self.clear_graph()
            
            # 게임 메타데이터 노드 생성
            self.create_game_metadata(game_data)
            
            # 챕터 노드 및 관계 생성
            self.create_chapters(chapters_data)
            
            # 종족 정보가 있으면 생성
            races_data = game_data.get("races", [])
            if races_data:
                self.create_races(races_data)
            
            # 캐릭터 관계 정보가 있으면 생성
            character_relations = game_data.get("character_relationships", {})
            if character_relations:
                self.create_character_relationships(character_relations)
            
            # 종족 관계 정보가 있으면 생성
            race_relations = game_data.get("race_relationships", {})
            if race_relations:
                self.create_race_relationships(race_relations)
            
            self.logger.info("Successfully created complete game graph")
            
        except Exception as e:
            self.logger.error(f"Error creating game graph: {e}")
            raise
    
    def query_graph(self, query: str, params: Dict = None) -> List[Dict]:
        """
        Neo4j 그래프에 쿼리 실행
        
        Args:
            query (str): Cypher 쿼리
            params (Dict, optional): 쿼리 파라미터
            
        Returns:
            List[Dict]: 쿼리 결과
        """
        params = params or {}
        results = []
        
        with self.driver.session() as session:
            records = session.run(query, **params)
            for record in records:
                results.append(dict(record))
        
        return results
    
    def get_characters(self) -> List[Dict]:
        """
        모든 캐릭터 정보 조회
        
        Returns:
            List[Dict]: 캐릭터 정보 리스트
        """
        query = """
        MATCH (c:Character)
        OPTIONAL MATCH (c)-[:BELONGS_TO]->(r:Race)
        RETURN c.name AS name, r.name AS race
        ORDER BY c.name
        """
        
        return self.query_graph(query)
    
    def get_character_relationships(self, character_name: str) -> List[Dict]:
        """
        특정 캐릭터의 관계 정보 조회
        
        Args:
            character_name (str): 캐릭터 이름
            
        Returns:
            List[Dict]: 관계 정보 리스트
        """
        query = """
        MATCH (c:Character {name: $name})-[r]->(other:Character)
        RETURN other.name AS related_character, type(r) AS relationship_type
        ORDER BY relationship_type, related_character
        """
        
        return self.query_graph(query, {"name": character_name})
    
    def get_locations(self) -> List[Dict]:
        """
        모든 장소 정보 조회
        
        Returns:
            List[Dict]: 장소 정보 리스트
        """
        query = """
        MATCH (l:Location)
        OPTIONAL MATCH (r:Race)-[:INHABITS]->(l)
        RETURN l.name AS name, collect(r.name) AS inhabited_by
        ORDER BY l.name
        """
        
        return self.query_graph(query)
    
    def get_chapter_details(self, chapter_order: int) -> Dict:
        """
        특정 챕터의 상세 정보 조회
        
        Args:
            chapter_order (int): 챕터 순서
            
        Returns:
            Dict: 챕터 상세 정보
        """
        query = """
        MATCH (c:Chapter {order: $order})
        OPTIONAL MATCH (c)-[:TAKES_PLACE_IN]->(l:Location)
        OPTIONAL MATCH (c)-[:FEATURES]->(ch:Character)
        OPTIONAL MATCH (ch)-[:BELONGS_TO]->(r:Race)
        RETURN c.title AS title, 
               c.order AS order,
               collect(DISTINCT l.name) AS locations,
               collect(DISTINCT {name: ch.name, race: r.name}) AS characters
        """
        
        results = self.query_graph(query, {"order": chapter_order})
        return results[0] if results else {}
