"""
storyline_generator.py

스토리라인 생성 모듈
- GDD 핵심 요소를 기반으로 챕터별 스토리라인 생성
- 챕터별 요약, 장소, 등장인물, 상세 스토리, 서브 스토리 구성
"""

import os
import json
import logging
import re
from typing import Dict, List, Any, Optional

from .llm_service import LLMService

class StorylineGenerator:
    """
    게임 스토리라인 생성기
    
    GDD의 핵심 요소를 기반으로 지정된 챕터 수만큼 상세 스토리라인을 생성합니다.
    각 챕터는 요약, 장소, 등장인물, 상세 스토리, 서브 스토리로 구성됩니다.
    """
    
    def __init__(self, llm_service: LLMService = None):
        """
        스토리라인 생성기 초기화
        
        Args:
            llm_service (LLMService, optional): LLM 서비스 인스턴스
        """
        # LLM 서비스 설정
        self.llm = llm_service or LLMService()
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)

    def build_prompt(
        self, 
        gdd_core: str, 
        chapters: int, 
        character_relationships: Dict = None,
        level_designs: List[Dict] = None
    ) -> str:
        """
        LLM에 전달할 프롬프트 구성
        
        Args:
            gdd_core (str): GDD 핵심 요소 텍스트
            chapters (int): 생성할 챕터 수
            character_relationships (Dict, optional): 캐릭터 간 관계 정보
            level_designs (List[Dict], optional): 레벨 디자인 정보
            
        Returns:
            str: 완성된 프롬프트
        """
        self.logger.info(f"Building prompt for generating {chapters} chapters...")
        
        # 기본 프롬프트 구성
        prompt_parts = [
            "당신은 전문 게임 스토리 작가입니다. 아래 정보를 바탕으로 매력적이고 일관성 있는 게임 스토리를 작성해주세요.",
            f"다음 GDD 핵심 요소를 기반으로 {chapters}개의 상세 챕터를 생성해주세요.",
            "각 챕터는 다음 형식으로 작성해주세요:",
            "# 챕터 N: [제목]",
            "## 요약",
            "[챕터의 간략한 요약]",
            "## 장소",
            "[챕터의 주요 배경 장소들]",
            "## 등장인물",
            "[이 챕터에 등장하는 주요 캐릭터들]",
            "## 상세 스토리",
            "[상세한 챕터 내용 - 최소 3-4 문단]",
            "## 서브 스토리",
            "[2-3개의 관련 서브 스토리 또는 사이드 퀘스트]",
            "\n\n해당 챕터의 이벤트들이 게임의 전체 스토리에 어떻게 기여하는지 고려해주세요.",
            "캐릭터 간 관계가 스토리에 반영되어야 합니다.",
            "각 챕터는 레벨 디자인 정보와 연결되도록 작성해주세요.",
        ]
        
        # 캐릭터 관계 정보가 있으면 추가
        if character_relationships and len(character_relationships) > 0:
            rel_parts = ["## 캐릭터 관계 정보:"]
            for char, relations in character_relationships.items():
                rel_parts.append(f"- {char}:")
                for related_char, rel_type in relations.items():
                    rel_parts.append(f"  * {related_char}와(과)의 관계: {rel_type}")
            prompt_parts.append("\n".join(rel_parts))
        
        # 레벨 디자인 정보가 있으면 추가
        if level_designs and len(level_designs) > 0:
            level_parts = ["## 레벨 디자인 정보:"]
            
            for i, level in enumerate(level_designs):
                level_name = level.get("name", f"레벨 {i+1}")
                level_parts.append(f"### {level_name}")
                
                if level.get("theme"):
                    level_parts.append(f"- 테마 및 배경 스토리: {level['theme']}")
                    
                if level.get("atmosphere"):
                    level_parts.append(f"- 분위기와 아트 디렉션: {level['atmosphere']}")
                    
                if level.get("mechanics") and len(level["mechanics"]) > 0:
                    level_parts.append("- 핵심 메커니즘 및 고유 특징:")
                    for mech in level["mechanics"]:
                        level_parts.append(f"  * {mech}")
                        
                if level.get("fun_elements") and len(level["fun_elements"]) > 0:
                    level_parts.append("- 재미 요소:")
                    for fun in level["fun_elements"]:
                        level_parts.append(f"  * {fun}")
                        
                # 난이도 정보 추가
                if level.get("difficulty"):
                    level_parts.append("- 난이도 진행:")
                    diff = level["difficulty"]
                    if diff.get("early"):
                        level_parts.append(f"  * 초반: {diff['early']}")
                    if diff.get("mid"):
                        level_parts.append(f"  * 중반: {diff['mid']}")
                    if diff.get("late"):
                        level_parts.append(f"  * 후반: {diff['late']}")
                        
                level_parts.append("")  # 빈 줄 추가
            
            prompt_parts.append("\n".join(level_parts))
        
        # GDD 핵심 요소 추가
        prompt_parts.append("## GDD 핵심 요소:")
        prompt_parts.append(gdd_core)
        
        # 추가 지침
        prompt_parts.append("\n\n스토리라인 작성 시 다음 사항을 고려해주세요:")
        prompt_parts.append("1. 각 챕터는 GDD의 주요 내러티브와 레벨 디자인에 맞게 구성되어야 합니다.")
        prompt_parts.append("2. 캐릭터 간 관계(신뢰, 우호적, 중립, 적대적, 증오)가 스토리에 자연스럽게 반영되어야 합니다.")
        prompt_parts.append("3. 각 챕터의 장소 설명은 해당 레벨의 분위기와 아트 디렉션을 반영해야 합니다.")
        prompt_parts.append("4. 상세 스토리에서 해당 레벨의 핵심 메커니즘과 고유 특징이 게임플레이 요소로 등장해야 합니다.")
        prompt_parts.append("5. 서브 스토리는 레벨의 재미 요소나 숨겨진 콘텐츠를 탐색하는 내용을 포함하세요.")
        
        return "\n\n".join(prompt_parts)

    def generate_storyline(
        self, 
        gdd_core: str, 
        chapters: int,
        character_relationships: Dict = None,
        level_designs: List[Dict] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        LLM을 사용하여 스토리라인 생성
        
        Args:
            gdd_core (str): GDD 핵심 요소 텍스트
            chapters (int): 생성할 챕터 수
            character_relationships (Dict, optional): 캐릭터 간 관계 정보
            level_designs (List[Dict], optional): 레벨 디자인 정보
            temperature (float, optional): LLM 생성 온도 (창의성 조절)
            max_tokens (int, optional): 최대 토큰 수
            
        Returns:
            Dict[str, Any]: {
                "full_text": 전체 스토리라인 텍스트,
                "chapters": 파싱된 챕터별 정보 리스트
            }
            
        Raises:
            Exception: LLM 호출 중 오류 발생 시
        """
        prompt = self.build_prompt(gdd_core, chapters, character_relationships, level_designs)
        self.logger.info(f"Sending prompt to LLM to generate {chapters} chapters...")
        
        try:
            storyline_text = self.llm.generate(
                prompt, 
                temperature=temperature, 
                max_tokens=max_tokens
            )
            self.logger.info("Storyline generated successfully.")
            
            # 챕터별 정보 파싱
            parsed_chapters = self.parse_chapters(storyline_text)
            
            return {
                "full_text": storyline_text,
                "chapters": parsed_chapters
            }
        except Exception as e:
            self.logger.error(f"Error during storyline generation: {e}")
            raise

    def parse_chapters(self, storyline_text: str) -> List[Dict[str, Any]]:
        """
        생성된 스토리라인 텍스트를 챕터별로 파싱
        
        Args:
            storyline_text (str): 생성된 전체 스토리라인 텍스트
            
        Returns:
            List[Dict[str, Any]]: 파싱된 챕터 정보 리스트
                [
                    {
                        "order": 챕터 순서,
                        "title": 챕터 제목,
                        "summary": 요약,
                        "location": 장소,
                        "characters": 등장인물 리스트,
                        "story": 상세 스토리,
                        "substories": 서브스토리 리스트
                    },
                    ...
                ]
        """
        self.logger.info("Parsing chapters from storyline text...")
        chapters = []
        
        # 챕터별로 분리
        chapter_texts = []
        current_chapter = []
        
        chapter_pattern = r'^# 챕터|^#챕터|^# Chapter|^#Chapter'
        
        for line in storyline_text.split('\n'):
            if re.match(chapter_pattern, line.strip()):
                if current_chapter:
                    chapter_texts.append('\n'.join(current_chapter))
                current_chapter = [line]
            else:
                current_chapter.append(line)
                
        # 마지막 챕터 추가
        if current_chapter:
            chapter_texts.append('\n'.join(current_chapter))
        
        # 각 챕터 파싱
        for i, chapter_text in enumerate(chapter_texts):
            lines = chapter_text.split('\n')
            
            # 기본 정보 초기화
            chapter_info = {
                "order": i + 1,
                "title": "",
                "summary": "",
                "location": "",
                "characters": [],
                "story": "",
                "substories": [],
                "level_connections": []  # 레벨 디자인과의 연결 정보 추가
            }
            
            # 제목 추출
            for line in lines:
                title_match = re.match(r'# 챕터 (\d+): (.+)|# Chapter (\d+): (.+)', line.strip())
                if title_match:
                    groups = title_match.groups()
                    # 한글 매칭 시
                    if groups[0] and groups[1]:
                        chapter_info["order"] = int(groups[0])
                        chapter_info["title"] = groups[1].strip()
                    # 영문 매칭 시
                    elif groups[2] and groups[3]:
                        chapter_info["order"] = int(groups[2])
                        chapter_info["title"] = groups[3].strip()
                    break
                elif re.match(chapter_pattern, line.strip()):
                    # 제목이 다른 형식일 경우 (예: "# 챕터 1 - 시작")
                    title_parts = line.split(':', 1)
                    if len(title_parts) > 1:
                        chapter_info["title"] = title_parts[1].strip()
                    else:
                        # 콜론이 없는 경우 마이너스나 대시로 분리 시도
                        title_parts = re.split(r'[-—]', line, 1)
                        if len(title_parts) > 1:
                            chapter_info["title"] = title_parts[1].strip()
                    break
            
            # 섹션별 내용 추출
            current_section = None
            section_content = []
            
            for line in lines:
                if re.match(r'## 요약|##요약|## Summary', line.strip()):
                    current_section = "summary"
                    section_content = []
                elif re.match(r'## 장소|##장소|## Location', line.strip()):
                    if current_section == "summary" and section_content:
                        chapter_info["summary"] = '\n'.join(section_content).strip()
                    current_section = "location"
                    section_content = []
                elif re.match(r'## 등장인물|##등장인물|## Characters', line.strip()):
                    if current_section == "location" and section_content:
                        chapter_info["location"] = '\n'.join(section_content).strip()
                    current_section = "characters"
                    section_content = []
                elif re.match(r'## 상세 스토리|##상세 스토리|## Detailed Story', line.strip()):
                    if current_section == "characters" and section_content:
                        # 등장인물 리스트로 변환
                        chars_text = '\n'.join(section_content).strip()
                        # 쉼표, 구분자 및 불릿 포인트 처리
                        chars = re.split(r',|\n|•|\*|-', chars_text)
                        # 빈 문자열 및 공백 제거
                        chapter_info["characters"] = [c.strip() for c in chars if c.strip()]
                    current_section = "story"
                    section_content = []
                elif re.match(r'## 서브 스토리|##서브 스토리|## Sub-stories', line.strip()):
                    if current_section == "story" and section_content:
                        chapter_info["story"] = '\n'.join(section_content).strip()
                    current_section = "substories"
                    section_content = []
                elif line.strip() and not line.strip().startswith('#'):
                    section_content.append(line)
            
            # 마지막 섹션 처리
            if current_section == "substories" and section_content:
                substory_text = '\n'.join(section_content).strip()
                
                # 번호나 구분자로 서브스토리 분리 시도
                substories = []
                
                # 숫자+점, 숫자+콜론 패턴 확인
                number_patterns = [
                    r'^\d+\.\s+', r'^\d+:\s+',  # 숫자+점/콜론
                    r'^서브\s*스토리\s*\d+', r'^사이드\s*퀘스트\s*\d+',  # 서브스토리/사이드퀘스트+숫자
                    r'^[A-Z]\.', r'^\*\s+', r'^-\s+'  # 알파벳+점, 별표, 대시
                ]
                
                # 구분 기준 찾기
                separator_pattern = None
                for pattern in number_patterns:
                    if re.search(pattern, substory_text, re.MULTILINE):
                        separator_pattern = pattern
                        break
                
                if separator_pattern:
                    # 패턴으로 분리
                    substory_parts = re.split(f"(?m)(?={separator_pattern})", substory_text)
                    # 빈 부분 제거
                    substories = [part.strip() for part in substory_parts if part.strip()]
                else:
                    # 구분자를 찾지 못한 경우 빈 줄로 분리 시도
                    if '\n\n' in substory_text:
                        substories = [part.strip() for part in substory_text.split('\n\n') if part.strip()]
                    else:
                        # 구분자를 찾지 못하면 전체를 하나의 서브스토리로 처리
                        substories = [substory_text]
                
                chapter_info["substories"] = substories
            
            # 레벨 디자인과의 연결 파악 (스토리 내용과 장소명 기반)
            story_text = chapter_info.get("story", "") + "\n" + chapter_info.get("summary", "")
            location = chapter_info.get("location", "")
            
            # (추가 로직 필요 - 레벨 이름 매칭 등)
            
            chapters.append(chapter_info)
        
        self.logger.info(f"Successfully parsed {len(chapters)} chapters")
        return chapters

    def extract_graph_data(self, chapters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        챕터 정보에서 지식 그래프용 데이터 추출
        
        Args:
            chapters (List[Dict[str, Any]]): 파싱된 챕터 정보 리스트
            
        Returns:
            List[Dict[str, Any]]: 지식 그래프용 데이터
                [
                    {
                        "order": 챕터 순서,
                        "title": 챕터 제목,
                        "location": 장소,
                        "characters": 등장인물 리스트,
                        "level_connection": 연관된 레벨 이름
                    },
                    ...
                ]
        """
        graph_data = []
        
        for chapter in chapters:
            # 기본 데이터 추출
            data = {
                "order": chapter["order"],
                "title": chapter["title"],
                "location": chapter["location"],
                "characters": chapter["characters"],
                "level_connection": chapter.get("level_connections", []),
                "races": [],  # 종족 정보 (별도 추출 필요)
                "relations": {},  # 관계 정보 (별도 추출 필요)
                "habitat": {}  # 서식지 정보 (별도 추출 필요)
            }
            
            # 챕터 내용에서 종족 정보 추출 시도
            story_text = chapter.get("story", "")
            
            # 인간, 엘프, 드워프 등 일반적인 판타지 종족명 탐색
            common_races = ["인간", "엘프", "드워프", "오크", "고블린", "트롤", "요정", "언데드"]
            found_races = []
            
            for race in common_races:
                if race in story_text:
                    found_races.append(race)
            
            data["races"] = found_races
            
            graph_data.append(data)
        
        return graph_data

    def extract_quest_data(self, chapters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        챕터 정보에서 퀘스트 데이터 추출
        
        Args:
            chapters (List[Dict[str, Any]]): 파싱된 챕터 정보 리스트
            
        Returns:
            List[Dict[str, Any]]: 퀘스트 데이터
                [
                    {
                        "title": 퀘스트 제목,
                        "type": "main" | "side",
                        "chapter": 연관된 챕터 순서,
                        "description": 퀘스트 설명,
                        "characters": 관련 캐릭터 리스트,
                        "location": 퀘스트 위치,
                        "rewards": 퀘스트 보상 (있을 경우)
                    },
                    ...
                ]
        """
        quests = []
        
        for chapter in chapters:
            # 메인 퀘스트 (챕터당 1개)
            main_quest = {
                "title": f"{chapter['title']} 완료",
                "type": "main",
                "chapter": chapter["order"],
                "description": chapter["summary"],
                "characters": chapter["characters"],
                "location": chapter["location"],
                "rewards": "스토리 진행"
            }
            quests.append(main_quest)
            
            # 서브 퀘스트 (챕터의 서브스토리에서 추출)
            for i, substory in enumerate(chapter.get("substories", [])):
                # 서브스토리 제목 추출 시도
                title = ""
                description = substory
                
                # 첫 문장이나 첫 줄이 제목인지 확인
                first_line = substory.split("\n")[0].strip()
                if ":" in first_line:
                    title_parts = first_line.split(":", 1)
                    title = title_parts[0].strip()
                    if len(title_parts) > 1:
                        description = title_parts[1].strip() + substory[len(first_line):]
                elif "." in first_line and len(first_line.split(".", 1)[0]) < 30:
                    title_parts = first_line.split(".", 1)
                    title = title_parts[0].strip()
                    if len(title_parts) > 1:
                        description = title_parts[1].strip() + substory[len(first_line):]
                
                # 제목을 추출하지 못한 경우 기본값 사용
                if not title:
                    title = f"서브 퀘스트 {chapter['order']}-{i+1}"
                
                side_quest = {
                    "title": title,
                    "type": "side",
                    "chapter": chapter["order"],
                    "description": description,
                    "characters": extract_characters_from_text(description, chapter["characters"]),
                    "location": chapter["location"],
                    "rewards": extract_rewards_from_text(description)
                }
                quests.append(side_quest)
        
        return quests

def extract_characters_from_text(text: str, known_characters: List[str]) -> List[str]:
    """텍스트에서 등장인물 추출 보조 함수"""
    found_characters = []
    for character in known_characters:
        if character in text:
            found_characters.append(character)
    return found_characters

def extract_rewards_from_text(text: str) -> str:
    """텍스트에서 보상 정보 추출 보조 함수"""
    reward_keywords = ["보상", "reward", "아이템", "item", "경험치", "exp", "골드", "gold"]
    
    for keyword in reward_keywords:
        if keyword in text.lower():
            # 키워드 포함 문장 추출 시도
            sentences = text.split(".")
            for sentence in sentences:
                if keyword in sentence.lower():
                    return sentence.strip()
    
    return "경험치 및 아이템"  # 기본값
