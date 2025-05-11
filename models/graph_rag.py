"""
graph_rag.py

Graph-RAG(Retrieval Augmented Generation) 모듈
- Neo4j 지식 그래프를 활용한 문서 수정 및 업데이트
- 기존 그래프와의 일관성을 유지하며 내용 반영
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
import re

from .knowledge_graph_service import KnowledgeGraphService
from .llm_service import LLMService

class GraphRAG:
    """
    Neo4j 지식 그래프를 활용한 RAG(Retrieval Augmented Generation) 서비스
    
    기존 게임 데이터와 그래프를 바탕으로 내용 수정이나 추가 시 일관성을 유지합니다.
    LLM에 그래프의 컨텍스트를 제공하여 더 정확한 내용 생성 및 갱신을 지원합니다.
    """
    
    def __init__(self, kg_service: KnowledgeGraphService = None, llm_service: LLMService = None):
        """
        Graph-RAG 초기화
        
        Args:
            kg_service (KnowledgeGraphService, optional): 지식 그래프 서비스 인스턴스
            llm_service (LLMService, optional): LLM 서비스 인스턴스
        """
        self.kg = kg_service or KnowledgeGraphService()
        self.llm = llm_service or LLMService()
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def extract_relevant_knowledge(self, query: str, context_type: str = "general") -> Dict[str, Any]:
        """
        쿼리 관련 지식 그래프 정보 추출
        
        Args:
            query (str): 검색 쿼리 또는 문맥
            context_type (str, optional): 컨텍스트 유형 ("character", "location", "chapter", "general")
            
        Returns:
            Dict[str, Any]: 추출된 관련 정보
        """
        self.logger.info(f"Extracting relevant knowledge for query: {query[:50]}...")
        
        # 기본 응답 구조
        context = {
            "characters": [],
            "locations": [],
            "races": [],
            "chapters": [],
            "relationships": []
        }
        
        # 정규 표현식으로 주요 엔티티 추출
        character_names = self._extract_entities(query, "Character")
        location_names = self._extract_entities(query, "Location")
        race_names = self._extract_entities(query, "Race")
        chapter_references = self._extract_chapters(query)
        
        # 캐릭터 정보 수집
        if character_names or context_type == "character":
            character_details = []
            
            # 모든 캐릭터 기본 정보 가져오기
            if not character_names:
                characters = self.kg.get_characters()
                character_names = [char["name"] for char in characters if "name" in char]
            
            # 개별 캐릭터 정보 및 관계 수집
            for name in character_names:
                # 캐릭터 관계 가져오기
                relationships = self.kg.get_character_relationships(name)
                
                character_info = {
                    "name": name,
                    "relationships": relationships
                }
                character_details.append(character_info)
            
            context["characters"] = character_details
        
        # 장소 정보 수집
        if location_names or context_type == "location":
            # 모든 장소 정보 가져오기 (장소명이 없거나 "location" 컨텍스트인 경우)
            locations = self.kg.get_locations()
            
            if location_names:
                # 특정 장소만 필터링
                locations = [loc for loc in locations if loc.get("name") in location_names]
            
            context["locations"] = locations
        
        # 챕터 정보 수집
        if chapter_references or context_type == "chapter":
            chapter_details = []
            
            # 챕터 번호를 정수로 변환
            chapter_numbers = []
            for ref in chapter_references:
                try:
                    num = int(ref)
                    chapter_numbers.append(num)
                except ValueError:
                    continue
            
            # 지정된 챕터 정보 가져오기
            for num in chapter_numbers:
                chapter_info = self.kg.get_chapter_details(num)
                if chapter_info:
                    chapter_details.append(chapter_info)
            
            context["chapters"] = chapter_details
        
        self.logger.info(f"Extracted context with {len(context['characters'])} characters, " +
                        f"{len(context['locations'])} locations, " +
                        f"{len(context['chapters'])} chapters")
        
        return context
    
    def _extract_entities(self, text: str, entity_type: str) -> List[str]:
        """
        텍스트에서 엔티티 이름 추출
        
        Args:
            text (str): 분석할 텍스트
            entity_type (str): 엔티티 유형 ("Character", "Location", "Race")
            
        Returns:
            List[str]: 추출된 엔티티 이름 목록
        """
        # 간단한 구현: 대문자로 시작하는 단어를 엔티티로 간주
        # 실제 구현에서는 그래프에서 기존 엔티티 목록을 가져와 매칭하는 방식이 더 정확함
        words = re.findall(r'\b[A-Z][a-zA-Z]*\b', text)
        return list(set(words))
    
    def _extract_chapters(self, text: str) -> List[str]:
        """
        텍스트에서 챕터 참조 추출
        
        Args:
            text (str): 분석할 텍스트
            
        Returns:
            List[str]: 추출된 챕터 번호 또는 참조
        """
        # 챕터 숫자 찾기 (예: "챕터 1", "Chapter 2" 등)
        chapter_refs = re.findall(r'[Cc]hapter\s+(\d+)|[챕터]\s*(\d+)', text)
        
        # 결과 평탄화
        result = []
        for tup in chapter_refs:
            for num in tup:
                if num:
                    result.append(num)
        
        return list(set(result))
    
    def format_context_for_llm(self, context: Dict[str, Any]) -> str:
        """
        LLM 프롬프트에 적합한 형식으로 컨텍스트 포맷팅
        
        Args:
            context (Dict[str, Any]): 컨텍스트 정보
            
        Returns:
            str: LLM 프롬프트용 포맷된 컨텍스트 문자열
        """
        sections = []
        
        # 캐릭터 정보 포맷팅
        if context["characters"]:
            char_section = ["## 캐릭터 정보"]
            
            for char in context["characters"]:
                char_info = [f"### {char['name']}"]
                
                # 관계 정보 추가
                if char.get("relationships"):
                    relations = []
                    for rel in char["relationships"]:
                        rel_char = rel.get("related_character", "")
                        rel_type = rel.get("relationship_type", "")
                        
                        # Neo4j 관계 유형을 가독성 있는 텍스트로 변환
                        if rel_type == "TRUSTS":
                            rel_desc = "신뢰"
                        elif rel_type == "FRIENDLY_WITH":
                            rel_desc = "우호적"
                        elif rel_type == "NEUTRAL_WITH":
                            rel_desc = "중립"
                        elif rel_type == "HOSTILE_WITH":
                            rel_desc = "적대적"
                        elif rel_type == "HATES":
                            rel_desc = "증오"
                        else:
                            rel_desc = "관련됨"
                        
                        relations.append(f"- {rel_char}와(과)의 관계: {rel_desc}")
                    
                    if relations:
                        char_info.append("관계:")
                        char_info.extend(relations)
                
                char_section.append("\n".join(char_info))
            
            sections.append("\n\n".join(char_section))
        
        # 장소 정보 포맷팅
        if context["locations"]:
            loc_section = ["## 장소 정보"]
            
            for loc in context["locations"]:
                loc_info = [f"### {loc.get('name', '알 수 없는 장소')}"]
                
                # 서식 종족 정보 추가
                if loc.get("inhabited_by") and any(loc["inhabited_by"]):
                    races = ", ".join([r for r in loc["inhabited_by"] if r])
                    loc_info.append(f"서식 종족: {races}")
                
                loc_section.append("\n".join(loc_info))
            
            sections.append("\n\n".join(loc_section))
        
        # 챕터 정보 포맷팅
        if context["chapters"]:
            chap_section = ["## 챕터 정보"]
            
            for chap in context["chapters"]:
                chap_info = [f"### 챕터 {chap.get('order', '?')}: {chap.get('title', '제목 없음')}"]
                
                # 장소 정보 추가
                if chap.get("locations") and any(chap["locations"]):
                    locations = ", ".join([l for l in chap["locations"] if l])
                    chap_info.append(f"장소: {locations}")
                
                # 등장인물 정보 추가
                if chap.get("characters") and any(chap["characters"]):
                    chars = []
                    for c in chap["characters"]:
                        name = c.get("name", "")
                        race = c.get("race", "")
                        if name:
                            if race:
                                chars.append(f"{name} ({race})")
                            else:
                                chars.append(name)
                    
                    if chars:
                        chap_info.append(f"등장인물: {', '.join(chars)}")
                
                chap_section.append("\n".join(chap_info))
            
            sections.append("\n\n".join(chap_section))
        
        # 모든 섹션 결합
        if sections:
            return "\n\n".join(sections)
        else:
            return "관련 정보를 찾을 수 없습니다."
    
    def build_rag_prompt(self, original_content: str, update_request: str, context: Dict[str, Any]) -> str:
        """
        RAG 프롬프트 구성
        
        Args:
            original_content (str): 기존 문서 내용
            update_request (str): 업데이트 요청 내용
            context (Dict[str, Any]): 지식 그래프에서 추출한 컨텍스트
            
        Returns:
            str: LLM에 전달할 최종 프롬프트
        """
        # 컨텍스트 포맷팅
        formatted_context = self.format_context_for_llm(context)
        
        # 프롬프트 구성
        prompt_parts = [
            "아래 기존 문서를 제공된 요청에 따라 업데이트해주세요.",
            "업데이트 시 다음 제약 사항을 반드시 준수해주세요:",
            "1. 기존 게임 세계관 및 설정과 일관성을 유지할 것",
            "2. 캐릭터, 장소, 종족 간 기존 관계를 존중할 것",
            "3. 새로운 내용을 추가하는 경우, 기존 정보와 충돌하지 않도록 할 것",
            "4. 명시적으로 변경이 요청된 경우에만 기존 내용을 수정할 것",
            "5. 원본 문서의 형식과 구조를 유지할 것",
            "",
            "## 기존 문서 내용",
            original_content,
            "",
            "## 업데이트 요청",
            update_request,
            "",
            "## 관련 컨텍스트 정보 (지식 그래프에서 추출)",
            formatted_context,
            "",
            "위 정보를 바탕으로 업데이트된 완전한 문서를 생성해주세요."
        ]
        
        return "\n\n".join(prompt_parts)
    
    def update_from_document(
        self, 
        original_content: str, 
        update_request: str, 
        context_type: str = "general", 
        temperature: float = 0.3
    ) -> str:
        """
        지식 그래프를 활용하여 문서 업데이트
        
        Args:
            original_content (str): 기존 문서 내용
            update_request (str): 업데이트 요청 내용
            context_type (str, optional): 컨텍스트 유형
            temperature (float, optional): LLM 생성 온도
            
        Returns:
            str: 업데이트된 문서 내용
        """
        self.logger.info("Starting document update with Graph-RAG...")
        
        try:
            # 관련 컨텍스트 추출
            context = self.extract_relevant_knowledge(
                query=update_request + "\n" + original_content[:500],  # 요청과 문서 앞부분을 분석
                context_type=context_type
            )
            
            # RAG 프롬프트 구성
            prompt = self.build_rag_prompt(original_content, update_request, context)
            
            # LLM으로 업데이트된 문서 생성
            self.logger.info("Generating updated document with LLM...")
            updated_content = self.llm.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=4096  # 적절한 토큰 수 설정
            )
            
            self.logger.info("Document update completed successfully")
            return updated_content
            
        except Exception as e:
            self.logger.error(f"Error updating document: {e}")
            raise

    def extract_entities_from_document(self, document: str) -> Dict[str, List[str]]:
        """
        문서에서 엔티티(캐릭터, 장소, 종족 등) 추출
        
        Args:
            document (str): 분석할 문서 내용
            
        Returns:
            Dict[str, List[str]]: 추출된 엔티티 정보
                {
                    "characters": [...],
                    "locations": [...],
                    "races": [...],
                    "relationships": {character1: {character2: "friendly", ...}, ...}
                }
        """
        # LLM을 사용하여 엔티티 추출
        prompt = f"""
        다음 게임 문서에서 등장하는 모든 엔티티(캐릭터, 장소, 종족 등)와 그들 간의 관계를 추출해주세요.
        다음 JSON 형식으로 결과를 반환해주세요:
        
        {{
            "characters": ["캐릭터1", "캐릭터2", ...],
            "locations": ["장소1", "장소2", ...],
            "races": ["종족1", "종족2", ...],
            "relationships": {{
                "캐릭터1": {{
                    "캐릭터2": "신뢰|우호적|중립|적대적|증오",
                    ...
                }},
                ...
            }}
        }}
        
        문서 내용:
        {document[:10000]}  # 문서가 너무 길면 앞부분만 사용
        """
        
        try:
            # LLM으로 엔티티 추출
            self.logger.info("Extracting entities from document with LLM...")
            result = self.llm.generate(prompt=prompt, temperature=0.1)
            
            # JSON 파싱
            try:
                # JSON 부분만 추출
                json_match = re.search(r'\{[\s\S]*\}', result)
                if json_match:
                    result_json = json_match.group(0)
                    entities = json.loads(result_json)
                    return entities
                else:
                    self.logger.warning("JSON 형식을 찾을 수 없습니다.")
                    return {"characters": [], "locations": [], "races": [], "relationships": {}}
            except json.JSONDecodeError as e:
                self.logger.warning(f"JSON 파싱 오류: {e}")
                return {"characters": [], "locations": [], "races": [], "relationships": {}}
                
        except Exception as e:
            self.logger.error(f"엔티티 추출 오류: {e}")
            return {"characters": [], "locations": [], "races": [], "relationships": {}}
    
    def update_graph_from_document(self, document: str) -> Dict[str, Any]:
        """
        문서를 분석하여 지식 그래프 업데이트
        
        Args:
            document (str): 업데이트할 문서 내용
            
        Returns:
            Dict[str, Any]: 업데이트 결과 통계
                {
                    "added_characters": 추가된 캐릭터 수,
                    "added_locations": 추가된 장소 수,
                    "added_races": 추가된 종족 수,
                    "added_relationships": 추가된 관계 수
                }
        """
        stats = {
            "added_characters": 0,
            "added_locations": 0,
            "added_races": 0,
            "added_relationships": 0
        }
        
        try:
            # 문서에서 엔티티 추출
            entities = self.extract_entities_from_document(document)
            
            # 캐릭터 추가
            for character in entities.get("characters", []):
                try:
                    # Neo4j 트랜잭션으로 캐릭터 추가 (없으면)
                    with self.kg.driver.session() as session:
                        result = session.run(
                            """
                            MERGE (c:Character {name: $name})
                            RETURN count(c) as count
                            """,
                            name=character
                        )
                        count = result.single()["count"]
                        if count == 1:
                            stats["added_characters"] += 1
                except Exception as e:
                    self.logger.error(f"캐릭터 추가 오류 ({character}): {e}")
            
            # 장소 추가
            for location in entities.get("locations", []):
                try:
                    # Neo4j 트랜잭션으로 장소 추가 (없으면)
                    with self.kg.driver.session() as session:
                        result = session.run(
                            """
                            MERGE (l:Location {name: $name})
                            RETURN count(l) as count
                            """,
                            name=location
                        )
                        count = result.single()["count"]
                        if count == 1:
                            stats["added_locations"] += 1
                except Exception as e:
                    self.logger.error(f"장소 추가 오류 ({location}): {e}")
            
            # 종족 추가
            for race in entities.get("races", []):
                try:
                    # Neo4j 트랜잭션으로 종족 추가 (없으면)
                    with self.kg.driver.session() as session:
                        result = session.run(
                            """
                            MERGE (r:Race {name: $name})
                            RETURN count(r) as count
                            """,
                            name=race
                        )
                        count = result.single()["count"]
                        if count == 1:
                            stats["added_races"] += 1
                except Exception as e:
                    self.logger.error(f"종족 추가 오류 ({race}): {e}")
            
            # 관계 유형 매핑
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
            
            # 캐릭터 간 관계 추가
            for char1, relations in entities.get("relationships", {}).items():
                for char2, rel_type in relations.items():
                    try:
                        # 관계 유형 매핑
                        neo4j_rel_type = relationship_types.get(rel_type.lower(), "RELATED_TO")
                        
                        # Neo4j 트랜잭션으로 관계 추가 (없으면)
                        with self.kg.driver.session() as session:
                            result = session.run(
                                f"""
                                MATCH (c1:Character {{name: $char1}}), (c2:Character {{name: $char2}})
                                MERGE (c1)-[r:{neo4j_rel_type}]->(c2)
                                RETURN count(r) as count
                                """,
                                char1=char1,
                                char2=char2
                            )
                            count = result.single()["count"]
                            if count == 1:
                                stats["added_relationships"] += 1
                    except Exception as e:
                        self.logger.error(f"관계 추가 오류 ({char1}->{char2}): {e}")
            
            self.logger.info(f"그래프 업데이트 완료: {stats}")
            return stats
            
        except Exception as e:
            self.logger.error(f"그래프 업데이트 오류: {e}")
            raise
