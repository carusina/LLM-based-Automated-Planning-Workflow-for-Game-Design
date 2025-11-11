"""
game_design_generator.py

Game Design Document (GDD) 생성 모듈
- 템플릿을 기반으로 프롬프트 구성
- LLM을 사용하여 완성된 GDD 생성
"""

import os
import json
import logging
import re
from typing import Dict, List, Any

from .llm_service import LLMService

class GameDesignGenerator:
    """
    게임 디자인 문서(GDD) 생성
    """

    def __init__(
        self,
        llm_service: LLMService = None,
        template_dir: str = None
    ) -> None:
        self.llm = llm_service or LLMService()
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.template_dir = template_dir or os.path.join(base_dir, 'templates')
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Template directory set to: {self.template_dir}")

    def load_template(self) -> str:
        template_path = os.path.join(self.template_dir, 'GDD.md')
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()

    def build_prompt(self, idea: str, genre: str, target: str, concept: str) -> str:
        template = self.load_template()
        # 프롬프트 구성은 기존과 동일하게 유지
        relationship_example = """
        * Main Characters & Relationships:
        - 아레스 (플레이어): 고대 드래곤 '이그니스'의 피를 이어받은 마지막 용기사. 정의감이 강하고 동료를 아끼는 성격. 점차 드래곤의 힘을 각성하며 왕국의 구원자로 성장한다. 플레이어와의 관계: 자신 (자기 자신을 조종)
        - 리아나: 엘드리안 왕국의 마지막 마법사 길드의 후예. 고대 마법에 능통하며, 아레스에게 유물에 대한 단서와 마법적 지원을 제공한다. 지적이고 냉철하지만, 내면에는 왕국을 향한 뜨거운 충정심을 품고 있다. 플레이어와의 관계: 신뢰
        - 카이로스: 과거 왕국의 영웅이었으나, 타락한 왕국의 현실에 절망하여 은둔한 전사. 처음에는 아레스를 경계하지만, 그의 의지를 보고 다시금 검을 든다. 거친 외모와 달리 따뜻한 마음을 지녔다. 플레이어와의 관계: 우호적
        - 벨리알: 왕국을 타락시킨 장본인이자, 어둠의 세력을 이끄는 마왕. 고대 드래곤의 힘을 탐하며 왕국을 자신의 지배 아래 두려 한다. 막강한 힘과 교활한 지략을 겸비했다. 플레이어와의 관계: 증오"""
        level_example = """
        9. Level Design
        1. Level List & Unique Features
        *   Level Name: 엘드리안 왕성 지하 감옥
        *   Theme & Background Story:
            벨리알의 그림자에 잠식된 엘드리안 왕국의 심장부. 과거 왕국의 영광을 상징하던 왕성이 지금은 어둠의 세력에게 점령당해 고통받는 이들을 가두는 감옥으로 전락했다. 지하 깊은 곳에는 금지된 고대 실험의 흔적과 첫 번째 드라콘 아르카나 조각이 숨겨져 있다는 소문이 있다.
        *   Atmosphere & Art Direction: 어둡고 습한 돌감옥, 녹슨 철창, 핏자국, 벽에 새겨진 고통받는 영혼들의 낙서, 간간이 보이는 신성력 잔재의 푸른빛 이펙트. 스산하고 음산한 분위기.
        *   Core Mechanic & Unique Features:
            - **환경 퍼즐:** 갇힌 NPC 구출을 위한 감옥 문 개방 퍼즐 (레버 조작, 비밀 통로 발견).
            - **숨겨진 통로:** 벽을 부수거나 특정 오브젝트와 상호작용하여 진입할 수 있는 히든 구역.
            - **첫 보스 전투:** 감옥 관리인 '고통의 간수 카라' (거대한 철퇴를 휘두르며 감옥 죄수들을 소환하는 패턴).
        *   Fun Elements:
            - 첫 드라곤 아르카나 조각 획득 및 '화염 브레스' 스킬 해금.
            - 감옥에 갇힌 주민들의 슬픈 사연을 담은 서브 퀘스트.
            - 퍼즐을 풀고 숨겨진 보물 상자를 찾는 탐험의 재미.

        *   Level Name: 잊혀진 고대 드래곤 유적지
        *   Theme & Background Story:
            엘드리안 왕국의 북쪽에 위치한, 고대 드래곤들이 처음 대지에 내려왔던 전설적인 장소. 지금은 시간이 멈춘 듯한 폐허로 변했으며, 타락한 드래곤들의 잔재와 고대의 함정들로 가득하다. 두 번째 드라콘 아르카나 조각이 잠들어 있다.
        *   Atmosphere & Art Direction: 거대한 돌기둥과 폐허가 된 제단, 용의 형상을 한 석상들, 이끼와 덩굴로 뒤덮인 유적, 안개 낀 신비로운 분위기. 푸른 마나의 잔광과 간헐적으로 들리는 용의 울음소리.
        *   Core Mechanic & Unique Features:
            - **플랫폼 액션:** 무너진 다리, 움직이는 석상 플랫폼을 이용한 점프 및 이동 퍼즐.
            - **원소 상호작용:** 드래곤 마법(불, 얼음)을 활용하여 얼어붙은 길을 녹이거나, 불타는 덩굴을 태워 길을 여는 퍼즐.
            - **중간 보스 전투:** 고대 유적을 지키는 '타락한 비늘수호자 크라칸' (광역 얼음 마법과 돌진 공격).
        *   Fun Elements:
            - 새로운 드래곤 마법 '냉기 폭풍' 스킬 해금.
            - 드래곤 유적 곳곳에 숨겨진 고대 드래곤의 지혜를 담은 비문 발견.
            - 동료 '리아나'의 마법 활용 퍼즐 협동 플레이."""
        parts = [
            "당신은 전문 게임 디자이너이자 엄격한 문서 포맷터입니다. 창의적이고 구체적인 게임 기획을 작성해 주세요.",
            "모든 내용은 한국어로 생성해주세요.",
            "아래 파라미터를 기반으로 게임 디자인 문서(GDD)를 생성해주세요.",
            "아래 주어진 GDD 템플릿의 서식(머리말, 번호, 글머리, 들여쓰기, 빈 줄 등)을 **100% 그대로** 유지하며, 오직 각 섹션의 내용만 채워 넣어야 합니다.",
            template, # GDD 템플릿 변수
            "또한 Narrative Overview의 Main Characters & Relationships에는 등장 캐릭터와 각 캐릭터의 소개를 생성해주세요.(캐릭터 3개 이상)",
            "또한 각 캐릭터마다 플레이어와의 관계 유형(신뢰, 우호적, 중립, 적대적, 증오 중 하나)을 반드시 명시해주세요.",
            "아래는 Main Characters & Relationships 예시입니다. 꼭 참고해서 똑같은 양식으로 생성해주세요.",
            relationship_example, # 관계 예시 변수
            "아래는 Level Design의 예시입니다. 꼭 참고해서 똑같은 양식으로 생성해주세요. (Level 3개 이상)",
            level_example, # 레벨 예시 변수
            f"게임 아이디어: {idea}",
            f"장르: {genre}",
            f"타겟 오디언스: {target}",
            f"컨셉: {concept}"
        ]
        return "\n\n".join(parts)

    def generate_gdd(
        self,
        idea: str,
        genre: str,
        target: str,
        concept: str,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> str:
        prompt = self.build_prompt(idea, genre, target, concept)
        self.logger.info("Sending prompt to LLM...")
        
        try:
            full_text = self.llm.generate(
                prompt, 
                temperature=temperature, 
                max_tokens=max_tokens
            )
            self.logger.info("GDD generated successfully.")
            
            return full_text
        except Exception as e:
            self.logger.error(f"Error during GDD generation: {e}")
            raise