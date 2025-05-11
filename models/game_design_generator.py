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
        **예시**  
        아린: 어린 시절부터 주인공과 함께 자란 친구로, 현재는 왕국 근위대의 핵심 기사. 강한 책임감과 따뜻한 인간미를 지님.  
        플레이어와의 관계: 신뢰  
         
        로그란: 폐허에서 은둔하며 살아가는 도적단 리더. 과묵하고 냉정하지만, 약자를 돕는 의리가 있음.  
        플레이어와의 관계: 중립  
        
        엘리아: 고대 마법서 연구에 집착하는 학자. 자신의 목표를 위해 수단과 방법을 가리지 않음.  
        플레이어와의 관계: 적대적  
        
        모르간: 어둠의 세력에 속한 마법사로, 주인공의 가족을 앗아간 원흉. 무자비하고 냉혹함.  
        플레이어와의 관계: 증오  
        """

        # 레벨 예시를 추가한 프롬프트 구성
        level_example = """
        1) Level List & Unique Features
        * Ancient Forest Entrance
        테마 & 배경 스토리: 주인공이 잃어버린 동료 단서를 찾기 위해 처음 발을 들이는 신비로운 숲 입구  
        분위기 & 아트 디렉션: 울창한 나무, 짙은 녹색 톤, 부드러운 빛줄기와 안개 효과  
        핵심 메커니즘 & 고유 특징:  
        - 점프 퍼즐 플랫폼  
        - 스파이크 함정  
        - 흔들리는 나무 다리  
        재미 요소:  
        - 나뭇잎 사이로 보이는 숨겨진 보물 상자  
        - 점프할 때마다 울리는 나뭇잎 사운드  

        * Desert Ruins Labyrinth
        테마 & 배경 스토리: 오래 전 사라진 왕국의 유적, 모래 폭풍으로 부분 매몰된 미로  
        분위기 & 아트 디렉션: 따뜻한 황토색·주황빛 하늘, 부서진 석조 문양  
        핵심 메커니즘 & 고유 특징:  
        - 모래 흘러내림 퍼즐(시간 제한)  
        - 숨겨진 함정 문  
        - 낙사지대 슬라이딩 구간  
        재미 요소:  
        - 함정 문 뒤의 비밀 보상 방  
        - 폭풍 속에서만 나타나는 환영 적  

        * Frost Peak Summit
        테마 & 배경 스토리: 영웅이 첫 보스를 마주하기 전 마지막 관문, 눈보라가 몰아치는 설산 정상  
        분위기 & 아트 디렉션: 차가운 청색·흰색 조화, 강한 바람과 눈발 효과  
        핵심 메커니즘 & 고유 특징:  
        - 미끄러운 얼음 바닥  
        - 한랭 대미지 구역(체온 게이지)  
        - 얼음 기둥 올라타기 퍼즐  
        재미 요소:  
        - 얼음 속 숨겨진 고대 유물  
        - 눈보라 속서 희미하게 보이는 길 표시  

        2) Difficulty Curve & Balancing
        * Ancient Forest Entrance
        난이도 진행 형태:  
        - 초반: 기본 점프·이동 튜토리얼 (쉬움)  
        - 중반: 타이밍 점프 도전 (보통)  
        - 후반: 스파이크 함정 + 이동 플랫폼 조합 (어려움)  
        밸런싱 고려사항:  
        - 튜토리얼 구간 직후 회복 포인트 배치  
        - 첫 클리어 보상으로 추가 경험치 제공  
        - 플랫폼 간격은 플레이어 기본 점프력에 맞춰 조정  

        * Desert Ruins Labyrinth
        난이도 진행 형태:  
        - 초반: 모래 미로 탐색(보통)  
        - 중반: 시간 제한 모래 흘러내림 퍼즐(어려움)  
        - 후반: 함정 문+낙사지대 조합(상당히 어려움)  
        밸런싱 고려사항:  
        - 각 퍼즐 구간 전 간단한 힌트 오브젝트 배치  
        - 모래 미로 중간 회복 아이템 배치  
        - 재도전 시 퍼즐 난이도 소폭 완화  

        * Frost Peak Summit
        난이도 진행 형태:  
        - 초반: 얼음 바닥 적응 구간 (보통)  
        - 중반: 얼음 기둥 퍼즐 + 체온 관리 (어려움)  
        - 후반: 눈보라 보스 전투 (매우 어려움)  
        밸런싱 고려사항:  
        - 체온 게이지 회복 포인트 배치  
        - 보스 전투 전 최종 회복 지점 마련  
        - 첫 클리어 보상으로 special 아이템(방한 장비) 제공 
        """

        # 프롬프트 구성
        parts = [
            "당신은 전문 게임 디자이너입니다. 창의적이고 구체적인 게임 기획을 작성해 주세요.",
            "모든 내용은 한국어로 생성해주세요.",
            "아래 파라미터를 기반으로 포괄적인 게임 디자인 문서(GDD)를 생성해주세요.",
            "Narrative Overview의 Main Characters & Relationships에는 등장 캐릭터와 각 캐릭터의 소개를 생성해주세요.(캐릭터 3개 이상)",
            "또한 각 캐릭터마다 플레이어와의 관계 유형(신뢰, 우호적, 중립, 적대적, 증오 중 하나)을 반드시 명시해주세요.",
            "아래는 Main Characters & Relationships 예시입니다. 꼭 참고해서 비슷한 형식으로 생성해주세요.",
            relationship_example,
            "아래는 Level Design의 예시입니다. 꼭 참고해서 비슷한 형식으로 생성해주세요. (Level 3개 이상)",
            level_example,
            f"게임 아이디어: {idea}",
            f"장르: {genre}",
            f"타겟 오디언스: {target}",
            f"컨셉: {concept}",
            "다음 템플릿을 꼭 사용해주세요:",
            template,
            "템플릿에 있는 모든 내용을 작성해주세요."
        ]
        prompt = "\n\n".join(parts)
        self.logger.debug(f"Prompt preview:\n{prompt[:200]}...")
        return prompt

    def extract_gdd_core(self, gdd_text: str) -> str:
        """
        GDD에서 스토리라인 생성에 필요한 핵심 요소 추출
        
        Args:
            gdd_text (str): 생성된 GDD 전체 텍스트
            
        Returns:
            str: 핵심 섹션들만 추출한 텍스트
        """
        core_sections = [
            "1. Project Overview",
            "3. Narrative Overview",
            "4. Gameplay Description",
            "5. Game Play Outline",
            "6. Key Features",
            "7. Mechanics Design",
            "9. Level Design"
        ]
        
        core_content = []
        lines = gdd_text.split('\n')
        
        # Cover Page는 항상 포함
        cover_content = []
        in_cover = True
        
        current_section = ""
        is_core_section = False
        
        for line in lines:
            # 섹션 헤더 확인
            if re.match(r'^[0-9]+\.', line.strip()):
                # 새로운 섹션 시작
                in_cover = False
                current_section = line.strip()
                is_core_section = any(section in current_section for section in core_sections)
                
                if is_core_section:
                    core_content.append(line)
                continue
            
            # 커버 페이지 내용 수집
            if in_cover:
                cover_content.append(line)
                continue
                
            # 핵심 섹션 내용 추가
            if is_core_section:
                core_content.append(line)
                
        # 커버 페이지와 핵심 섹션 내용 결합
        result = '\n'.join(cover_content + ['\n'] + core_content)
        return result

    def extract_character_relationships(self, gdd_text: str) -> Dict[str, Dict[str, str]]:
        """
        GDD에서 캐릭터 간 관계 정보 추출
        
        Args:
            gdd_text (str): 생성된 GDD 전체 텍스트
            
        Returns:
            Dict[str, Dict[str, str]]: 캐릭터 관계 정보
        """
        relationships: Dict[str, Dict[str, str]] = {}
        
        try:
            # 여러 패턴으로 Narrative Overview 섹션 찾기
            narrative_section = ""
            narrative_patterns = [
                r'(?s)\*\*3\.\s*Narrative Overview\*\*(.*?)(?=\*\*4\.)',
                r'(?s)3\.\s*Narrative Overview(.*?)(?=4\.)',
                r'(?s)Narrative Overview(.*?)Gameplay Description'
            ]
            
            for pattern in narrative_patterns:
                nav_match = re.search(pattern, gdd_text)
                if nav_match:
                    narrative_section = nav_match.group(1)
                    break
                    
            if not narrative_section:
                self.logger.warning("Narrative Overview 섹션을 찾을 수 없습니다.")
                return relationships
                
            # 여러 패턴으로 캐릭터 정보 섹션 찾기
            character_section = ""
            character_section_patterns = [
                r'(?s)\* Main Characters\s*\n?& Relationships:(.*?)(?=\* World Lore)',
                r'(?s)Main Characters\s*&\s*Relationships:(.*?)(?=World Lore)',
                r'(?s)Main Characters:(.*?)(?=World Lore)',
                r'(?s)Characters\s*&\s*Relationships:(.*?)(?=World)'
            ]
            
            for pattern in character_section_patterns:
                char_match = re.search(pattern, narrative_section)
                if char_match:
                    character_section = char_match.group(1)
                    break
                    
            if not character_section:
                self.logger.warning("Characters & Relationships 섹션을 찾을 수 없습니다.")
                return relationships
                
            # 캐릭터 정보 추출
            # 여러 가지 캐릭터 정의 패턴 처리
            character_patterns = [
                r'(?m)^\s*\*\s*([^:]+?):\s*(.*?)$',       # * 캐릭터명: 설명
                r'(?m)^\s*-\s*\*\*([^:]+):\*\*\s*(.*?)$', # - **캐릭터명:** 설명
                r'(?m)^\s*\*\*([^:]+):\*\*\s*(.*?)$',     # **캐릭터명:** 설명
                r'(?m)^\s*([^:]+?):\s*(.*?)$'             # 캐릭터명: 설명
            ]
            
            # 관계 패턴 처리
            relation_patterns = [
                r'(?m)^\s*플레이어와의\s*관계:\s*(\S+)',   # 플레이어와의 관계: 타입
                r'(?m)플레이어와의\s*관계:\s*(\S+)',       # 플레이어와의 관계: 타입
                r'관계:\s*(\S+)'                          # 관계: 타입
            ]
            
            # 캐릭터 정보 추출
            characters = []
            character_blocks = {}
            
            # 캐릭터 블록 구분하기 (각 캐릭터당 설명+관계 정보)
            for pattern in character_patterns:
                matches = list(re.finditer(pattern, character_section))
                if matches:
                    # 각 캐릭터 정보와 다음 캐릭터 정보 사이의 모든 텍스트 추출
                    for i, match in enumerate(matches):
                        char_name = match.group(1).strip()
                        start = match.start()
                        end = len(character_section)
                        
                        # 다음 캐릭터 정보가 있으면 여기까지만 추출
                        if i < len(matches) - 1:
                            end = matches[i+1].start()
                            
                        character_blocks[char_name] = character_section[start:end]
                        characters.append(char_name)
                        
                    # 캐릭터 정보를 찾았으면 종료
                    if characters:
                        break
            
            # 각 캐릭터의 관계 정보 추출
            for char_name in characters:
                if char_name in ["World Lore", "Story Branching", "Synopsis"]:
                    continue
                    
                relationships[char_name] = {}
                char_block = character_blocks.get(char_name, "")
                
                # 관계 정보 찾기
                for pattern in relation_patterns:
                    rel_match = re.search(pattern, char_block)
                    if rel_match:
                        rel_type = rel_match.group(1).strip()
                        relationships[char_name]['플레이어'] = rel_type
                        break
            
            self.logger.info(f"추출된 캐릭터 관계: {relationships}")
            return relationships
            
        except Exception as e:
            self.logger.error(f"캐릭터 관계 추출 중 오류 발생: {e}")
            return relationships

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
                    break
                    
            # 레벨 이름 추출
            level_names = []
            
            # 여러 패턴으로 레벨 이름 찾기
            level_name_patterns = [
                r'\*\s+[""]?([^"\n:]+?)[""]?(?=\s+테마|\s+Theme|\s+분위기)',  # * 레벨명 테마
                r'\*\s+[""]?([^"\n:]+?)[""]?',                              # * 레벨명
            ]
            
            for pattern in level_name_patterns:
                matches = re.findall(pattern, level_list_section)
                if matches:
                    level_names = [name.strip() for name in matches if name.strip() and 
                                not name.startswith("Level List") and 
                                not name.startswith("Difficulty")]
                    break
                    
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
                    "mechanics": [],
                    "fun_elements": [],
                    "difficulty": {
                        "early": "",
                        "mid": "",
                        "late": ""
                    },
                    "balancing": []
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
                    mechanics_patterns = [
                        r'(?:핵심\s*메커니즘|Core\s*Mechanic)[^:]*:[^-]*((?:-[^\n]+\n)+)',
                        r'메커니즘[^:]*:[^-]*((?:-[^\n]+\n)+)',
                    ]
                    
                    for pattern in mechanics_patterns:
                        mechanics_match = re.search(pattern, level_content, re.IGNORECASE | re.DOTALL)
                        if mechanics_match:
                            mechanics_text = mechanics_match.group(1)
                            mechanics = []
                            for line in mechanics_text.split('\n'):
                                line = line.strip()
                                if line.startswith('-'):
                                    mechanics.append(line[1:].strip())
                            if mechanics:
                                level_info["mechanics"] = mechanics
                            break
                    
                    # 재미 요소 추출
                    fun_patterns = [
                        r'(?:재미\s*요소|Fun\s*Elements)[^:]*:[^-]*((?:-[^\n]+\n)+)',
                        r'재미[^:]*:[^-]*((?:-[^\n]+\n)+)',
                    ]
                    
                    for pattern in fun_patterns:
                        fun_match = re.search(pattern, level_content, re.IGNORECASE | re.DOTALL)
                        if fun_match:
                            fun_text = fun_match.group(1)
                            fun_elements = []
                            for line in fun_text.split('\n'):
                                line = line.strip()
                                if line.startswith('-'):
                                    fun_elements.append(line[1:].strip())
                            if fun_elements:
                                level_info["fun_elements"] = fun_elements
                            break
                
                # 난이도 정보 추출
                if difficulty_section:
                    # 레벨별 난이도 블록 찾기
                    level_diff_content = ""
                    level_diff_patterns = [
                        f'\\*\\s+{re.escape(level_name)}[^\\n]*\\n([^\\*]+)',
                        f'{re.escape(level_name)}[^\\n]*\\n([^\\*]+)'
                    ]
                    
                    for pattern in level_diff_patterns:
                        level_diff_match = re.search(pattern, difficulty_section, re.DOTALL)
                        if level_diff_match:
                            level_diff_content = level_diff_match.group(1)
                            break
                            
                    if level_diff_content:
                        # 난이도 진행 형태 추출
                        diff_progress_patterns = [
                            r'난이도\s*진행\s*형태[^:]*:((?:[^\n]*\n)*?)',
                            r'난이도[^:]*:((?:[^\n]*\n)*?)',
                        ]
                        
                        for pattern in diff_progress_patterns:
                            diff_progress_match = re.search(pattern, level_diff_content, re.IGNORECASE | re.DOTALL)
                            if diff_progress_match:
                                progress_text = diff_progress_match.group(1)
                                
                                # 초반, 중반, 후반 난이도 추출
                                difficulty_parts = [
                                    ("early", [r'-\s*초반[^:]*:\s*([^\n]+)', r'초반[^:]*:\s*([^\n]+)']),
                                    ("mid", [r'-\s*중반[^:]*:\s*([^\n]+)', r'중반[^:]*:\s*([^\n]+)']),
                                    ("late", [r'-\s*후반[^:]*:\s*([^\n]+)', r'후반[^:]*:\s*([^\n]+)'])
                                ]
                                
                                for part_key, part_patterns in difficulty_parts:
                                    for pattern in part_patterns:
                                        part_match = re.search(pattern, progress_text)
                                        if part_match:
                                            level_info["difficulty"][part_key] = part_match.group(1).strip()
                                            break
                                
                                break
                        
                        # 밸런싱 고려사항 추출
                        balancing_patterns = [
                            r'밸런싱\s*고려사항[^:]*:((?:[^\n]*\n)*?)',
                            r'밸런싱[^:]*:((?:[^\n]*\n)*?)',
                        ]
                        
                        for pattern in balancing_patterns:
                            balancing_match = re.search(pattern, level_diff_content, re.IGNORECASE | re.DOTALL)
                            if balancing_match:
                                balancing_text = balancing_match.group(1)
                                balancing_items = []
                                for line in balancing_text.split('\n'):
                                    line = line.strip()
                                    if line.startswith('-'):
                                        balancing_items.append(line[1:].strip())
                                if balancing_items:
                                    level_info["balancing"] = balancing_items
                                break
                
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
                "relationships": 캐릭터 관계 정보,
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
            
            # 캐릭터 관계 추출
            relationships = self.extract_character_relationships(full_text)
            
            # 레벨 디자인 정보 추출
            levels = self.extract_level_design(full_text)
            
            return {
                "full_text": full_text,
                "core_elements": core_elements,
                "relationships": relationships,
                "levels": levels
            }
        except Exception as e:
            self.logger.error(f"Error during GDD generation: {e}")
            raise
