"""
models/cinematic_generator.py

이 모듈은 구조화된 스토리라인 데이터를 기반으로, 각 장면에 해당하는
시네마틱 이미지를 생성하는 역할을 담당합니다.

기존의 GeminiImageGenerator를 재사용하여, GDD로부터 추론된 '동적 아트 스타일'과
'캐릭터 시트'를 일관성 있게 활용하는 것이 핵심입니다.
이를 통해 프로젝트 전체의 시각적 통일성을 보장합니다.
"""
import os
import re
from pathlib import Path
from typing import Dict, Any, List

from .llm_service import LLMService
from .local_image_generator import GeminiImageGenerator
from .utils import LoggingUtils

# 로거 설정
logger = LoggingUtils.setup_logger(__name__)

class CinematicGenerator:
    """
    스토리라인의 각 씬(Scene)을 시각화하는 시네마틱 이미지 생성기.
    의존성 주입을 통해 LLM 서비스와 이미지 생성기를 제어합니다.
    """

    def __init__(self, llm_service: LLMService, image_generator: GeminiImageGenerator):
        """
        CinematicGenerator를 초기화합니다.

        Args:
            llm_service (LLMService): 텍스트 생성을 위한 LLM 서비스.
            image_generator (GeminiImageGenerator): 이미지 생성을 담당하는 기존 서비스.
        """
        self.llm_service = llm_service
        self.image_generator = image_generator
        logger.info("CinematicGenerator initialized.")

    def _create_scene_narrative(self, description: str) -> str:
        """
        단순한 씬 설명을 바탕으로, 이미지 생성에 적합한 구체적인 연출/상황 묘사를 생성합니다.
        """
        try:
            prompt = (
                "You are a master cinematographer. Based on the following brief scene description, "
                "create a detailed and vivid paragraph in English that describes the characters' specific actions, facial expressions, interactions, and the overall camera composition. "
                "This description will be used to generate a single, compelling image for the scene. Do not mention camera movements, only the final shot composition.\n\n"
                f"Scene Description: \"{description}\"\n\n"
                "Now, generate the detailed cinematic description for the image generator."
            )
            narrative = self.llm_service.generate(prompt, temperature=0.7)
            return narrative.strip().replace("\n", " ")
        except Exception as e:
            logger.error(f"Failed to create scene narrative: {e}", exc_info=True)
            return ""

    def generate_scenes(self, storyline_data: List[Dict[str, Any]], output_dir: str) -> List[str]:
        """
        [REFACTORED] 확립된 비주얼 아이덴티티를 기반으로 각 씬의 이미지를 생성합니다.

        Args:
            storyline_data (List[Dict[str, Any]]): 씬 정보가 담긴 리스트.
            output_dir (str): 이미지 저장 경로.

        Returns:
            List[str]: 생성된 이미지 파일의 전체 경로 리스트.
        """
        logger.info("Starting cinematic scene generation using established visual identity...")
        
        # --- [REFACTORED] 총괄 아트 디렉터의 결정사항을 직접 참조 ---
        final_art_style = self.image_generator.established_art_style
        character_sheets = self.image_generator.character_sheets
        # ---

        if not final_art_style:
            logger.error("Art style has not been established. Please run 'establish_visual_identity' on the image generator first.")
            return []

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Using established art style: {final_art_style}")

        saved_image_paths = []
        for scene in storyline_data:
            scene_id = scene.get("scene_id")
            if not scene_id:
                logger.warning("Skipping scene with no scene_id.")
                continue

            logger.info(f"Processing Scene ID: {scene_id}")

            # '시네마틱 씬 프롬프트' 조합
            prompt_parts = [final_art_style]

            # [등장인물 묘사부] - 확립된 캐릭터 시트 사용
            scene_characters = scene.get("characters", [])
            for char_name in scene_characters:
                if char_name in character_sheets:
                    prompt_parts.append(f"({character_sheets[char_name]})")
                else:
                    logger.warning(f"Character sheet for '{char_name}' not found in established identity.")

            # [배경 묘사부]
            setting = scene.get("setting")
            if setting:
                prompt_parts.append(f"Background: {setting}")

            # [연출/상황 묘사부]
            description = scene.get("description")
            if description:
                narrative = self._create_scene_narrative(description)
                if narrative:
                    prompt_parts.append(narrative)

            final_prompt = ", ".join(filter(None, prompt_parts))
            logger.debug(f"Final prompt for scene {scene_id}: {final_prompt}")

            # 이미지 생성 및 저장
            try:
                image_filename = f"scene_{scene_id}.png"
                image_path = output_path / image_filename
                
                logger.info(f"Requesting image for scene {scene_id}...")
                response = self.image_generator.image_model.generate_content(contents=[final_prompt])

                image_saved_for_scene = False
                text_parts = []

                if not response.candidates:
                    logger.error(f"Image generation failed for scene {scene_id}. No candidates returned.")
                    continue

                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data and part.inline_data.mime_type.startswith('image/'):
                        image_data = part.inline_data.data
                        from PIL import Image
                        from io import BytesIO
                        
                        image = Image.open(BytesIO(image_data))
                        image.save(image_path)
                        saved_image_paths.append(str(image_path))
                        logger.info(f"✅ Successfully saved image: {image_path}")
                        image_saved_for_scene = True
                        break
                    elif hasattr(part, 'text') and part.text:
                        text_parts.append(part.text)

                if not image_saved_for_scene:
                    if text_parts:
                        full_text_response = " ".join(text_parts)
                        logger.error(f"Image generation failed for scene {scene_id}. Model returned text instead: {full_text_response[:500]}...")
                    else:
                        error_details = "No valid image data in response."
                        try:
                            if response.prompt_feedback: error_details += f" | Prompt Feedback: {response.prompt_feedback}"
                        except AttributeError: pass
                        logger.error(f"Image generation failed for scene {scene_id}. {error_details}")

            except Exception as e:
                logger.error(f"An error occurred while generating image for scene {scene_id}: {e}", exc_info=True)

        logger.info(f"Cinematic scene generation finished. Saved {len(saved_image_paths)} images.")
        return saved_image_paths
