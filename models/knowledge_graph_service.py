import os
import re
import logging
import json
from typing import Dict, List, Any
from dotenv import load_dotenv
from neo4j import GraphDatabase

from .llm_service import LLMService

class KnowledgeGraphService:
    """
    GDD 기반 메타데이터 추출 및 Neo4j 지식 그래프 생성을 담당하는 서비스
    """
    
    def __init__(self, llm_service: LLMService, *, uri: str = None, user: str = None, password: str = None):
        load_dotenv()
        
        self.llm = llm_service

        load_uri = uri or os.getenv('NEO4J_URI')
        load_user = user or os.getenv('NEO4J_USER')
        load_pass = password or os.getenv('NEO4J_PASSWORD')

        self.driver = None
        if all([load_uri, load_user, load_pass]):
            self.driver = GraphDatabase.driver(load_uri, auth=(load_user, load_pass))
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        if self.driver:
            self.logger.info("Initialized Neo4j connection")
        else:
            self.logger.warning("Neo4j connection info missing, proceeding without Neo4j.")

    def close(self):
        """Neo4j 연결 종료"""
        if self.driver:
            self.driver.close()
            self.logger.info("Closed Neo4j connection")

    def extract_metadata_from_gdd(self, gdd_text: str) -> Dict[str, Any]:
        """LLM을 사용하여 GDD 텍스트에서 구조화된 메타데이터를 추출합니다."""
        prompt = f"""        당신은 게임 기획 문서(GDD)를 분석하여 구조화된 데이터만 추출하는 전문 내러티브 분석가입니다.
        다음 GDD 텍스트를 읽고, 아래에 명시된 JSON 형식에 맞춰 핵심 메타데이터를 '추론'하고 '추출'해주세요.
        GDD에 명시적으로 드러나지 않은 내용(예: 인물 간의 관계, 암시적 그룹)은 GDD 내용을 바탕으로 논리적으로 추론하여 채워주세요.
        추가적인 설명이나 인사말 없이, 오직 JSON 객체만 응답으로 반환해야 합니다.
        모든 키와 문자열 값에 반드시 큰따옴표(")를 사용하고, 마지막 요소 뒤에 쉼표(trailing comma)를 사용하지 마세요.

        **추출할 JSON 형식:**
        {{
            "game_title": "게임의 공식적인 제목",
            "narrative_overview": {{
                "synopsis": "게임의 전체적인 줄거리 요약",
                "world_lore": "게임 세계관에 대한 핵심 설명"
            }},
            "levels": [
                {{
                    "name": "레벨 이름",
                    "description": "레벨에 대한 설명",
                    "theme": "레벨의 주요 테마",
                    "atmosphere": "레벨의 전체적인 분위기"
                }}
            ],
            "characters": [
                {{
                    "name": "캐릭터 이름",
                    "description": "캐릭터 외형 및 성격 묘사",
                    "goal": "캐릭터의 궁극적인 목표 또는 동기"
                }}
            ],
            "character_relationships": [
                {{
                    "source": "캐릭터 A",
                    "target": "캐릭터 B",
                    "type": "관계를 나타내는 서술어 (예: 돕는다, 조언한다, 방해한다)"
                }}
            ],
            "implicit_groups": [
                {{
                    "group_name": "그룹의 성격 (예: 주인공 그룹, 적대 그룹)",
                    "members": ["캐릭터 이름1", "캐릭터 이름2"]
                }}
            ],
            "key_items": [
                {{
                    "name": "핵심 아이템 이름",
                    "description": "아이템의 역할이나 중요성에 대한 설명",
                    "estimated_location": "아이템을 발견할 수 있는 추정 장소"
                }}
            ]
        }}

        --- GDD 텍스트 시작 ---
        {gdd_text}
        --- GDD 텍스트 끝 ---

        위 GDD 텍스트를 분석하여 JSON 객체를 생성해주세요.
        """
        self.logger.info("LLM에게 GDD 메타데이터 추출 요청...")
        try:
            response_text = self.llm.generate(prompt, temperature=0.2, max_tokens=4096)
            match = re.search(r'```json\s*([\s\S]+?)\s*```', response_text)
            if match:
                json_string = match.group(1)
            else:
                json_match = re.search(r'{{\s*[\s\S]*\s*}}', response_text)
                if json_match:
                    json_string = json_match.group(0)
                else:
                    self.logger.error("LLM 응답에서 JSON 객체를 찾을 수 없습니다.")
                    return {{}}
            metadata = json.loads(json_string)
            self.logger.info("GDD 메타데이터를 성공적으로 추출했습니다.")
            return metadata
            return {}
        except json.JSONDecodeError as e:
            self.logger.error(f"LLM 응답에서 JSON을 파싱하는 중 오류가 발생했습니다: {e}")
            self.logger.debug(f"파싱 실패 텍스트: {response_text}")
            return {}
        except Exception as e:
            self.logger.error(f"메타데이터 추출 중 예기치 않은 오류가 발생했습니다: {e}")
            return {}

    def create_graph_from_metadata(self, metadata: Dict[str, Any]):
        """
        추출된 메타데이터를 기반으로 Neo4j 지식 그래프를 생성합니다. (재작성된 안정화 버전)
        """
        if not self.driver:
            self.logger.warning("Neo4j driver not initialized. Skipping graph creation.")
            return

        def _create_graph_tx(tx, metadata):
            # 1. 기존 데이터 삭제
            self.logger.info("Initializing graph: Clearing all existing data...")
            tx.run("MATCH (n) DETACH DELETE n")

            # --- Helper for de-duplication ---
            def get_unique_nodes(items, key_name):
                seen = set()
                unique = []
                for item in items:
                    if isinstance(item, dict) and (key_val := item.get(key_name)) and key_val not in seen:
                        seen.add(key_val)
                        unique.append(item)
                return unique

            # 2. 모든 노드 데이터 준비 (중복 제거)
            self.logger.info("Preparing nodes...")
            characters = get_unique_nodes(metadata.get("characters", []), "name")
            levels = get_unique_nodes(metadata.get("levels", []), "name")
            key_items = get_unique_nodes(metadata.get("key_items", []), "name")
            implicit_groups = get_unique_nodes(metadata.get("implicit_groups", []), "group_name")
            
            # 존재하는 노드 이름만 세트로 저장 (관계 생성 시 무결성 체크용)
            character_names = {c['name'] for c in characters}
            level_names = {lvl['name'] for lvl in levels}

            # 3. 모든 노드 생성
            tx.run(
                """CREATE (g:Game {title: $game_title, synopsis: $synopsis, world_lore: $world_lore})""",
                game_title=metadata.get("game_title", "Untitled Game"),
                synopsis=metadata.get("narrative_overview", {}).get("synopsis", ""),
                world_lore=metadata.get("narrative_overview", {}).get("world_lore", "")
            )
            self.logger.info("- Created Game node.")

            if characters:
                tx.run("UNWIND $props AS p MERGE (c:Character {name: p.name}) SET c += p", props=characters)
                self.logger.info(f"- Created or merged {len(characters)} Character nodes.")
            if levels:
                tx.run("UNWIND $props AS p MERGE (l:Level {name: p.name}) SET l += p", props=levels)
                self.logger.info(f"- Created or merged {len(levels)} Level nodes.")
            if key_items:
                tx.run("UNWIND $props AS p MERGE (i:KeyItem {name: p.name}) SET i += p", props=key_items)
                self.logger.info(f"- Created or merged {len(key_items)} KeyItem nodes.")
            if implicit_groups:
                tx.run("UNWIND $props AS p MERGE (g:Group {name: p.group_name})", props=implicit_groups)
                self.logger.info(f"- Created or merged {len(implicit_groups)} Group nodes.")

            # 4. 모든 관계 데이터 준비 (중복 및 무결성 체크)
            self.logger.info("Preparing relationships...")
            
            # 그룹 멤버 관계
            valid_memberships = []
            for group in implicit_groups:
                if group_name := group.get("group_name"):
                    for member_name in group.get("members", []):
                        if member_name in character_names: # 무결성 체크
                            valid_memberships.append({"group_name": group_name, "member_name": member_name})
            
            # 캐릭터 상호작용 관계
            valid_char_rels = []
            seen_char_rels = set()
            for rel in metadata.get("character_relationships", []):
                source, target, rel_type = rel.get("source"), rel.get("target"), rel.get("type")
                if source in character_names and target in character_names and rel_type:
                    rel_tuple = (source, target, rel_type)
                    if rel_tuple not in seen_char_rels: # 중복 체크
                        seen_char_rels.add(rel_tuple)
                        valid_char_rels.append(rel)

            # 아이템 위치 관계
            valid_item_locs = []
            for item in key_items:
                loc = item.get("estimated_location")
                if item.get("name") and loc and loc in level_names: # 무결성 체크
                    valid_item_locs.append({"item_name": item["name"], "location_name": loc})

            # 5. 모든 관계 생성
            tx.run("MATCH (g:Game), (c:Character) MERGE (g)-[:HAS_CHARACTER]->(c)")
            tx.run("MATCH (g:Game), (l:Level) MERGE (g)-[:HAS_LEVEL]->(l)")
            tx.run("MATCH (g:Game), (i:KeyItem) MERGE (g)-[:HAS_KEY_ITEM]->(i)")
            tx.run("MATCH (g:Game), (grp:Group) MERGE (g)-[:HAS_GROUP]->(grp)")
            self.logger.info("- Created basic Game relationships.")

            if valid_memberships:
                tx.run("""
                UNWIND $props AS p
                MATCH (g:Group {name: p.group_name})
                MATCH (c:Character {name: p.member_name})
                MERGE (c)-[:MEMBER_OF]->(g)
                """, props=valid_memberships)
                self.logger.info(f"- Created {len(valid_memberships)} MEMBER_OF relationships.")

            if valid_char_rels:
                tx.run("""
                UNWIND $rels AS rel
                MATCH (a:Character {name: rel.source})
                MATCH (b:Character {name: rel.target})
                MERGE (a)-[r:INTERACTS_WITH]->(b)
                SET r.type = rel.type
                """, rels=valid_char_rels)
                self.logger.info(f"- Created {len(valid_char_rels)} INTERACTS_WITH relationships.")

            if valid_item_locs:
                tx.run("""
                UNWIND $props AS p
                MATCH (i:KeyItem {name: p.item_name})
                MATCH (l:Level {name: p.location_name})
                MERGE (i)-[:LOCATED_IN]->(l)
                """, props=valid_item_locs)
                self.logger.info(f"- Created {len(valid_item_locs)} LOCATED_IN relationships.")

        try:
            with self.driver.session() as session:
                session.write_transaction(_create_graph_tx, metadata)
                self.logger.info("✅ Knowledge graph transaction completed successfully.")
        except Exception as e:
            self.logger.error(f"A failure occurred during the graph creation transaction: {e}", exc_info=True)
            raise