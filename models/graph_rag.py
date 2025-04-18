# models/graph_rag.py
from typing import Dict, List, Any, Optional
import re
import json

class GraphRAG:
    """그래프 기반 검색 증강 생성(Graph Retrieval-Augmented Generation) 클래스"""
    
    def __init__(self, llm_service, knowledge_graph_service):
        """
        GraphRAG 초기화
        
        Args:
            llm_service: LLM 서비스 인스턴스
            knowledge_graph_service: Neo4j 지식 그래프 서비스 인스턴스
        """
        self.llm_service = llm_service
        self.kg_service = knowledge_graph_service
    
    def generate_chapter_content(self, game_title, chapter_number, chapter_title="", guideline="", include_details=True):
        """
        챕터 내용을 생성합니다.
        
        Args:
            game_title: 게임 제목
            chapter_number: 챕터 번호
            chapter_title: 챕터 제목 (없으면 빈 문자열)
            guideline: 사용자가 입력한 가이드라인
            include_details: 챕터 상세 내용 포함 여부 (기본값: True)
            
        Returns:
            생성된 챕터 내용
        """
        # 1. 지식 그래프에서 관련 정보 검색
        neighbors = self.kg_service.get_chapter_neighbors(game_title, chapter_number)
        related_elements = self.kg_service.get_related_elements(game_title, None, None)
        
        # 게임 전체 정보 추출
        game_overview = {
            "title": game_title,
            "chapters": [],
            "characters": []
        }
        
        # 챕터 정보 수집
        if "chapters" in related_elements:
            for chapter in related_elements["chapters"]:
                game_overview["chapters"].append({
                    "number": chapter["chapter_number"],
                    "title": chapter["chapter_title"]
                })
        
        # 캐릭터 정보 수집
        if "characters" in related_elements:
            for character in related_elements["characters"]:
                game_overview["characters"].append({
                    "name": character["name"],
                    "role": character["role"]
                })
        
        # 이전 챕터와 다음 챕터 정보
        previous_chapters = neighbors.get("previous", [])
        next_chapters = neighbors.get("next", [])
        
        # 이전/다음 챕터가 있다면 해당 챕터의 세부 정보 가져오기
        prev_chapter_details = None
        if previous_chapters:
            prev_number = previous_chapters[0]["number"]
            prev_details = self.kg_service.get_related_elements(game_title, prev_number)
            if prev_details and len(prev_details) > 0:
                prev_chapter_details = prev_details[0]
        
        # 2. 챕터 내용 생성을 위한 프롬프트 구성
        if not chapter_title and game_overview["chapters"]:
            # 챕터 제목이 제공되지 않으면 기존 챕터 제목 찾기
            for chapter in game_overview["chapters"]:
                if chapter["number"] == chapter_number:
                    chapter_title = chapter["title"]
                    break
        
        # 만약 여전히 제목이 없으면 기본값 사용
        if not chapter_title:
            chapter_title = f"챕터 {chapter_number}"
        
        # 프롬프트 구성
        prompt = f"""게임 제목: {game_title}

        ## 작업 설명
        챕터 {chapter_number}: "{chapter_title}"에 대한 상세 내용을 생성해야 합니다.
        
        ## 게임 개요
        - 제목: {game_title}
        """
        
        # 챕터 구조 추가
        prompt += "\n## 챕터 구조\n"
        for chapter in sorted(game_overview["chapters"], key=lambda x: x["number"]):
            prompt += f"- 챕터 {chapter['number']}: {chapter['title']}\n"
        
        # 캐릭터 정보 추가
        if game_overview["characters"]:
            prompt += "\n## 주요 캐릭터\n"
            for character in game_overview["characters"]:
                prompt += f"- {character['name']} ({character['role']})\n"
        
        # 연속성을 위한 이전 챕터 정보 추가
        if prev_chapter_details:
            prompt += f"\n## 이전 챕터 ({previous_chapters[0]['number']}: {previous_chapters[0]['title']}) 요약\n"
            prompt += f"제목: {prev_chapter_details.get('chapter_title', '')}\n"
            prompt += f"설명: {prev_chapter_details.get('chapter_description', '')}\n"
            
            if prev_chapter_details.get('events'):
                prompt += "주요 사건:\n"
                for event in prev_chapter_details.get('events', []):
                    if event:
                        prompt += f"- {event}\n"
            
            if prev_chapter_details.get('locations'):
                prompt += "위치:\n"
                for location in prev_chapter_details.get('locations', []):
                    if location:
                        prompt += f"- {location}\n"
        
        # 사용자 가이드라인 추가
        if guideline:
            prompt += f"\n## 사용자 가이드라인\n{guideline}\n"
        
        # 출력 스키마 정의 (챕터 개요)
        chapter_outline_schema = {
            "chapter_number": chapter_number,
            "title": chapter_title,
            "synopsis": "챕터 개요",
            "goals": ["플레이어 목표 1", "플레이어 목표 2"],
            "key_locations": ["주요 위치 1", "주요 위치 2"],
            "key_events": ["주요 사건 1", "주요 사건 2"],
            "challenges": ["도전 1", "도전 2"]
        }
        
        # 출력 스키마 정의 (챕터 상세 내용)
        chapter_details_schema = {
            "chapter_number": chapter_number,
            "title": chapter_title,
            "detailed_synopsis": "상세 시놉시스",
            "opening_scene": "오프닝 씬 설명",
            "key_events": [
                {
                    "event_title": "이벤트 제목",
                    "description": "이벤트 설명",
                    "player_involvement": "플레이어 관여 방식",
                    "gameplay_mechanics": ["관련 게임플레이 메커닉 1", "관련 게임플레이 메커닉 2"],
                    "outcomes": ["가능한 결과 1", "가능한 결과 2"]
                }
            ],
            "characters": [
                {
                    "name": "캐릭터 이름",
                    "role": "이 챕터에서의 역할",
                    "interactions": "플레이어와의 상호작용",
                    "development": "캐릭터 발전/변화"
                }
            ],
            "locations": [
                {
                    "name": "장소 이름",
                    "description": "장소 설명",
                    "significance": "스토리에서의 중요성",
                    "gameplay_elements": ["게임플레이 요소 1", "게임플레이 요소 2"]
                }
            ],
            "challenges": [
                {
                    "challenge_type": "도전 유형 (전투, 퍼즐, 선택 등)",
                    "description": "도전 설명",
                    "difficulty": "난이도",
                    "rewards": ["보상 1", "보상 2"]
                }
            ],
            "choices_and_consequences": [
                {
                    "choice_point": "선택 지점",
                    "options": ["선택지 1", "선택지 2"],
                    "consequences": ["결과 1", "결과 2"]
                }
            ],
            "climax": "챕터 클라이맥스 설명",
            "ending": "챕터 엔딩 설명",
            "connection_to_next_chapter": "다음 챕터와의 연결",
            "key_items": ["주요 아이템 1", "주요 아이템 2"],
            "secrets": ["숨겨진 비밀/이스터에그 1", "숨겨진 비밀/이스터에그 2"]
        }
        
        # 생성 요청 추가
        prompt += """
        ## 요청
        사용자 가이드라인을 필수적으로 반영해주세요.
        """
        
        # 3. LLM으로 내용 생성
        try:
            if not include_details:
                # 챕터 개요만 생성
                return self.llm_service.generate_structured_output(
                    prompt=prompt,
                    output_schema=chapter_outline_schema,
                    provider="openai",
                    temperature=0.7
                )
            else:
                # 챕터 상세 내용 생성
                return self.llm_service.generate_structured_output(
                    prompt=prompt,
                    output_schema=chapter_details_schema,
                    provider="openai",
                    temperature=0.7
                )
            
        except Exception as e:
            print(f"챕터 내용 생성 중 오류 발생: {str(e)}")
            return {"error": f"내용 생성 중 오류가 발생했습니다: {str(e)}"}

    def generate_complete_chapter(self, game_title, chapter_number, chapter_title="", guideline=""):
        """
        챕터의 개요와 상세 내용을 모두 생성합니다.
        
        Args:
            game_title: 게임 제목
            chapter_number: 챕터 번호
            chapter_title: 챕터 제목 (없으면 빈 문자열)
            guideline: 사용자가 입력한 가이드라인
            
        Returns:
            개요와 상세 내용을 포함한 딕셔너리
        """
        # 챕터 개요 생성
        chapter_outline = self.generate_chapter_content(
            game_title=game_title,
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            guideline=guideline,
            include_details=False
        )
        
        # 챕터 상세 내용 생성
        chapter_details = self.generate_chapter_content(
            game_title=game_title,
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            guideline=guideline,
            include_details=True
        )
        
        # 필요한 정보만 반환
        return {
            "outline": chapter_outline,  # 챕터 개요
            "details": chapter_details   # 챕터 상세 내용
        }