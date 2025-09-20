"""
game_design_generator.py

Game Design Document (GDD) 생성 모듈
- 템플릿을 기반으로 프롬프트 구성
- 캐릭터 관계(신뢰·우호적·중립·적대적·증오) 포함
- LLM을 사용하여 완성된 GDD 생성
"""

import os
import json
import logging
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

from .llm_service import LLMService

class GameDesignGenerator:
    """
    게임 디자인 문서(GDD) 생성기
    
    사용자 입력 기반으로 LLM에 프롬프트를 구성해 GDD를 생성합니다.
    GDD는 표준 템플릿을 사용하며, Narrative Overview 섹션에는
    캐릭터 간 관계(신뢰·우호적·중립·적대적·증오)가 포함됩니다.
    """

    def __init__(
        self,
        llm_service: LLMService = None,
        template_dir: str = None
    ) -> None:
        """
        GDD 생성기 초기화
        
        Args:
            llm_service (LLMService, optional): LLM 서비스 인스턴스
            template_dir (str, optional): 템플릿 디렉토리 경로
        """
        # LLM 서비스 설정
        self.llm = llm_service or LLMService()

        # 템플릿 디렉토리 설정 (상대 경로 사용)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.template_dir = template_dir or os.path.join(base_dir, 'templates')

        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Template directory set to: {self.template_dir}")

    def load_template(self) -> str:
        """
        GDD.md 템플릿 파일 로드
        
        Returns:
            str: 템플릿 내용
            
        Raises:
            FileNotFoundError: 템플릿 파일이 없는 경우
        """
        template_path = os.path.join(self.template_dir, 'GDD.md')
        if not os.path.isfile(template_path):
            self.logger.error(f"GDD template not found at {template_path}")
            raise FileNotFoundError(f"Template not found: {template_path}")

        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.logger.debug("Loaded GDD template successfully.")
        return content

    def build_prompt(
        self,
        idea: str,
        genre: str,
        target: str,
        concept: str
    ) -> str:
        """
        LLM에 전달할 프롬프트 구성
        
        Args:
            idea (str): 게임 아이디어 설명
            genre (str): 게임 장르
            target (str): 타겟 오디언스
            concept (str): 게임 컨셉
            
        Returns:
            str: 완성된 프롬프트
        """
        self.logger.info("Building prompt for GDD generation...")
        template = self.load_template()

        # 관계 타입 예시를 추가한 프롬프트 구성
        relationship_example = """
        - 에리안: 차원 여행자로서 주인공의 길잡이 역할을 맡는 신비로운 존재. 지혜롭고 사려 깊은 성격으로, 주인공에게 조언을 아끼지 않는다.  
          플레이어와의 관계: 신뢰  
        - 카린: 불의 차원에서 만난 전사로, 강력한 전투력을 지녔다. 초기에 주인공을 경계하지만, 차차 우정을 쌓아간다.  
          플레이어와의 관계: 우호적  
        - 녹터: 어둠의 차원을 지배하는 강력한 마법사로, 여러 차원을 혼란에 빠뜨리려 한다. 주인공의 주요 적으로, 무자비하고 교활하다.  
          플레이어와의 관계: 적대적  
        """

        # 레벨 예시를 추가한 프롬프트 구성
        level_example = """
        9. Level Design
            1. Level List & Unique Features
            * 불의 차원
                - Theme & Background Story: 화산과 용암이 흐르는 차원, 강력한 불의 생물들이 지키고 있다.  
                - Atmosphere & Art Direction: 붉은 톤의 하늘과 땅, 뜨거운 열기  
                - Core Mechanic & Unique Features: 
                - 용암 피하기 퍼즐  
                - 불의 정령들과의 전투  
                - 용암 속 숨겨진 보물 찾기  
                - Fun Elements: 스킬 연계를 통한 적 빠르게 처치하기, 숨겨진 보물 구역  
                
            * 물의 차원
                - Theme & Background Story: 물의 신비로운 생명체들이 사는 차원, 해류가 강하게 흐른다.  
                - Atmosphere & Art Direction: 푸른 바다와 하늘, 반짝이는 물결  
                - Core Mechanic & Unique Features: 
                - 해류를 이용한 이동 퍼즐  
                - 물속 생물들과의 전투  
                - 물 속 숨겨진 유물 찾기  
                - Fun Elements: 해류 타고 이동하기, 숨겨진 유물 수집 보너스  
                
            * 어둠의 차원
                - Theme & Background Story: 어둠의 힘이 지배하는 차원, 음울하고 불길한 분위기  
                - Atmosphere & Art Direction: 검은 하늘과 대지, 희미한 빛  
                - Core Mechanic & Unique Features: 
                - 어둠 속에서의 생존 퍼즐  
                - 어둠의 생명체들과의 전투  
                - 어둠 속 숨겨진 비밀 발견하기  
                - Fun Elements: 어둠 속 길 찾기, 랜덤 이벤트

            2. Difficulty Curve & Balancing
            * Difficulty Progression: 
                - 불의 차원: 초반(기본 전투, 쉬움) → 중반(용암 퍼즐, 보통) → 후반(보스 전투, 어려움)  
                - 물의 차원: 초반(해류 이용 이동, 보통) → 중반(물속 전투, 어려움) → 후반(숨겨진 유물 찾기, 매우 어려움)
                - 어둠의 차원: 초반(어둠 속 탐험, 보통) → 중반(어둠의 생물 전투, 어려움) → 후반(최종 보스, 매우 어려움)
            * Balancing Considerations: 
                - 스킬과 장비 업그레이드에 따른 적 난이도 조정
                - 주요 구간 전후 회복 아이템 배치
                - 첫 클리어 보상과 추가 도전 보상 차별화
        """

        # 프롬프트 구성
        parts = [
            "당신은 전문 게임 디자이너이자 엄격한 문서 포맷터입니다. 창의적이고 구체적인 게임 기획을 작성해 주세요.",
            "모든 내용은 한국어로 생성해주세요.",
            "아래 파라미터를 기반으로 게임 디자인 문서(GDD)를 생성해주세요.",
            "아래 주어진 GDD 템플릿의 서식(머리말, 번호, 글머리, 들여쓰기, 빈 줄 등)을 **100% 그대로** 유지하며, 오직 각 섹션의 내용만 채워 넣어야 합니다.",
            "템플릿에 없는 항목을 추가하거나, 순서를 바꾸거나, 스타일을 바꾸면 안 됩니다.",
            template,
            "또한 Narrative Overview의 Main Characters & Relationships에는 등장 캐릭터와 각 캐릭터의 소개를 생성해주세요.(캐릭터 3개 이상)",
            "또한 각 캐릭터마다 플레이어와의 관계 유형(신뢰, 우호적, 중립, 적대적, 증오 중 하나)을 반드시 명시해주세요.",
            "아래는 Main Characters & Relationships 예시입니다. 꼭 참고해서 똑같은 양식으로 생성해주세요.",
            relationship_example,
            "아래는 Level Design의 예시입니다. 꼭 참고해서 똑같은 양식으로 생성해주세요. (Level 3개 이상)",
            level_example,
            f"게임 아이디어: {idea}",
            f"장르: {genre}",
            f"타겟 오디언스: {target}",
            f"컨셉: {concept}"
        ]
        prompt = "\n\n".join(parts)
        self.logger.debug(f"Prompt preview:\n{prompt[:200]}...")
        return prompt

    def extract_gdd_core(self, gdd_text: str) -> dict:
        """
        GDD에서 요구된 핵심 요소를 딕셔너리로 추출 (멀티라인 지원)
        """
        result = {
            "elevator_pitch": "",
            "narrative_overview": {},
            "game_play_outline": {},
            "key_features": []
        }
        
        def get_section_content(text, start_keyword, end_keyword_pattern):
            try:
                # 섹션 시작 키워드와 끝 키워드 패턴으로 섹션 전체 내용을 찾음
                section_pattern = re.compile(f'{start_keyword}(.*?){end_keyword_pattern}', re.DOTALL | re.IGNORECASE)
                section_match = re.search(section_pattern, text)
                if not section_match:
                    return ""
                
                section_text = section_match.group(1)
                
                # 하위 항목 추출
                sub_items = {}
                item_pattern = re.compile(r'\*\s*([^:]+):\s*(.*?)(?=\s*\*|$)', re.DOTALL)
                matches = item_pattern.findall(section_text)
                
                # 만약 위 패턴으로 못찾으면, 한줄짜리 간단한 패턴으로 다시 시도
                if not matches:
                    pattern = re.compile(f'\*\s*{start_keyword}\s*[:\-]?\s*(.*)', re.IGNORECASE)
                    match = pattern.search(text)
                    if match:
                        return match.group(1).strip()
                    return section_text.strip()

                # 멀티라인 콘텐츠 처리
                content = ""
                for match in matches:
                    content += match[0].strip() + ": " + match[1].strip() + "\n"
                return content.strip()

            except Exception:
                return ""

        # 1) Elevator Pitch
        result["elevator_pitch"] = get_section_content(gdd_text, "Elevator Pitch", "(Table of Contents|1\.\s*Project Overview)")

        # 2) Narrative Overview
        narrative_text = get_section_content(gdd_text, "3\.\s*Narrative Overview", "4\.\s*Gameplay Description")
        result["narrative_overview"] = {
            "story_synopsis": get_section_content(narrative_text, "Story Synopsis", "Main Characters"),
            "world_lore_and_history": get_section_content(narrative_text, "World Lore & History", "Story Branching"),
            "story_branching_and_arcs": get_section_content(narrative_text, "Story Branching & Arcs", "4\.")
        }

        # 3) Game Play Outline
        gameplay_text = get_section_content(gdd_text, "5\.\s*Game Play Outline", "6\.\s*Key Features")
        result["game_play_outline"] = {
            "win_lose_conditions": get_section_content(gameplay_text, "Win/Lose Conditions", "Endings & Rewards"),
            "endings_rewards": get_section_content(gameplay_text, "Endings & Rewards", "Fun Factor"),
            "fun_factor": get_section_content(gameplay_text, "Fun Factor", "6\.")
        }

        # 4) Key Features
        key_features_text = get_section_content(gdd_text, "6\.\s*Key Features", "7\.\s*Mechanics Design")
        if key_features_text:
            # Key Features는 보통 불릿 포인트 리스트로 제공됨
            result["key_features"] = [line.strip() for line in key_features_text.split('*') if line.strip()]

        return result
    
    def extract_character_relationships(self, gdd_text: str) -> Dict[str, Dict[str, str]]:
        """
        GDD에서 캐릭터 간 관계 정보 추출 (더 유연한 버전)
        """
        characters: Dict[str, Dict[str, str]] = {}
        try:
            # 3. Narrative Overview 섹션 전체를 가져옴
            narrative_section_match = re.search(r'(?sm)3\.\s*Narrative Overview(.*?)(?=4\.\s*Gameplay Description)', gdd_text)
            if not narrative_section_match:
                self.logger.warning("Narrative Overview 섹션을 찾을 수 없습니다.")
                return characters

            narrative_section = narrative_section_match.group(1)
            
            # Main Characters & Relationships 하위 섹션을 찾음
            char_section_match = re.search(r'(?sm)\*\s*Main Characters & Relationships:\s*(.*?)(?=\s*\*|\Z)', narrative_section)
            if not char_section_match:
                self.logger.warning("Characters & Relationships 섹션을 찾을 수 없습니다.")
                return characters
            
            character_section = char_section_match.group(1)
            
            # 각 캐릭터 블록(- 으로 시작)을 찾음
            block_pattern = re.compile(r'(?ms)^\s*-\s*([^:]+):\s*(.*?)(?=(?:^\s*-)|\Z)')

            for m in block_pattern.finditer(character_section):
                name = m.group(1).strip()
                block = m.group(2).strip()

                # 관계 추출
                rel_match = re.search(r'플레이어와의\s*관계:\s*(\S+)', block)
                relation = rel_match.group(1).strip() if rel_match else ""

                # 설명 추출 (관계 라인 제외)
                description = re.sub(r'플레이어와의\s*관계:.*', '', block).strip()

                characters[name] = {
                    "description": description,
                    "relation": relation
                }
            return characters
        except Exception as e:
            self.logger.error(f"캐릭터 관계 추출 중 오류 발생: {e}")
            return characters

    def extract_level_design(self, gdd_text: str) -> List[Dict[str, Any]]:
        """
        GDD에서 레벨 디자인 정보 추출 (더 유연한 버전)
        """
        levels = []
        try:
            # 9. Level Design 섹션 전체를 가져옴
            level_design_section_match = re.search(r'(?s)9\.\s*Level Design(.*?)(?=10\.\s*UI/UX Design)', gdd_text)
            if not level_design_section_match:
                self.logger.warning("Level Design 섹션을 찾을 수 없습니다.")
                return levels
            
            level_design_section = level_design_section_match.group(1)

            # '*'로 시작하는 각 레벨 블록을 분리
            level_blocks = re.split(r'(?m)^\s*\*', level_design_section)
            
            for block in level_blocks:
                if not block.strip():
                    continue

                # 레벨 이름 추출
                level_name_match = re.match(r'([^\n:]+)', block)
                if not level_name_match:
                    continue
                
                level_name = level_name_match.group(1).strip()
                level_info = {"name": level_name, "theme": "", "atmosphere": "", "mechanics": []}

                def get_detail(pattern, text):
                    match = re.search(pattern, text, re.IGNORECASE)
                    return match.group(1).strip() if match else ""

                # Theme, Atmosphere, Mechanics 추출
                level_info["theme"] = get_detail(r'(?:Theme & Background Story|테마)[^:]*:\s*([^\n]+)', block)
                level_info["atmosphere"] = get_detail(r'(?:Atmosphere & Art Direction|분위기)[^:]*:\s*([^\n]+)', block)
                
                mechanics_match = re.search(r'Core Mechanic & Unique Features:\s*(.*)', block, re.DOTALL)
                if mechanics_match:
                    mechanics_text = mechanics_match.group(1)
                    # '-'를 기준으로 메커니즘 분리
                    level_info["mechanics"] = [mech.strip() for mech in mechanics_text.split('-') if mech.strip()]

                if level_info["name"]:
                    levels.append(level_info)
            
            self.logger.info(f"총 {len(levels)}개 레벨 디자인 정보 추출 완료")
            return levels
        except Exception as e:
            self.logger.error(f"레벨 디자인 추출 중 오류 발생: {e}")
            return levels

    def generate_gdd(
        self,
        idea: str,
        genre: str,
        target: str,
        concept: str,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        LLM을 사용하여 GDD 생성
        
        Args:
            idea (str): 게임 아이디어
            genre (str): 게임 장르
            target (str): 타겟 오디언스
            concept (str): 게임 컨셉
            temperature (float, optional): LLM 생성 온도 (창의성 조절)
            max_tokens (int, optional): 최대 토큰 수
            
        Returns:
            Dict[str, Any]: {
                "full_text": GDD 전체 내용,
                "core_elements": 스토리라인 생성용 핵심 내용,
                "characters": 캐릭터 관계 정보,
                "levels": 레벨 디자인 정보
            }
            
        Raises:
            Exception: LLM 호출 중 오류 발생 시
        """
        prompt = self.build_prompt(idea, genre, target, concept)
        self.logger.info("Sending prompt to LLM...")
        
        try:
            full_text = self.llm.generate(
                prompt, 
                temperature=temperature, 
                max_tokens=max_tokens
            )
            self.logger.info("GDD generated successfully.")
            
            # 핵심 요소 추출
            core_elements = self.extract_gdd_core(full_text)
            
            # 캐릭터 추출
            characters = self.extract_character_relationships(full_text)
            
            # 레벨 디자인 정보 추출
            levels = self.extract_level_design(full_text)
            
            return {
                "full_text": full_text,
                "core_elements": core_elements,
                "characters": characters,
                "levels": levels
            }
        except Exception as e:
            self.logger.error(f"Error during GDD generation: {e}")
            raise