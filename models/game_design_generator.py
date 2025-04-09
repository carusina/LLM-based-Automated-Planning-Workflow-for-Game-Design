# models/game_design_generator.py
from typing import Dict, List, Any, Optional, Union
from models.llm_service import LLMService
import json

class GameDesignGenerator:
    """LLM을 사용하여 게임 기획 요소를 생성하는 클래스"""
    
    def __init__(self, llm_service: LLMService):
        """
        게임 기획 생성기 초기화
        
        Args:
            llm_service: LLM 서비스 인스턴스
        """
        self.llm_service = llm_service
        
    def generate_game_concept(self, 
                             initial_concept: str, 
                             genre: str = None, 
                             target_audience: str = None) -> Dict[str, Any]:
        """
        게임 컨셉을 생성하거나 개선
        
        Args:
            initial_concept: 초기 게임 컨셉 아이디어
            genre: 게임 장르 (선택 사항)
            target_audience: 타겟 사용자층 (선택 사항)
            
        Returns:
            확장된 게임 컨셉 정보
        """
        # 출력 스키마 정의
        output_schema = {
            "title": "게임 제목",
            "high_concept": "한 줄 설명",
            "extended_concept": "확장된 개념 설명 (3-5문장)",
            "unique_selling_points": ["차별화 포인트 1", "차별화 포인트 2"],
            "target_audience": "타겟 사용자층",
            "genre": "주요 장르",
            "subgenres": ["서브 장르 1", "서브 장르 2"],
            "mood": "게임의 분위기/감성",
            "visual_style": "시각적 스타일 설명"
        }
        
        # 프롬프트 구성
        prompt_parts = [
            "다음 초기 게임 컨셉을 바탕으로 확장된 게임 컨셉 정보를 생성해주세요:",
            f"초기 컨셉: {initial_concept}"
        ]
        
        if genre:
            prompt_parts.append(f"장르: {genre}")
        
        if target_audience:
            prompt_parts.append(f"타겟 사용자층: {target_audience}")
        
        prompt_parts.append("\n창의적이고 독창적인 게임 컨셉을 개발해주세요. 기존 게임들과 차별화된 요소를 포함하되, 실현 가능한 범위 내에서 제안해주세요.")
        
        prompt = "\n".join(prompt_parts)
        
        # LLM을 사용하여 게임 컨셉 생성
        return self.llm_service.generate_structured_output(prompt, output_schema)
    
    def generate_gameplay_mechanics(self, 
                                   game_concept: Dict[str, Any], 
                                   complexity_level: str = "중간") -> Dict[str, Any]:
        """
        게임 플레이 메커니즘 생성
        
        Args:
            game_concept: 게임 컨셉 정보
            complexity_level: 게임플레이 복잡도 수준 ("낮음", "중간", "높음")
            
        Returns:
            게임플레이 메커니즘 정보
        """
        # 출력 스키마 정의
        output_schema = {
            "core_gameplay_loop": "핵심 게임플레이 루프 설명",
            "player_actions": ["주요 플레이어 액션 1", "주요 플레이어 액션 2"],
            "progression_system": "게임 진행/성장 시스템 설명",
            "challenge_types": ["도전 유형 1", "도전 유형 2"],
            "reward_systems": ["보상 시스템 1", "보상 시스템 2"],
            "game_modes": ["게임 모드 1", "게임 모드 2"],
            "controls": "조작 방식 설명",
            "unique_mechanics": ["독특한 메커닉 1", "독특한 메커닉 2"],
            "complexity_assessment": "복잡도 평가 및 접근성"
        }
        
        # 게임 컨셉에서 필요한 정보 추출
        concept_str = f"게임 제목: {game_concept.get('title', '제목 미정')}\n"
        concept_str += f"컨셉: {game_concept.get('high_concept', '')}\n"
        concept_str += f"장르: {game_concept.get('genre', '')}\n"
        concept_str += f"타겟 사용자층: {game_concept.get('target_audience', '')}"
        
        # 프롬프트 구성
        prompt = f"""다음 게임 컨셉을 바탕으로 게임플레이 메커니즘을 개발해주세요:

{concept_str}

복잡도 수준: {complexity_level}

게임 메커니즘은 다음 요소를 포함해야 합니다:
1. 핵심 게임플레이 루프 - 플레이어가 반복적으로 수행하는 핵심 활동
2. 주요 플레이어 액션 - 플레이어가 수행할 수 있는 주요 행동들
3. 진행/성장 시스템 - 플레이어 또는 캐릭터의 성장 방식
4. 도전 요소 - 플레이어가 극복해야 할 도전 과제들
5. 보상 시스템 - 플레이어에게 제공되는 보상 방식
6. 게임 모드 - 다양한 플레이 방식 (싱글플레이어, 멀티플레이어 등)
7. 조작 방식 - 플레이어의 입력 방식
8. 독특한 메커닉 - 이 게임만의 차별화된 게임플레이 요소

해당 장르의 관습을 참고하되, 창의적이고 혁신적인 요소를 포함하세요. 플레이어 경험을 최우선으로 고려하여 재미있고 매력적인 게임플레이를 설계해주세요."""
        
        # LLM을 사용하여 게임플레이 메커니즘 생성
        return self.llm_service.generate_structured_output(prompt, output_schema)
    
    def generate_narrative_elements(self, 
                                  game_concept: Dict[str, Any],
                                  gameplay_mechanics: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        게임의 내러티브 요소 생성
        
        Args:
            game_concept: 게임 컨셉 정보
            gameplay_mechanics: 게임플레이 메커니즘 정보 (선택 사항)
            
        Returns:
            내러티브 요소 정보
        """
        # 출력 스키마 정의
        output_schema = {
            "setting": "게임 세계관 설명",
            "background_lore": "배경 스토리/역사",
            "main_plot": "주요 스토리 라인",
            "plot_structure": "스토리 구조 (3막 구조 등)",
            "themes": ["주요 테마 1", "주요 테마 2"],
            "characters": [
                {
                    "name": "캐릭터명",
                    "role": "역할",
                    "background": "배경",
                    "motivation": "동기",
                    "arc": "캐릭터 아크"
                }
            ],
            "narrative_devices": ["내러티브 장치 1", "내러티브 장치 2"],
            "player_agency": "플레이어의 선택/분기점",
            "integration_with_gameplay": "게임플레이와 내러티브 통합 방식"
        }
        
        # 게임 컨셉에서 필요한 정보 추출
        concept_str = f"게임 제목: {game_concept.get('title', '제목 미정')}\n"
        concept_str += f"컨셉: {game_concept.get('high_concept', '')}\n"
        concept_str += f"장르: {game_concept.get('genre', '')}\n"
        concept_str += f"분위기: {game_concept.get('mood', '')}"
        
        # 게임플레이 메커니즘 정보가 있으면 추가
        mechanics_str = ""
        if gameplay_mechanics:
            mechanics_str = f"\n\n게임플레이 메커니즘:\n"
            mechanics_str += f"- 핵심 루프: {gameplay_mechanics.get('core_gameplay_loop', '')}\n"
            mechanics_str += f"- 진행 시스템: {gameplay_mechanics.get('progression_system', '')}"
        
        # 프롬프트 구성
        prompt = f"""다음 게임 컨셉을 바탕으로 매력적인 내러티브 요소를 개발해주세요:

{concept_str}{mechanics_str}

다음 요소를 포함한 풍부하고 몰입감 있는 내러티브를 설계해주세요:
1. 세계관과 배경 - 게임이 펼쳐지는 세계의 설정
2. 주요 스토리 라인 - 게임의 전체적인 이야기 흐름
3. 캐릭터 - 주요 캐릭터들의 배경, 동기, 성장 과정
4. 주요 테마 - 게임이 탐구하는 핵심 주제
5. 내러티브 장치 - 스토리텔링을 위한 방법론
6. 플레이어 선택 - 플레이어가 스토리에 영향을 미치는 방식

게임플레이와 내러티브 간의 조화를 고려하되, 장르에 적합한 내러티브를 구성해주세요. 플레이어가 스토리에 몰입할 수 있도록 매력적이고 흥미로운 내러티브를 제안해주세요."""
        
        # LLM을 사용하여 내러티브 요소 생성
        return self.llm_service.generate_structured_output(prompt, output_schema)
    
    def generate_art_direction(self, 
                             game_concept: Dict[str, Any],
                             narrative_elements: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        게임의 아트 디렉션 생성
        
        Args:
            game_concept: 게임 컨셉 정보
            narrative_elements: 내러티브 요소 정보 (선택 사항)
            
        Returns:
            아트 디렉션 정보
        """
        # 출력 스키마 정의
        output_schema = {
            "visual_style": "시각적 스타일 (사실적, 스타일라이즈드, 픽셀 아트 등)",
            "color_palette": "주요 색상 팔레트 설명",
            "art_references": ["참고할 수 있는 아트 스타일/작품 1", "참고할 수 있는 아트 스타일/작품 2"],
            "character_design": "캐릭터 디자인 방향",
            "environment_design": "환경 디자인 방향",
            "ui_design": "UI 디자인 방향",
            "animation_style": "애니메이션 스타일",
            "lighting": "조명 방식",
            "sound_design": "사운드 디자인 방향",
            "music_direction": "음악 방향"
        }
        
        # 게임 컨셉에서 필요한 정보 추출
        concept_str = f"게임 제목: {game_concept.get('title', '제목 미정')}\n"
        concept_str += f"컨셉: {game_concept.get('high_concept', '')}\n"
        concept_str += f"장르: {game_concept.get('genre', '')}\n"
        concept_str += f"분위기: {game_concept.get('mood', '')}\n"
        concept_str += f"시각적 스타일: {game_concept.get('visual_style', '')}"
        
        # 내러티브 요소 정보가 있으면 추가
        narrative_str = ""
        if narrative_elements:
            narrative_str = f"\n\n내러티브 요소:\n"
            narrative_str += f"- 세계관: {narrative_elements.get('setting', '')}\n"
            narrative_str += f"- 테마: {', '.join(narrative_elements.get('themes', []))}"
        
        # 프롬프트 구성
        prompt = f"""다음 게임 컨셉을 바탕으로 아트 디렉션을 개발해주세요:

{concept_str}{narrative_str}

다음 요소를 포함한 일관되고 매력적인 아트 디렉션을 설계해주세요:
1. 시각적 스타일 - 전반적인 그래픽 스타일 (사실적, 스타일라이즈드, 픽셀 아트 등)
2. 색상 팔레트 - 주요 색상과 그 의미/목적
3. 참고 자료 - 영감을 얻을 수 있는 아트 스타일이나 작품
4. 캐릭터 디자인 - 캐릭터의 시각적 스타일 방향
5. 환경 디자인 - 게임 세계의 환경 디자인 방향
6. UI 디자인 - 사용자 인터페이스 디자인 방향
7. 애니메이션과 이펙트 - 움직임과 시각 효과 스타일
8. 사운드와 음악 - 오디오 요소 방향

게임의 분위기와 내러티브에 부합하면서도 기술적 제약을 고려한 아트 디렉션을 제안해주세요. 시각적 일관성과 독창성을 갖춘 스타일을 개발해주세요."""
        
        # LLM을 사용하여 아트 디렉션 생성
        return self.llm_service.generate_structured_output(prompt, output_schema)
    
    def generate_technical_specs(self, 
                               game_concept: Dict[str, Any],
                               gameplay_mechanics: Dict[str, Any] = None,
                               art_direction: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        게임의 기술 사양 생성
        
        Args:
            game_concept: 게임 컨셉 정보
            gameplay_mechanics: 게임플레이 메커니즘 정보 (선택 사항)
            art_direction: 아트 디렉션 정보 (선택 사항)
            
        Returns:
            기술 사양 정보
        """
        # 출력 스키마 정의
        output_schema = {
            "target_platforms": ["타겟 플랫폼 1", "타겟 플랫폼 2"],
            "minimum_specs": "최소 사양",
            "recommended_specs": "권장 사양",
            "engine": "게임 엔진 추천",
            "key_technologies": ["핵심 기술 1", "핵심 기술 2"],
            "networking": "네트워킹 요구사항 (멀티플레이어의 경우)",
            "performance_targets": "성능 목표 (FPS, 해상도 등)",
            "development_challenges": ["예상 기술적 도전 1", "예상 기술적 도전 2"],
            "asset_requirements": "에셋 요구사항",
            "estimated_development_resources": "예상 개발 리소스 (인력, 시간 등)"
        }
        
        # 게임 컨셉에서 필요한 정보 추출
        concept_str = f"게임 제목: {game_concept.get('title', '제목 미정')}\n"
        concept_str += f"컨셉: {game_concept.get('high_concept', '')}\n"
        concept_str += f"장르: {game_concept.get('genre', '')}"
        
        # 게임플레이 메커니즘 정보가 있으면 추가
        mechanics_str = ""
        if gameplay_mechanics:
            mechanics_str = f"\n\n게임플레이 메커니즘:\n"
            mechanics_str += f"- 핵심 루프: {gameplay_mechanics.get('core_gameplay_loop', '')}\n"
            mechanics_str += f"- 게임 모드: {', '.join(gameplay_mechanics.get('game_modes', []))}"
        
        # 아트 디렉션 정보가 있으면 추가
        art_str = ""
        if art_direction:
            art_str = f"\n\n아트 디렉션:\n"
            art_str += f"- 시각적 스타일: {art_direction.get('visual_style', '')}\n"
            art_str += f"- 애니메이션 스타일: {art_direction.get('animation_style', '')}"
        
        # 프롬프트 구성
        prompt = f"""다음 게임 컨셉을 바탕으로 기술 사양을 개발해주세요:

{concept_str}{mechanics_str}{art_str}

다음 요소를 포함한 현실적이고 구체적인 기술 사양을 제안해주세요:
1. 타겟 플랫폼 - 게임이 출시될 플랫폼
2. 시스템 요구사항 - 최소 및 권장 사양
3. 게임 엔진 - 적합한 게임 엔진 추천
4. 핵심 기술 - 게임 구현에 필요한 핵심 기술
5. 네트워킹 요구사항 - 멀티플레이어 게임의 경우
6. 성능 목표 - 프레임레이트, 해상도 등
7. 개발 도전 과제 - 예상되는 기술적 어려움
8. 개발 리소스 - 필요한 인력, 시간, 비용 추정

현재 게임 개발 기술 트렌드와 제약을 고려하여 실현 가능한 기술 사양을 제시해주세요."""
        
        # LLM을 사용하여 기술 사양 생성
        return self.llm_service.generate_structured_output(prompt, output_schema)
    
    def generate_monetization_plan(self, 
                                 game_concept: Dict[str, Any],
                                 gameplay_mechanics: Dict[str, Any] = None,
                                 target_audience: str = None) -> Dict[str, Any]:
        """
        게임의 수익화 계획 생성
        
        Args:
            game_concept: 게임 컨셉 정보
            gameplay_mechanics: 게임플레이 메커니즘 정보 (선택 사항)
            target_audience: 타겟 사용자층 (선택 사항)
            
        Returns:
            수익화 계획 정보
        """
        # 출력 스키마 정의
        output_schema = {
            "monetization_model": "주요 수익화 모델 (프리미엄, F2P, 구독 등)",
            "price_point": "가격 책정 (프리미엄의 경우)",
            "in_app_purchases": "인앱 구매 항목 및 가격 전략",
            "virtual_currency": "가상 화폐 시스템 (있는 경우)",
            "battle_pass": "배틀패스/시즌패스 구조 (있는 경우)",
            "advertising": "광고 전략 (있는 경우)",
            "dlc_expansion": "DLC/확장팩 계획",
            "subscription": "구독 모델 세부사항 (있는 경우)",
            "player_retention_strategies": ["플레이어 유지 전략 1", "플레이어 유지 전략 2"],
            "revenue_projections": "수익 예상 (대략적인 추정)",
            "market_analysis": "시장 분석 및 경쟁 수익화 모델 비교"
        }
        
        # 게임 컨셉에서 필요한 정보 추출
        concept_str = f"게임 제목: {game_concept.get('title', '제목 미정')}\n"
        concept_str += f"컨셉: {game_concept.get('high_concept', '')}\n"
        concept_str += f"장르: {game_concept.get('genre', '')}"
        
        if target_audience:
            concept_str += f"\n타겟 사용자층: {target_audience}"
        elif 'target_audience' in game_concept:
            concept_str += f"\n타겟 사용자층: {game_concept['target_audience']}"
        
        # 게임플레이 메커니즘 정보가 있으면 추가
        mechanics_str = ""
        if gameplay_mechanics:
            mechanics_str = f"\n\n게임플레이 메커니즘:\n"
            mechanics_str += f"- 핵심 루프: {gameplay_mechanics.get('core_gameplay_loop', '')}\n"
            mechanics_str += f"- 진행 시스템: {gameplay_mechanics.get('progression_system', '')}\n"
            mechanics_str += f"- 보상 시스템: {', '.join(gameplay_mechanics.get('reward_systems', []))}"
        
        # 프롬프트 구성
        prompt = f"""다음 게임 컨셉을 바탕으로 수익화 계획을 개발해주세요:

{concept_str}{mechanics_str}

다음 요소를 포함한 현실적이고 지속 가능한 수익화 계획을 제안해주세요:
1. 수익화 모델 - 주요 수익화 방식 (프리미엄, F2P, 구독 등)
2. 가격 책정 - 적정 가격대 또는 인앱 구매 전략
3. 추가 수익원 - DLC, 확장팩, 시즌패스 등
4. 플레이어 유지 전략 - 장기적인 참여와 수익을 위한 전략
5. 시장 분석 - 경쟁작들의 수익화 모델과 비교

게임 경험을 저해하지 않으면서도 지속 가능한 수익을 창출할 수 있는 균형 잡힌 접근법을 제시해주세요. 타겟 사용자층의 특성과 선호도를 고려한 수익화 전략을 개발해주세요."""
        
        # LLM을 사용하여 수익화 계획 생성
        return self.llm_service.generate_structured_output(prompt, output_schema)
    
    def generate_development_roadmap(self, 
                                   game_concept: Dict[str, Any],
                                   technical_specs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        게임 개발 로드맵 생성
        
        Args:
            game_concept: 게임 컨셉 정보
            technical_specs: 기술 사양 정보 (선택 사항)
            
        Returns:
            개발 로드맵 정보
        """
        # 출력 스키마 정의
        output_schema = {
            "development_timeline": {
                "pre_production": "사전 제작 단계 (기간 및 주요 마일스톤)",
                "prototype": "프로토타입 단계 (기간 및 주요 마일스톤)",
                "production": "본 제작 단계 (기간 및 주요 마일스톤)",
                "alpha": "알파 단계 (기간 및 주요 마일스톤)",
                "beta": "베타 단계 (기간 및 주요 마일스톤)",
                "gold": "골드 마스터 (기간 및 주요 마일스톤)",
                "post_launch": "출시 후 지원 (기간 및 주요 마일스톤)"
            },
            "team_structure": {
                "core_team": ["핵심 팀원 역할 1", "핵심 팀원 역할 2"],
                "expanded_team": ["확장 팀원 역할 1", "확장 팀원 역할 2"],
                "outsourcing": ["외주 영역 1", "외주 영역 2"]
            },
            "budget_estimate": "예상 개발 예산 범위",
            "risk_assessment": ["주요 리스크 1", "주요 리스크 2"],
            "testing_plan": "테스트 계획 개요",
            "marketing_timeline": "마케팅 타임라인 개요",
            "key_deliverables": ["주요 산출물 1", "주요 산출물 2"],
            "success_metrics": ["성공 지표 1", "성공 지표 2"]
        }
        
        # 게임 컨셉에서 필요한 정보 추출
        concept_str = f"게임 제목: {game_concept.get('title', '제목 미정')}\n"
        concept_str += f"컨셉: {game_concept.get('high_concept', '')}\n"
        concept_str += f"장르: {game_concept.get('genre', '')}"
        
        # 기술 사양 정보가 있으면 추가
        tech_str = ""
        if technical_specs:
            tech_str = f"\n\n기술 사양:\n"
            tech_str += f"- 타겟 플랫폼: {', '.join(technical_specs.get('target_platforms', []))}\n"
            tech_str += f"- 게임 엔진: {technical_specs.get('engine', '')}\n"
            tech_str += f"- 개발 도전 과제: {', '.join(technical_specs.get('development_challenges', []))}"
        
        # 프롬프트 구성
        prompt = f"""다음 게임 컨셉을 바탕으로 개발 로드맵을 설계해주세요:

{concept_str}{tech_str}

다음 요소를 포함한 현실적이고 상세한 개발 로드맵을 제안해주세요:
1. 개발 타임라인 - 사전 제작부터 출시 후 지원까지의 단계별 일정
2. 팀 구성 - 필요한 팀원 역할 및 구조
3. 예산 추정 - 대략적인 개발 예산 범위
4. 리스크 평가 - 주요 개발 리스크 및 대응 전략
5. 테스트 계획 - QA 및 사용자 테스트 접근법
6. 마케팅 타임라인 - 주요 마케팅 활동 및 일정
7. 성공 지표 - 게임의 성공을 측정할 주요 지표

이 규모와 장르의 게임 개발에 대한 현실적인 이해를 바탕으로 실행 가능한 로드맵을 제시해주세요. 인디 스튜디오부터 중소규모 개발사까지 다양한 개발 환경을 고려하여 조정 가능한 계획을 제안해주세요."""
        
        # LLM을 사용하여 개발 로드맵 생성
        return self.llm_service.generate_structured_output(prompt, output_schema)
    
    def analyze_competitor(self, competitor_name: str) -> Dict[str, Any]:
        """
        경쟁 게임 분석
        
        Args:
            competitor_name: 분석할 경쟁 게임 이름
            
        Returns:
            경쟁 게임 분석 정보
        """
        # 출력 스키마 정의
        output_schema = {
            "game_name": "게임 이름",
            "developer": "개발사",
            "publisher": "퍼블리셔",
            "release_date": "출시일",
            "platforms": ["플랫폼 1", "플랫폼 2"],
            "genre": "장르",
            "target_audience": "타겟 사용자층",
            "key_features": ["주요 특징 1", "주요 특징 2"],
            "gameplay_analysis": "게임플레이 분석",
            "narrative_analysis": "내러티브 분석",
            "art_style_analysis": "아트 스타일 분석",
            "monetization_model": "수익화 모델",
            "reception": {
                "critic_score": "평론가 점수 (예: 메타크리틱)",
                "user_score": "사용자 평점",
                "sales_performance": "판매 실적 (가능한 경우)"
            },
            "strengths": ["강점 1", "강점 2"],
            "weaknesses": ["약점 1", "약점 2"],
            "lessons": ["배울 점 1", "배울 점 2"]
        }
        
        # 프롬프트 구성
        prompt = f"""다음 게임에 대한 상세한 경쟁 분석을 제공해주세요:

게임 이름: {competitor_name}

다음 요소를 포함한 철저하고 객관적인 분석을 수행해주세요:
1. 게임 기본 정보 - 개발사, 퍼블리셔, 출시일, 플랫폼, 장르
2. 주요 특징 - 게임의 핵심 기능 및 판매 포인트
3. 게임플레이 분석 - 핵심 메커니즘, 난이도, 재미 요소
4. 내러티브 분석 - 스토리텔링 접근법과 효과
5. 아트 스타일 분석 - 시각적 디자인과 기술적 구현
6. 수익화 모델 - 비즈니스 모델 및 수익 전략
7. 시장 반응 - 비평가 및 사용자 평가, 판매 실적
8. 강점과 약점 - 주목할 만한 성공 요소와 개선이 필요한 영역
9. 배울 점 - 이 게임에서 얻을 수 있는 주요 교훈

이 분석은 실제 게임 개발에 도움이 될 수 있도록 구체적이고 actionable한 인사이트를 제공해야 합니다. 객관적이고 균형 잡힌 평가를 제공해주세요."""
        
        # LLM을 사용하여 경쟁 게임 분석 생성
        return self.llm_service.generate_structured_output(prompt, output_schema)
    
    def generate_specific_content(self, content_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        특정 게임 콘텐츠 생성
        
        Args:
            content_type: 생성할 콘텐츠 유형 (character, level, item, quest 등)
            parameters: 콘텐츠 생성을 위한 매개변수
            
        Returns:
            생성된 콘텐츠 정보
        """
        # 콘텐츠 유형에 따른 출력 스키마 정의
        output_schemas = {
            "character": {
                "name": "캐릭터 이름",
                "role": "역할 (플레이어 캐릭터, NPC, 적 등)",
                "background": "배경 이야기",
                "personality": "성격 특성",
                "appearance": "외형 설명",
                "abilities": ["능력 1", "능력 2"],
                "stats": {
                    "strength": "힘 수치/설명",
                    "agility": "민첩 수치/설명",
                    "intelligence": "지능 수치/설명",
                    "other_stats": "기타 스탯"
                },
                "relationships": "다른 캐릭터와의 관계",
                "arc": "캐릭터 아크/성장",
                "gameplay_role": "게임플레이 역할",
                "dialogue_examples": ["대화 예시 1", "대화 예시 2"]
            },
            "level": {
                "name": "레벨 이름",
                "theme": "테마/분위기",
                "objective": "목표/미션",
                "layout": "레이아웃 설명",
                "environments": ["환경 요소 1", "환경 요소 2"],
                "challenges": ["도전 요소 1", "도전 요소 2"],
                "enemies": ["적 유형 1", "적 유형 2"],
                "puzzles": ["퍼즐 요소 1", "퍼즐 요소 2"],
                "rewards": ["보상 1", "보상 2"],
                "narrative_elements": "내러티브 요소",
                "music_atmosphere": "음악 및 분위기",
                "player_progression": "플레이어 진행/성장 요소"
            },
            "item": {
                "name": "아이템 이름",
                "type": "아이템 유형 (무기, 방어구, 소모품 등)",
                "rarity": "희귀도",
                "description": "설명",
                "appearance": "외형",
                "stats": "능력치/효과",
                "usage": "사용 방법",
                "acquisition": "획득 방법",
                "lore": "아이템 배경 이야기",
                "upgrade_path": "업그레이드 경로 (있는 경우)",
                "value": "가치/가격"
            },
            "quest": {
                "title": "퀘스트 제목",
                "type": "퀘스트 유형 (메인, 사이드, 반복 등)",
                "giver": "퀘스트 제공자",
                "location": "위치",
                "description": "설명",
                "objectives": ["목표 1", "목표 2"],
                "narrative": "내러티브 요소",
                "dialogue": "대화 내용",
                "challenges": ["도전 요소 1", "도전 요소 2"],
                "rewards": ["보상 1", "보상 2"],
                "consequences": "선택과 결과",
                "related_quests": "관련 퀘스트"
            }
        }
        
        # 지원되는 콘텐츠 유형 확인
        if content_type.lower() not in output_schemas:
            raise ValueError(f"지원되지 않는 콘텐츠 유형: {content_type}")
        
        # 출력 스키마 선택
        output_schema = output_schemas[content_type.lower()]
        
        # 매개변수 문자열 생성
        params_str = "\n".join([f"{key}: {value}" for key, value in parameters.items()])
        
        # 프롬프트 구성
        prompt = f"""{content_type.capitalize()} 콘텐츠를 다음 매개변수를 바탕으로 생성해주세요:

{params_str}

창의적이고 독창적인 {content_type} 콘텐츠를 개발해주세요. 게임 내에서 매력적이고 기억에 남을 요소가 될 수 있도록 충분한 세부 사항과 독특한 특징을 포함해주세요."""
        
        # LLM을 사용하여 특정 콘텐츠 생성
        return self.llm_service.generate_structured_output(prompt, output_schema)
    
    def refine_design(self, current_design: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """
        기존 게임 기획 개선
        
        Args:
            current_design: 현재 게임 기획 정보
            feedback: 개선을 위한 피드백
            
        Returns:
            개선된 게임 기획 정보
        """
        # 현재 기획을 JSON 문자열로 변환
        current_design_str = json.dumps(current_design, ensure_ascii=False, indent=2)
        
        # 프롬프트 구성
        prompt = f"""다음은 현재 게임 기획 문서입니다:

{current_design_str}

다음 피드백을 바탕으로 이 게임 기획을 개선해주세요:

{feedback}

기존 구조를 유지하면서 피드백을 반영한 개선된 게임 기획을 제공해주세요. 변경 사항을 분명하게 적용하고, 기획의 일관성을 유지해주세요."""
        
        # LLM을 사용하여 기획 개선
        # 원래 기획과 동일한 구조를 유지하기 위해 현재 디자인을 출력 스키마로 사용
        return self.llm_service.generate_structured_output(prompt, current_design)
    
    def generate_complete_design(self,
                                game_concept: str,
                                target_audience: str = "일반 게이머",
                                genre: str = "미정", 
                                platform: str = "PC",
                                gameplay_mechanics: List[str] = None,
                                art_style: str = "",
                                story_elements: Dict[str, Any] = None,
                                competitive_analysis: List[str] = None) -> Dict[str, Any]:
        """
        완전한 게임 기획서 생성
        
        Args:
            game_concept: 게임 컨셉
            target_audience: 타겟 사용자층
            genre: 게임 장르
            platform: 타겟 플랫폼
            gameplay_mechanics: 게임플레이 메커니즘 목록 (선택 사항)
            art_style: 아트 스타일 (선택 사항)
            story_elements: 스토리 요소 (선택 사항)
            competitive_analysis: 경쟁 게임 분석 (선택 사항)
            
        Returns:
            완전한 게임 기획 정보
        """
        # 1. 게임 컨셉 생성
        concept_info = self.generate_game_concept(
            initial_concept=game_concept,
            genre=genre,
            target_audience=target_audience
        )
        
        # 2. 게임플레이 메커니즘 생성
        gameplay_info = self.generate_gameplay_mechanics(
            game_concept=concept_info,
            complexity_level="중간"
        )
        
        # 3. 내러티브 요소 생성
        narrative_info = self.generate_narrative_elements(
            game_concept=concept_info,
            gameplay_mechanics=gameplay_info
        )
        
        # 4. 아트 디렉션 생성
        art_info = self.generate_art_direction(
            game_concept=concept_info,
            narrative_elements=narrative_info
        )
        
        # 5. 기술 사양 생성
        tech_info = self.generate_technical_specs(
            game_concept=concept_info,
            gameplay_mechanics=gameplay_info,
            art_direction=art_info
        )
        
        # 6. 수익화 계획 생성
        monetization_info = self.generate_monetization_plan(
            game_concept=concept_info,
            gameplay_mechanics=gameplay_info,
            target_audience=target_audience
        )
        
        # 7. 개발 로드맵 생성
        roadmap_info = self.generate_development_roadmap(
            game_concept=concept_info,
            technical_specs=tech_info
        )
        
        # 8. 경쟁 분석 (competitive_analysis가 제공된 경우)
        competition_info = {}
        if competitive_analysis and len(competitive_analysis) > 0:
            competition_info["competitors"] = []
            for competitor in competitive_analysis[:2]:  # 최대 2개까지만 분석
                competitor_info = self.analyze_competitor(competitor)
                competition_info["competitors"].append(competitor_info)
        
        # 모든 정보 결합
        complete_design = {
            "game_title": concept_info.get("title", "게임 제목 미정"),
            "high_concept": concept_info.get("high_concept", ""),
            "target_audience": target_audience,
            "genre": concept_info.get("genre", genre),
            "platform": platform,
            "concept_details": concept_info,
            "gameplay": gameplay_info,
            "narrative": narrative_info,
            "art_direction": art_info,
            "technical_specs": tech_info,
            "monetization": monetization_info,
            "development_roadmap": roadmap_info
        }
        
        if competition_info:
            complete_design["competition_analysis"] = competition_info
        
        return complete_design