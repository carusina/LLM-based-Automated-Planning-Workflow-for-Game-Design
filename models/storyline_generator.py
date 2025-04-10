# models/storyline_generator.py
from typing import Dict, List, Any, Optional
from models.llm_service import LLMService
import json

class StorylineGenerator:
    """LLM을 사용하여 게임 스토리라인을 생성하는 클래스"""
    
    def __init__(self, llm_service: LLMService):
        """
        스토리라인 생성기 초기화
        
        Args:
            llm_service: LLM 서비스 인스턴스
        """
        self.llm_service = llm_service
    
    def generate_storyline_outline(self, 
                                  narrative_concept: Dict[str, Any],
                                  num_chapters: int = 5) -> Dict[str, Any]:
        """
        게임 스토리라인의 개요 생성
        
        Args:
            narrative_concept: 게임의 내러티브 컨셉 정보
            num_chapters: 챕터 수 (기본값: 5)
            
        Returns:
            스토리라인 개요 정보
        """
        # 출력 스키마 정의
        output_schema = {
            "title": "스토리 제목",
            "premise": "스토리의 전제/기본 설정",
            "story_arc": "전체적인 스토리 아크 설명",
            "themes": ["핵심 테마 1", "핵심 테마 2"],
            "chapters": [
                {
                    "chapter_number": 1,
                    "title": "챕터 제목",
                    "synopsis": "챕터 개요",
                    "goals": ["플레이어 목표 1", "플레이어 목표 2"],
                    "key_locations": ["주요 위치 1", "주요 위치 2"],
                    "key_events": ["주요 사건 1", "주요 사건 2"],
                    "challenges": ["도전 1", "도전 2"]
                }
            ],
            "main_character_arc": "주인공의 성장 과정",
            "major_plot_points": ["주요 플롯 포인트 1", "주요 플롯 포인트 2"],
            "possible_endings": ["가능한 엔딩 1", "가능한 엔딩 2"]
        }
        
        # 내러티브 정보 추출
        setting = narrative_concept.get('setting', '')
        background_lore = narrative_concept.get('background_lore', '')
        main_plot = narrative_concept.get('main_plot', '')
        themes = narrative_concept.get('themes', [])
        
        # 캐릭터 정보 추출
        characters = narrative_concept.get('characters', [])
        character_info = ""
        for character in characters:
            character_info += f"- {character.get('name', '이름 없음')}: {character.get('role', '')}, {character.get('background', '')}\n"
        
        # 프롬프트 구성
        prompt = f"""다음 게임의 내러티브 컨셉을 바탕으로 상세한 스토리라인 개요를 생성해주세요:

세계관: {setting}

배경 스토리/역사: {background_lore}

주요 스토리라인: {main_plot}

주요 테마: {', '.join(themes)}

주요 캐릭터:
{character_info}

이 게임을 위한 {num_chapters}개의 챕터로 구성된 스토리라인 개요를 작성해주세요. 각 챕터는 명확한 목표, 주요 위치, 핵심 사건, 도전 과제를 포함해야 합니다. 이야기는 플레이어가 게임 플레이를 통해 경험할 수 있는 여정이어야 합니다.

스토리는 명확한 시작, 중간, 끝을 가져야 하며, 플레이어의 선택에 따라 다양한 결말로 이어질 수 있어야 합니다. 캐릭터의 성장과 변화가 스토리 전반에 걸쳐 나타나야 합니다.

창의적이고 몰입감 있는 스토리라인을 개발해주세요."""
        
        # LLM을 사용하여 스토리라인 개요 생성
        # 챕터 수에 맞게 스키마 조정
        chapters = []
        for i in range(1, num_chapters + 1):
            chapters.append({
                "chapter_number": i,
                "title": f"챕터 {i} 제목",
                "synopsis": "챕터 개요",
                "goals": ["플레이어 목표 1", "플레이어 목표 2"],
                "key_locations": ["주요 위치 1", "주요 위치 2"],
                "key_events": ["주요 사건 1", "주요 사건 2"],
                "challenges": ["도전 1", "도전 2"]
            })
        
        output_schema["chapters"] = chapters
        
        return self.llm_service.generate_structured_output(prompt, output_schema)
    
    def generate_chapter_details(self,
                               storyline_outline: Dict[str, Any],
                               chapter_number: int) -> Dict[str, Any]:
        """
        특정 챕터의 상세 내용 생성
        
        Args:
            storyline_outline: 스토리라인 개요 정보
            chapter_number: 챕터 번호
            
        Returns:
            챕터 상세 정보
        """
        # 출력 스키마 정의
        output_schema = {
            "chapter_number": chapter_number,
            "title": "챕터 제목",
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
        
        # 스토리라인 개요에서 필요한 정보 추출
        title = storyline_outline.get('title', '스토리 제목')
        premise = storyline_outline.get('premise', '')
        themes = storyline_outline.get('themes', [])
        
        # 챕터 정보 추출
        chapters = storyline_outline.get('chapters', [])
        target_chapter = None
        
        for chapter in chapters:
            if chapter.get('chapter_number') == chapter_number:
                target_chapter = chapter
                break
        
        if not target_chapter:
            raise ValueError(f"챕터 {chapter_number}를 찾을 수 없습니다.")
        
        chapter_title = target_chapter.get('title', f'챕터 {chapter_number}')
        chapter_synopsis = target_chapter.get('synopsis', '')
        chapter_goals = target_chapter.get('goals', [])
        chapter_locations = target_chapter.get('key_locations', [])
        chapter_events = target_chapter.get('key_events', [])
        chapter_challenges = target_chapter.get('challenges', [])
        
        # 프롬프트 구성
        goals_str = "\n".join([f"- {goal}" for goal in chapter_goals])
        locations_str = "\n".join([f"- {location}" for location in chapter_locations])
        events_str = "\n".join([f"- {event}" for event in chapter_events])
        challenges_str = "\n".join([f"- {challenge}" for challenge in chapter_challenges])
        
        prompt = f"""다음 스토리라인 개요를 바탕으로 챕터 {chapter_number}의 상세 내용을 생성해주세요:

스토리 제목: {title}
스토리 전제: {premise}
주요 테마: {', '.join(themes)}

챕터 제목: {chapter_title}
챕터 개요: {chapter_synopsis}

챕터 목표:
{goals_str}

주요 위치:
{locations_str}

주요 사건:
{events_str}

도전 과제:
{challenges_str}

이 챕터에 대한 상세 내용을 개발해주세요. 플레이어가 경험할 자세한 스토리, 주요 사건, 캐릭터 상호작용, 도전 과제, 선택지, 보상 등을 포함해야 합니다. 게임플레이와 스토리텔링이 자연스럽게 통합될 수 있도록 설계해주세요.

창의적이고 몰입감 있는 챕터 내용을 개발해주세요."""
        
        # LLM을 사용하여 챕터 상세 내용 생성
        return self.llm_service.generate_structured_output(prompt, output_schema)
    
    def generate_character_arcs(self,
                              storyline_outline: Dict[str, Any],
                              narrative_concept: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        스토리라인에 따른 캐릭터 아크 생성
        
        Args:
            storyline_outline: 스토리라인 개요 정보
            narrative_concept: 게임의 내러티브 컨셉 정보
            
        Returns:
            캐릭터 아크 정보 리스트
        """
        # 출력 스키마 정의
        output_schema = {
            "character_arcs": [
                {
                    "name": "캐릭터 이름",
                    "starting_state": "초기 상태/성격",
                    "motivation": "주요 동기",
                    "internal_conflict": "내적 갈등",
                    "external_conflict": "외적 갈등",
                    "development_stages": [
                        {
                            "stage": "발전 단계 이름",
                            "description": "단계 설명",
                            "triggers": "이 변화를 일으키는 사건/요인",
                            "chapter_correlation": "관련 챕터"
                        }
                    ],
                    "relationships": [
                        {
                            "with_character": "관계를 맺는 캐릭터",
                            "initial_state": "초기 관계",
                            "evolution": "관계 발전",
                            "impact_on_story": "스토리에 미치는 영향"
                        }
                    ],
                    "key_decisions": ["중요 결정 1", "중요 결정 2"],
                    "resolution": "아크의 결말",
                    "player_influence": "플레이어가 이 아크에 영향을 미치는 방법"
                }
            ]
        }
        
        # 내러티브 정보에서 캐릭터 추출
        characters = narrative_concept.get('characters', [])
        
        # 스토리라인 정보 추출
        title = storyline_outline.get('title', '스토리 제목')
        premise = storyline_outline.get('premise', '')
        story_arc = storyline_outline.get('story_arc', '')
        themes = storyline_outline.get('themes', [])
        chapters = storyline_outline.get('chapters', [])
        
        # 챕터 정보 문자열 생성
        chapters_str = ""
        for chapter in chapters:
            chapter_num = chapter.get('chapter_number', '')
            chapter_title = chapter.get('title', '')
            chapter_synopsis = chapter.get('synopsis', '')
            chapters_str += f"챕터 {chapter_num}: {chapter_title} - {chapter_synopsis}\n"
        
        # 캐릭터 정보 문자열 생성
        characters_str = ""
        for character in characters:
            name = character.get('name', '이름 없음')
            role = character.get('role', '')
            background = character.get('background', '')
            motivation = character.get('motivation', '')
            arc = character.get('arc', '')
            characters_str += f"캐릭터: {name}\n역할: {role}\n배경: {background}\n동기: {motivation}\n아크: {arc}\n\n"
        
        # 프롬프트 구성
        prompt = f"""다음 스토리라인 개요와 캐릭터 정보를 바탕으로 상세한 캐릭터 아크를 생성해주세요:

스토리 제목: {title}
스토리 전제: {premise}
스토리 아크: {story_arc}
주요 테마: {', '.join(themes)}

챕터 정보:
{chapters_str}

캐릭터 정보:
{characters_str}

각 캐릭터의 상세한 아크를 개발해주세요. 캐릭터의 초기 상태, 동기, 갈등, 발전 단계, 관계, 중요 결정, 결말 등을 포함해야 합니다. 캐릭터의 발전은 게임의 챕터와 연결되어야 하며, 플레이어의 선택이 캐릭터 아크에 어떤 영향을 미칠 수 있는지도 고려해주세요.

모든 캐릭터가 스토리 전반에 걸쳐 의미 있는 발전을 보여주고, 플레이어가 감정적으로 연결될 수 있는 깊이 있는 아크를 개발해주세요."""
        
        # LLM을 사용하여 캐릭터 아크 생성
        response = self.llm_service.generate_structured_output(prompt, output_schema)
        return response.get('character_arcs', [])
    
    def generate_branching_paths(self,
                               storyline_outline: Dict[str, Any],
                               num_branches: int = 3) -> Dict[str, Any]:
        """
        스토리의 분기점과 다양한 경로 생성
        
        Args:
            storyline_outline: 스토리라인 개요 정보
            num_branches: 생성할 분기 수 (기본값: 3)
            
        Returns:
            스토리 분기 정보
        """
        # 출력 스키마 정의
        output_schema = {
            "major_decision_points": [
                {
                    "title": "결정 포인트 제목",
                    "description": "상황 설명",
                    "location": "발생 위치",
                    "chapter_correlation": "관련 챕터",
                    "choices": [
                        {
                            "option": "선택지 설명",
                            "immediate_consequences": "즉각적인 결과",
                            "long_term_effects": ["장기적 영향 1", "장기적 영향 2"],
                            "affected_characters": ["영향 받는 캐릭터 1", "영향 받는 캐릭터 2"],
                            "path_direction": "이 선택이 이끄는 스토리 방향"
                        }
                    ],
                    "gameplay_impact": "게임플레이에 미치는 영향",
                    "narrative_significance": "내러티브적 중요성"
                }
            ],
            "story_branches": [
                {
                    "branch_name": "분기 이름",
                    "trigger": "이 분기를 발생시키는 결정/사건",
                    "synopsis": "분기 시놉시스",
                    "key_events": ["주요 사건 1", "주요 사건 2"],
                    "unique_characters": ["이 분기에만 등장하는 캐릭터 1", "이 분기에만 등장하는 캐릭터 2"],
                    "unique_locations": ["이 분기에만 등장하는 위치 1", "이 분기에만 등장하는 위치 2"],
                    "unique_challenges": ["이 분기에만 등장하는 도전 1", "이 분기에만 등장하는 도전 2"],
                    "ending": "이 분기의 결말"
                }
            ],
            "hidden_paths": [
                {
                    "path_name": "숨겨진 경로 이름",
                    "unlock_condition": "잠금 해제 조건",
                    "content": "숨겨진 내용 설명",
                    "rewards": ["보상 1", "보상 2"]
                }
            ],
            "convergence_points": [
                {
                    "title": "합류 포인트 제목",
                    "description": "다양한 분기가 어떻게 다시 합쳐지는지 설명",
                    "affected_branches": ["영향 받는 분기 1", "영향 받는 분기 2"],
                    "narrative_handling": "내러티브적으로 어떻게 처리되는지"
                }
            ]
        }
        
        # 스토리라인 정보 추출
        title = storyline_outline.get('title', '스토리 제목')
        premise = storyline_outline.get('premise', '')
        story_arc = storyline_outline.get('story_arc', '')
        themes = storyline_outline.get('themes', [])
        chapters = storyline_outline.get('chapters', [])
        major_plot_points = storyline_outline.get('major_plot_points', [])
        possible_endings = storyline_outline.get('possible_endings', [])
        
        # 챕터 정보 문자열 생성
        chapters_str = ""
        for chapter in chapters:
            chapter_num = chapter.get('chapter_number', '')
            chapter_title = chapter.get('title', '')
            chapter_synopsis = chapter.get('synopsis', '')
            chapters_str += f"챕터 {chapter_num}: {chapter_title} - {chapter_synopsis}\n"
        
        # 프롬프트 구성
        prompt = f"""다음 스토리라인 개요를 바탕으로 {num_branches}개의 주요 스토리 분기와 결정 포인트를 생성해주세요:

스토리 제목: {title}
스토리 전제: {premise}
스토리 아크: {story_arc}
주요 테마: {', '.join(themes)}

챕터 정보:
{chapters_str}

주요 플롯 포인트:
{', '.join(major_plot_points)}

가능한 엔딩:
{', '.join(possible_endings)}

플레이어의 선택에 기반한 의미 있는 스토리 분기를 개발해주세요. 각 분기는 게임플레이와 내러티브에 실질적인 영향을 미쳐야 합니다. 결정 포인트는 선택의 중요성을 느낄 수 있도록 충분히 무거운 결과를 가져야 합니다.

또한 숨겨진 경로와 특별한 발견으로 플레이어가 탐험을 통해 추가적인 내용을 발견할 수 있도록 해주세요. 다양한 분기가 어떻게 다시 합쳐지는지, 또는 완전히 다른 결말로 이어지는지도 고려해주세요.

플레이어가 자신의 선택이 게임 세계와 캐릭터에 의미 있는 영향을 미친다고 느낄 수 있는 분기 시스템을 설계해주세요."""
        
        # LLM을 사용하여 스토리 분기 생성
        # 분기 수에 맞게 스키마 조정
        story_branches = []
        for i in range(1, num_branches + 1):
            story_branches.append({
                "branch_name": f"분기 {i}",
                "trigger": "이 분기를 발생시키는 결정/사건",
                "synopsis": "분기 시놉시스",
                "key_events": ["주요 사건 1", "주요 사건 2"],
                "unique_characters": ["이 분기에만 등장하는 캐릭터 1", "이 분기에만 등장하는 캐릭터 2"],
                "unique_locations": ["이 분기에만 등장하는 위치 1", "이 분기에만 등장하는 위치 2"],
                "unique_challenges": ["이 분기에만 등장하는 도전 1", "이 분기에만 등장하는 도전 2"],
                "ending": "이 분기의 결말"
            })
        
        output_schema["story_branches"] = story_branches
        
        return self.llm_service.generate_structured_output(prompt, output_schema)
    
    def generate_dialogue_script(self,
                               character_name: str,
                               scene_description: str,
                               context: Dict[str, Any],
                               dialogue_type: str = "conversation") -> Dict[str, Any]:
        """
        특정 캐릭터나 장면을 위한 대화 스크립트 생성
        
        Args:
            character_name: 캐릭터 이름
            scene_description: 장면 설명
            context: 맥락 정보 (스토리라인, 챕터 정보 등)
            dialogue_type: 대화 유형 (conversation, cinematic, tutorial 등)
            
        Returns:
            대화 스크립트 정보
        """
        # 출력 스키마 정의
        output_schema = {
            "scene_title": "씬 제목",
            "scene_setting": "씬 배경/상황",
            "characters_present": ["등장 캐릭터 1", "등장 캐릭터 2"],
            "tone": "대화의 톤/분위기",
            "script": [
                {
                    "speaker": "화자",
                    "line": "대사",
                    "emotion": "감정/상태",
                    "action": "행동 설명 (선택적)"
                }
            ],
            "player_dialogue_options": [
                {
                    "option_text": "선택지 텍스트",
                    "response": "NPC 응답",
                    "outcome": "이 선택의 결과"
                }
            ],
            "branching_points": ["대화 분기점 1", "대화 분기점 2"],
            "narrative_purpose": "이 대화의 내러티브적 목적",
            "gameplay_integration": "게임플레이와의 통합 방법"
        }
        
        # 맥락 정보 추출
        chapter_info = context.get('chapter_info', {})
        chapter_title = chapter_info.get('title', '')
        chapter_synopsis = chapter_info.get('synopsis', '')
        
        character_info = context.get('character_info', {})
        character_role = character_info.get('role', '')
        character_background = character_info.get('background', '')
        
        # 프롬프트 구성
        prompt = f"""다음 정보를 바탕으로 "{character_name}"이(가) 등장하는 대화 스크립트를 생성해주세요:

캐릭터 정보:
이름: {character_name}
역할: {character_role}
배경: {character_background}

장면 설명:
{scene_description}

챕터 정보:
제목: {chapter_title}
개요: {chapter_synopsis}

대화 유형: {dialogue_type}

자연스럽고 캐릭터의 개성이 드러나는 대화 스크립트를 작성해주세요. 대사는 해당 캐릭터의 성격, 배경, 동기를 반영해야 합니다. 플레이어가 선택할 수 있는 다양한 대화 옵션도 포함해주세요.

대화는 게임플레이 흐름과 자연스럽게 통합되어야 하며, 스토리텔링과 캐릭터 발전에 기여해야 합니다. {dialogue_type} 유형에 적합한 톤과 스타일로 작성해주세요."""
        
        # LLM을 사용하여 대화 스크립트 생성
        return self.llm_service.generate_structured_output(prompt, output_schema)
    
    def generate_complete_storyline(self,
                                  narrative_concept: Dict[str, Any],
                                  num_chapters: int = 5,
                                  num_branches: int = 3) -> Dict[str, Any]:
        """
        완전한 게임 스토리라인 생성
        
        Args:
            narrative_concept: 게임의 내러티브 컨셉 정보
            num_chapters: 챕터 수 (기본값: 5)
            num_branches: 분기 수 (기본값: 3)
            
        Returns:
            완전한 스토리라인 정보
        """
        # 1. 스토리라인 개요 생성
        storyline_outline = self.generate_storyline_outline(
            narrative_concept=narrative_concept,
            num_chapters=num_chapters
        )
        
        # 2. 각 챕터 상세 내용 생성
        chapter_details = []
        for i in range(1, num_chapters + 1):
            chapter_detail = self.generate_chapter_details(
                storyline_outline=storyline_outline,
                chapter_number=i
            )
            chapter_details.append(chapter_detail)
        
        # 3. 캐릭터 아크 생성
        character_arcs = self.generate_character_arcs(
            storyline_outline=storyline_outline,
            narrative_concept=narrative_concept
        )
        
        # 4. 스토리 분기 생성
        story_branches = self.generate_branching_paths(
            storyline_outline=storyline_outline,
            num_branches=num_branches
        )
        
        # 5. 주요 대화 스크립트 생성 (첫 번째 챕터의 첫 번째 등장 캐릭터에 대해)
        sample_dialogue = None
        if narrative_concept.get('characters') and len(narrative_concept.get('characters', [])) > 0:
            main_character = narrative_concept['characters'][0]
            character_name = main_character.get('name', '주인공')
            
            # 첫 번째 챕터 정보 가져오기
            first_chapter = next((chapter for chapter in storyline_outline.get('chapters', []) if chapter.get('chapter_number') == 1), {})
            
            if first_chapter:
                context = {
                    'chapter_info': first_chapter,
                    'character_info': main_character
                }
                
                sample_dialogue = self.generate_dialogue_script(
                    character_name=character_name,
                    scene_description=f"{first_chapter.get('title', '첫 번째 챕터')}의 오프닝 씬",
                    context=context,
                    dialogue_type="introduction"
                )
        
        # 모든 정보 결합
        complete_storyline = {
            "title": storyline_outline.get("title", "스토리 제목"),
            "premise": storyline_outline.get("premise", ""),
            "story_arc": storyline_outline.get("story_arc", ""),
            "themes": storyline_outline.get("themes", []),
            "chapter_outlines": storyline_outline.get("chapters", []),
            "chapter_details": chapter_details,
            "character_arcs": character_arcs,
            "story_branches": story_branches,
            "major_plot_points": storyline_outline.get("major_plot_points", []),
            "possible_endings": storyline_outline.get("possible_endings", [])
        }
        
        # 샘플 대화가 있는 경우 추가
        if sample_dialogue:
            complete_storyline["sample_dialogue"] = sample_dialogue
        
        return complete_storyline