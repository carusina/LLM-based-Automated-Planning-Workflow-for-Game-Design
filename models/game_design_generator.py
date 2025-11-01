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
        relationship_example = """- 에리안: ... 플레이어와의 관계: 신뢰"""
        level_example = """9. Level Design ..."""
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