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
        GDD에서 요구된 핵심 요소를 딕셔너리로 추출
        반환 예시:
        {
        "elevator_pitch": str,
        "narrative_overview": {
            "story_synopsis": str,
            "world_lore_and_history": str,
            "story_branching_and_arcs": str
        },
        "game_play_outline": {
            "win_lose_conditions": str,
            "endings_rewards": str,
            "fun_factor": str
        },
        "key_features": [str, ...]
        }
        """
        # 기본 구조 초기화
        result = {
            "elevator_pitch": "",
            "narrative_overview": {
                "story_synopsis": "",
                "world_lore_and_history": "",
                "story_branching_and_arcs": ""
            },
            "game_play_outline": {
                "win_lose_conditions": "",
                "endings_rewards": "",
                "fun_factor": ""
            },
            "key_features": []
        }

        lines = gdd_text.splitlines()

        # 1) Elevator Pitch
        for line in lines:
            m = re.match(r'^\s*\*\s*Elevator Pitch\s*[:\-]\s*(.+)', line, re.IGNORECASE)
            if m:
                result["elevator_pitch"] = m.group(1).strip()
                break

        # 2) Narrative Overview: 지정된 세 가지 항목만 추출
        for line in lines:
            m = re.match(r'^\s*\*\s*Story Synopsis\s*[:\-]\s*(.+)', line)
            if m:
                result["narrative_overview"]["story_synopsis"] = m.group(1).strip()
            m = re.match(r'^\s*\*\s*World Lore & History\s*[:\-]\s*(.+)', line)
            if m:
                result["narrative_overview"]["world_lore_and_history"] = m.group(1).strip()
            m = re.match(r'^\s*\*\s*Story Branching & Arcs\s*[:\-]\s*(.+)', line)
            if m:
                result["narrative_overview"]["story_branching_and_arcs"] = m.group(1).strip()

        # 3) Game Play Outline
        for line in lines:
            m = re.match(r'^\s*\*\s*Win/Lose Conditions\s*[:\-]\s*(.+)', line)
            if m:
                result["game_play_outline"]["win_lose_conditions"] = m.group(1).strip()
            m = re.match(r'^\s*\*\s*Endings\s*&\s*Rewards\s*[:\-]\s*(.+)', line)
            if m:
                result["game_play_outline"]["endings_rewards"] = m.group(1).strip()
            m = re.match(r'^\s*\*\s*Fun Factor\s*[:\-]\s*(.+)', line)
            if m:
                result["game_play_outline"]["fun_factor"] = m.group(1).strip()

        # 4) Key Features
        features = []
        in_feats = False
        for line in lines:
            # 섹션 6. Key Features 시작 감지 (숫자 앞에 # 있거나 없음)
            if re.match(r'^\s*(?:#+\s*)?6\.\s*Key Features', line, re.IGNORECASE):
                in_feats = True
                continue
            # 다음 섹션 (숫자 또는 # 숫자) 감지 시 종료
            if in_feats and re.match(r'^\s*(?:#+\s*)?\d+\.', line):
                break
            if in_feats:
                m = re.match(r'^\s*[\*\-]\s*(.+)', line)
                if m:
                    features.append(m.group(1).strip())
        result["key_features"] = features

        return result
    
    def extract_character_relationships(self, gdd_text: str) -> Dict[str, Dict[str, str]]:
        """
        GDD에서 캐릭터 간 관계 정보 추출
        
        Args:
            gdd_text (str): 생성된 GDD 전체 텍스트
            
        Returns:
            Dict[str, Dict[str, str]]: 캐릭터 정보
        """
        characters: Dict[str, Dict[str, str]] = {}
        
        try:
            # 여러 패턴으로 Narrative Overview 섹션 찾기
            narrative_section = ""
            narrative_patterns = [
                # 3. Narrative Overview 본문만: “#” 유무 상관없이, 4. Gameplay Description 전까지
                r'(?sm)^\s*(?:##?\s*)?3\.\s*Narrative Overview\s*'  # “3. Narrative Overview” 헤더
                r'(.*?)(?=^\s*4\.\s*Gameplay\s+Description)',      # “4. Gameplay Description” 전까지

                r'(?s)3\.\s*Narrative Overview\s*'
                r'(.*?)(?=4\.\s*Gameplay\s+Description)'
            ]
            
            for pattern in narrative_patterns:
                nav_match = re.search(pattern, gdd_text)
                if nav_match:
                    narrative_section = nav_match.group(1)
                    # print(narrative_section)
                    break
                    
            if not narrative_section:
                self.logger.warning("Narrative Overview 섹션을 찾을 수 없습니다.")
                return characters
                
            # 여러 패턴으로 캐릭터 정보 섹션 찾기
            character_section = ""
            character_section_patterns = [
                # "* Main Characters & Relationships:" 다음부터 "* World Lore" 전까지
                r'(?s)\*\s*Main Characters\s*&\s*Relationships:\s*(.*?)(?=\*\s*World Lore)',
                r'(?s)Main Characters\s*&\s*Relationships:\s*(.*?)(?=World Lore)'
            ]
            
            for pattern in character_section_patterns:
                char_match = re.search(pattern, narrative_section)
                if char_match:
                    character_section = char_match.group(1)
                    # print(character_section)
                    break
                    
            if not character_section:
                self.logger.warning("Characters & Relationships 섹션을 찾을 수 없습니다.")
                return characters
                
            # 1) 하이픈 리스트 블록용 패턴: multiline + dotall, non-greedy, 다음 하이픈 또는 문서 끝까지
            block_pattern = re.compile(
                r'(?ms)^\s*-\s*([^:]+):\s*'   # 그룹1: 캐릭터 이름
                r'(.+?)'                      # 그룹2: 설명+관계 문구 (non-greedy)
                r'(?=^\s*-\s*[^:]+:|\Z)'      # 다음 "- 이름:" 이나 문서 끝 앞에서 멈춤
            )

            for m in block_pattern.finditer(character_section):
                name  = m.group(1).strip()
                block = m.group(2).strip()

                # 1) relation 추출
                rel_match = re.search(r'(?m)^\s*플레이어와의\s*관계:\s*(\S+)', block)
                relation = rel_match.group(1).strip() if rel_match else ""

                # 2) description 추출: relation 라인 전체를 삭제
                description = re.sub(
                    r'(?m)^\s*플레이어와의\s*관계:.*$',  # 플레이어와의 관계: 이하 줄
                    '',                                 # 빈 문자열로 대체
                    block
                ).strip()

                characters[name] = {
                    "description": description,
                    "relation":   relation
                }
            return characters
            
        except Exception as e:
            self.logger.error(f"캐릭터 관계 추출 중 오류 발생: {e}")
            return characters

    def extract_level_design(self, gdd_text: str) -> List[Dict[str, Any]]:
        """
        GDD에서 레벨 디자인 정보 추출
        
        Args:
            gdd_text (str): 생성된 GDD 전체 텍스트
            
        Returns:
            List[Dict[str, Any]]: 레벨 디자인 정보 리스트
        """
        levels = []
        
        try:
            # 여러 패턴으로 Level Design 섹션 찾기
            level_design_section = ""
            level_design_patterns = [
                r'(?s)\*\*9\.\s*Level Design\*\*(.*?)(?=\*\*10\.)',
                r'(?s)9\.\s*Level Design(.*?)(?=10\.)',
                r'(?s)Level Design(.*?)UI/UX Design'
            ]
            
            for pattern in level_design_patterns:
                ld_match = re.search(pattern, gdd_text)
                if ld_match:
                    level_design_section = ld_match.group(1)
                    # print(level_design_section)
                    break
                    
            if not level_design_section:
                self.logger.warning("Level Design 섹션을 찾을 수 없습니다.")
                return levels
                
            # 1. Level List & Unique Features 블록 추출
            level_list_section = ""
            level_list_patterns = [
                r'(?s)1\)\s*Level List\s*&\s*Unique Features(.*?)(?=2\))',
                r'(?s)1\.\s*Level List\s*&\s*Unique Features(.*?)(?=2\.)',
                r'(?s)Level List\s*&\s*Unique Features(.*?)Difficulty'
            ]
            
            for pattern in level_list_patterns:
                list_match = re.search(pattern, level_design_section)
                if list_match:
                    level_list_section = list_match.group(1)
                    # print(level_list_section)
                    break
                    
            if not level_list_section:
                self.logger.warning("Level List & Unique Features 섹션을 찾을 수 없습니다.")
                return levels
                
            # 2. Difficulty Curve & Balancing 블록 추출
            difficulty_section = ""
            difficulty_patterns = [
                r'(?s)2\)\s*Difficulty Curve\s*&\s*Balancing(.*)',
                r'(?s)2\.\s*Difficulty Curve\s*&\s*Balancing(.*)',
                r'(?s)Difficulty Curve\s*&\s*Balancing(.*)'
            ]
            
            for pattern in difficulty_patterns:
                diff_match = re.search(pattern, level_design_section)
                if diff_match:
                    difficulty_section = diff_match.group(1)
                    # print(difficulty_section)
                    break
                    
            # 레벨 이름 추출
            level_names = []
            
            for line in level_list_section.splitlines():
                line = line.strip()
                # 1) '*' 로 시작하는 줄만 골라내고
                if not line.startswith('*'):
                    continue

                # 2) 맨 앞의 '*' 제거
                name_part = line.lstrip('*').strip()

                # 3) 이름 뒤에 붙은 설명 구분자(‘–’, ‘-’, 콜론 등) 기준으로 잘라서
                #    실제 레벨명만 취한다
                name = re.split(r'\s*[-–:]\s*', name_part)[0]

                # 4) 빈 문자열 아니면 추가
                if name:
                    level_names.append(name)
                    
            if not level_names:
                self.logger.warning("레벨 이름을 추출할 수 없습니다.")
                return levels
                
            self.logger.info(f"발견된 레벨 이름: {level_names}")
            
            # 레벨별 정보 추출
            for level_name in level_names:
                level_info = {
                    "name": level_name,
                    "theme": "",
                    "atmosphere": "",
                    "mechanics": []
                }
                
                # 레벨 내용 추출
                level_content = ""
                level_content_patterns = [
                    f'\\*\\s+{re.escape(level_name)}[^\\n]*\\n([^\\*]+)',
                    f'{re.escape(level_name)}[^\\n]*\\n([^\\*]+)'
                ]
                
                for pattern in level_content_patterns:
                    level_match = re.search(pattern, level_list_section, re.DOTALL)
                    if level_match:
                        level_content = level_match.group(1)
                        # print(level_content)
                        break
                        
                if level_content:
                    # 테마 추출
                    theme_patterns = [
                        r'(?:테마|Theme)\s*&\s*(?:배경\s*스토리|Background\s*Story)[^:]*:\s*([^\n]+)',
                        r'테마[^:]*:\s*([^\n]+)',
                    ]
                    
                    for pattern in theme_patterns:
                        theme_match = re.search(pattern, level_content, re.IGNORECASE)
                        if theme_match:
                            level_info["theme"] = theme_match.group(1).strip()
                            break
                    
                    # 분위기 추출
                    atmosphere_patterns = [
                        r'(?:분위기|Atmosphere)\s*&\s*(?:아트\s*디렉션|Art\s*Direction)[^:]*:\s*([^\n]+)',
                        r'분위기[^:]*:\s*([^\n]+)',
                    ]
                    
                    for pattern in atmosphere_patterns:
                        atmosphere_match = re.search(pattern, level_content, re.IGNORECASE)
                        if atmosphere_match:
                            level_info["atmosphere"] = atmosphere_match.group(1).strip()
                            break
                    
                    # 핵심 메커니즘 추출
                    mechanics = []
                    lines = level_content.splitlines()
                    capture = False

                    for line in lines:
                        # 1) "핵심 메커니즘" 헤더를 만나면 캡처 모드 on
                        if re.search(r'(?:핵심\s*메커니즘|Core\s*Mechanic)', line, re.IGNORECASE):
                            capture = True
                            continue

                        if capture:
                            # → Fun Elements가 나오면 중단
                            if re.match(r'\s*-\s*Fun\s*Elements\s*:', line, re.IGNORECASE):
                                break

                            # 2) 기존 방식: 리스트 아이템만 추가
                            m = re.match(r'\s*-\s*(.+)', line)
                            if m:
                                mechanics.append(m.group(1).strip())
                            else:
                                break

                    level_info["mechanics"] = mechanics
                
                # 유효한 레벨 정보인지 확인 (최소한 이름은 있어야 함)
                if level_info["name"]:
                    levels.append(level_info)
                    self.logger.info(f"레벨 '{level_name}' 정보 추출 완료")
            
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