"""
local_image_generator.py

[재작성됨 v7] GDD 메타데이터 기반 이미지 생성 모듈 (실제 데이터 구조 반영).
이 모듈은 메타데이터의 'levels' 키와 그 하위 구조(description, theme, atmosphere)를 정확히 반영하여
캐릭터 및 레벨 콘셉트 아트를 안정적으로 생성합니다.

1. LLMService를 활용, 메타데이터로부터 캐릭터 및 레벨에 대한 이미지 생성용 프롬프트를 생성합니다.
2. 'gemini-2.5-flash-image-preview' 모델에 프롬프트를 전달합니다.
3. 500 Internal Server Error와 같은 일시적인 API 오류 발생 시, 재시도 로직을 수행합니다.
4. 모델 응답의 각 part를 순회하며, mime_type이 이미지인 part만 필터링하여 안전하게 저장합니다.
"""

import os
import re
import time
import logging
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv
from io import BytesIO

# PIL(Pillow)가 설치되지 않았을 경우를 대비
try:
    from PIL import Image
except ImportError:
    Image = None

# google.generativeai가 설치되지 않았을 경우를 대비
try:
    import google.generativeai as genai
    from google.api_core import exceptions
except ImportError:
    genai = None
    exceptions = None

from .llm_service import LLMService
from .utils import LoggingUtils

# 로거 설정
logger = LoggingUtils.setup_logger(__name__)

class GeminiImageGenerator:
    """
    GDD 메타데이터를 입력받아 Google Gemini API를 통해 콘셉트 아트를 생성하고 저장하는 클래스.
    `GenerativeModel` 인터페이스와 `gemini-2.5-flash-image-preview` 모델을 사용합니다.
    """

    def __init__(self, llm_service: LLMService):
        """
        GeminiImageGenerator를 초기화합니다.
        """
        if not genai or not Image or not exceptions:
            raise ImportError("Required libraries not found. Please run 'pip install google-generativeai pillow google-api-core'.")

        self.llm_service = llm_service
        logger.info(f"LLMService for prompt engineering: {type(self.llm_service.client).__name__}")

        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in the .env file.")

        genai.configure(api_key=api_key)

        self.image_model = genai.GenerativeModel('gemini-2.5-flash-image-preview')
        logger.info(f"GeminiImageGenerator initialized with image model: {self.image_model.model_name}")

    def _generate_image_prompts(self, metadata: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """
        메타데이터를 기반으로 캐릭터 및 레벨의 이미지 생성용 상세 프롬프트를 생성합니다.
        """
        logger.info("Generating detailed image prompts for characters and levels...")
        # '왜?': 일관성을 위해 locations 대신 levels 키를 사용합니다.
        prompts = {"characters": {}, "levels": {}}
        
        character_prompt_template = """
        As a world-class video game concept art director, create a single, powerful, and visually descriptive prompt in English for an AI image generator.
        The prompt must be a comma-separated list of keywords and phrases that capture the essence of the character described below.
        Focus on visual details: appearance, clothing, expression, mood, lighting, and art style.
        For example: "epic fantasy, detailed character portrait, a stoic male warrior, intricate glowing armor, cinematic lighting, holding a mythical sword, style of digital painting, concept art, sharp focus".

        Character Information:
        - Name: {name}
        - Description: {description}

        Generate the detailed English prompt now.
        """

        try:
            # --- 캐릭터 프롬프트 생성 로직 ---
            for item_info in metadata.get("characters", []):
                name = item_info.get("name")
                desc = item_info.get("description")
                if not (name and desc):
                    continue
                prompt_text = character_prompt_template.format(name=name, description=desc)
                generated_prompt = self.llm_service.generate(prompt_text, temperature=0.7)
                prompts["characters"][name] = generated_prompt.strip()

            # --- 레벨 프롬프트 생성 로직 (실제 데이터 구조 반영) ---
            # '왜?': 메타데이터의 실제 키인 'levels'와 그 하위 구조(description, theme, atmosphere)를 사용하도록 수정합니다.
            for item_info in metadata.get("levels", []):
                level_name = item_info.get("name")
                level_description = item_info.get("description")
                level_theme = item_info.get("theme")
                level_atmosphere = item_info.get("atmosphere")

                if not all([level_name, level_description, level_theme, level_atmosphere]):
                    logger.warning(f"Skipping level '{level_name}' due to missing data.")
                    continue

                # 지시사항에 명시된, 풍부한 컨텍스트를 제공하는 프롬프트 구조를 사용합니다.
                prompt_instruction = (
                    f"다음 게임 레벨 정보를 바탕으로, AI 이미지 생성 모델이 사용할 생생하고 서사적인 영어 프롬프트를 생성해줘. "
                    f"아래의 모든 요소를 종합하여 하나의 통일된 분위기의 장면을 묘사해야 해.\n\n"
                    f"장소 이름: {level_name}\n"
                    f"장면 묘사: {level_description}\n"
                    f"핵심 테마: {level_theme}\n"
                    f"전체적인 분위기: {level_atmosphere}\n\n"
                    f"결과물은 'cinematic fantasy landscape, epic, detailed, matte painting' 같은 아트 스타일 키워드를 반드시 포함해야 해."
                )
                
                generated_prompt = self.llm_service.generate(prompt_instruction, temperature=0.7)
                prompts["levels"][level_name] = generated_prompt.strip()
                logger.debug(f"Generated prompt for level '{level_name}'.")
            
            logger.info(f"Successfully generated {len(prompts['characters'])} character prompts and {len(prompts['levels'])} level prompts.")
            return prompts

        except Exception as e:
            logger.error(f"An error occurred while generating image prompts: {e}", exc_info=True)
            return prompts

    def generate_images_from_metadata(self, metadata: Dict[str, Any], output_dir: str) -> List[str]:
        """
        메타데이터로부터 콘셉트 아트 이미지를 생성하고 저장합니다.
        일시적인 서버 오류 발생 시 재시도 로직을 포함합니다.
        """
        logger.info(f"Starting image generation process for characters and levels. Output directory: {output_dir}")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        image_prompts = self._generate_image_prompts(metadata)
        if not (image_prompts["characters"] or image_prompts["levels"]):
            logger.warning("No image prompts were generated. Skipping image creation.")
            return []

        saved_image_paths = []
        
        # '왜?': 캐릭터와 레벨을 하나의 딕셔너리로 통합하여, 중복 코드 없이 단일 루프로 처리하기 위함입니다.
        all_prompts = {f"character_{k}": v for k, v in image_prompts["characters"].items()}
        # 'locations' -> 'levels'로 키 변경, 파일명 접두사를 'level_'로 변경
        all_prompts.update({f"level_{k}": v for k, v in image_prompts["levels"].items()})
        total_requests = len(all_prompts)

        for entity_key, prompt in all_prompts.items():
            try:
                response = None
                max_retries = 3
                retry_delay_seconds = 5

                for attempt in range(max_retries):
                    try:
                        logger.info(f"Requesting image for '{entity_key}' (Attempt {attempt + 1}/{max_retries})...")
                        response = self.image_model.generate_content(contents=[prompt])
                        break
                    except (exceptions.InternalServerError, exceptions.ServiceUnavailable) as e:
                        logger.warning(f"Attempt {attempt + 1} for '{entity_key}' failed with a transient server error: {e}. Retrying in {retry_delay_seconds}s...")
                        if attempt + 1 == max_retries:
                            logger.error(f"All retries failed for '{entity_key}'.")
                            raise
                        time.sleep(retry_delay_seconds)
                        retry_delay_seconds *= 2
                
                if not response:
                    logger.error(f"No response from API for '{entity_key}' after all retries.")
                    continue

                images_saved_for_this_prompt = 0
                text_parts = []

                if not response.candidates:
                    logger.error(f"Image generation failed for '{entity_key}'. Response had no candidates.")
                    continue

                for i, part in enumerate(response.candidates[0].content.parts):
                    if hasattr(part, 'inline_data') and part.inline_data and part.inline_data.mime_type.startswith('image/') :
                        image_data = part.inline_data.data
                        image = Image.open(BytesIO(image_data))
                        
                        safe_filename_base = re.sub(r'[\\/*?:"<>|]', '_', entity_key).strip()
                        image_filename = f"{safe_filename_base}_{i}.png"
                        image_path = output_path / image_filename

                        image.save(image_path)
                        saved_image_paths.append(str(image_path))
                        images_saved_for_this_prompt += 1
                        logger.info(f"✅ Successfully saved image: {image_path}")
                    
                    elif hasattr(part, 'text') and part.text:
                        text_parts.append(part.text)

                if images_saved_for_this_prompt == 0:
                    if text_parts:
                        full_text_response = " ".join(text_parts)
                        logger.error(f"Image generation failed for '{entity_key}'. Model returned text instead: {full_text_response[:300]}...")
                    else:
                        logger.error(f"Image generation failed for '{entity_key}'. No valid image data in response.")

            except Exception as e:
                logger.error(f"An unexpected error occurred while processing '{entity_key}': {e}", exc_info=False)
        
        logger.info(f"Image generation process finished. Successfully saved {len(saved_image_paths)} images out of {total_requests} requests.")
        return saved_image_paths
