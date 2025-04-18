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
    
    def generate_chapter_content(self, game_title, chapter_number, chapter_title="", guideline=""):
        """
        챕터 내용을 생성합니다.
        
        Args:
            game_title: 게임 제목
            chapter_number: 챕터 번호
            chapter_title: 챕터 제목 (없으면 빈 문자열)
            guideline: 사용자가 입력한 가이드라인
            
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
        
        # 생성 요청 형식
        prompt += """
        ## 요청
        이 챕터에 대한 다음 정보를 마크다운 형식으로 생성해주세요:
        1. 챕터에 대한 간략한 설명 (1-2 문장)
        2. 목표 (2-4개 항목) - 글머리 기호로 나열
        3. 주요 위치 (2-3개 항목) - 글머리 기호로 나열
        4. 주요 사건 (3-5개 항목) - 글머리 기호로 나열
        5. 도전 과제 (2-3개 항목) - 글머리 기호로 나열
        
        다음 형식을 사용해주세요:

        (챕터에 대한 간략한 설명)
        
        **목표:**
        - (목표 1)
        - (목표 2)
        ...
        
        **주요 위치:**
        - (위치 1)
        - (위치 2)
        ...
        
        **주요 사건:**
        - (사건 1)
        - (사건 2)
        ...
        
        **도전 과제:**
        - (도전 과제 1)
        - (도전 과제 2)
        ...
        """
        
        # 3. LLM으로 내용 생성
        try:
            generated_content = self.llm_service.generate_text(
                prompt=prompt,
                provider="openai",
                temperature=0.7,
                max_tokens=1500
            )
            
            # 필요하면 형식을 정리 (마크다운 형식이 아닌 부분 제거)
            return self._clean_generated_content(generated_content)
            
        except Exception as e:
            print(f"챕터 내용 생성 중 오류 발생: {str(e)}")
            return f"내용 생성 중 오류가 발생했습니다: {str(e)}"
    
    def _clean_generated_content(self, content):
        """
        생성된 내용을 정리합니다.
        
        Args:
            content: 생성된 텍스트
            
        Returns:
            정리된 텍스트
        """
        # '(챕터에 대한 간략한 설명)' 같은 안내 구문 제거
        content = re.sub(r'\(([^)]*)\)', r'\1', content)
        
        # 불필요한 마크다운 헤더 제거 (###, ## 등)
        content = re.sub(r'^#{1,6}\s+.*$', '', content, flags=re.MULTILINE)
        
        # 양식에 맞게 정리
        content = content.strip()
        
        # 내용에 줄바꿈 추가 (단락 구분을 위해)
        content_parts = content.split('**목표:**')
        if len(content_parts) > 1:
            description = content_parts[0].strip()
            rest_content = '**목표:**' + content_parts[1]
            content = description + '\n\n' + rest_content
            
        # 각 섹션 사이에 빈 줄 추가
        for section in ["**목표:**", "**주요 위치:**", "**주요 사건:**", "**도전 과제:**"]:
            if section in content:
                content = content.replace(section, '\n' + section)
        
        # 필수 섹션 확인하고 없으면 추가
        required_sections = ["**목표:**", "**주요 위치:**", "**주요 사건:**", "**도전 과제:**"]
        
        for section in required_sections:
            if section not in content:
                # 섹션에 해당하는 글머리 기호 리스트 찾기
                list_items = re.findall(r'- .*?\n', content)
                if list_items:
                    # 목록 앞에 섹션 추가
                    content = content.replace(list_items[0], f"{section}\n{list_items[0]}")
        
        # 줄바꿈 정리 (연속된 빈 줄 제거)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content