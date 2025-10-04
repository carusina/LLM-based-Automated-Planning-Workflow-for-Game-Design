"""
local_image_generator.py

[재작성됨 v10] 최종 진화: GDD 맥락 분석 기반 동적 아트 스타일 생성
1.  **지능형 스타일 분석 (_create_dynamic_art_style_guide)**:
    GDD 텍스트 전체를 입력받아, LLM을 '아트 디렉터'로 활용하여 게임의 핵심 비주얼
    테마를 5~7개의 키워드로 추출합니다. 이를 통해 '중세 판타지' GDD에 '사이버펑크' 레벨이
    등장하는 복합적인 테마도 정확히 이해하고 시각적 통일성을 유지합니다.

2.  **아트 스타일 우선순위 (3-Tier-System)**:
    이미지 생성 시, 아래의 명확한 우선순위에 따라 최종 아트 스타일을 결정하여
    사용자 의도와 시스템의 자율성 사이의 균형을 맞춥니다.
    - **1순위 (사용자 지정):** 사용자가 --art-style로 직접 지정한 스타일.
    - **2순위 (동적 생성):** 사용자 지정이 없을 경우, GDD를 분석하여 자동 생성한 스타일.
    - **3순위 (기본값):** 위 두 가지가 모두 실패/누락될 경우에만 사용하는 최종 폴백 스타일.

3.  **완전한 맥락-비주얼 동기화**:
    이를 통해 GDD의 텍스트적 콘셉트와 생성되는 이미지의 시각적 결과물이 완벽하게
    일치하는, 진정한 의미의 '콘셉트 주도형 비주얼 생성'을 구현합니다.
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
    GDD 텍스트를 분석하여 동적으로 아트 스타일을 생성하고, 이를 기반으로
    계층적 프롬프트를 구성하여 콘셉트 아트를 생성하는 지능형 이미지 생성기.
    """

    # 3순위(폴백)로 사용될 기본 아트 스타일 가이드
    ART_STYLE_GUIDE = "masterpiece, best quality, (art by studio ghibli, makoto shinkai:1.2), beautiful detailed vibrant illustration, cinematic lighting, epic fantasy"

    def __init__(self, llm_service: LLMService, art_style_guide: str = None):
        """
        GeminiImageGenerator를 초기화합니다.

        Args:
            llm_service (LLMService): 프롬프트 생성을 위한 LLM 서비스 인스턴스.
            art_style_guide (str, optional): 1순위로 적용될 사용자 지정 아트 스타일.
        """
        if not genai or not Image or not exceptions:
            raise ImportError("Required libraries not found. Please run 'pip install google-generativeai pillow google-api-core'.")

        self.llm_service = llm_service
        # 1순위: 사용자가 --art-style로 직접 제공한 스타일을 저장
        self.user_provided_style = art_style_guide
        # 2순위: GDD를 분석하여 동적으로 생성될 스타일을 저장할 공간
        self.dynamic_art_style_guide = None
        
        if self.user_provided_style:
            logger.info(f"User-provided art style is set. This will be used as the highest priority.")

        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in the .env file.")

        genai.configure(api_key=api_key)
        self.image_model = genai.GenerativeModel('gemini-2.5-flash-image-preview')
        logger.info(f"GeminiImageGenerator initialized with image model: {self.image_model.model_name}")

    def _create_dynamic_art_style_guide(self, gdd_text: str):
        """
        GDD 텍스트 전체를 분석하여, 게임의 핵심 비주얼 테마를 담은
        '동적 아트 스타일 가이드'를 생성하고 self.dynamic_art_style_guide에 저장합니다.
        """
        logger.info("Analyzing GDD to create a dynamic art style guide...")
        try:
            prompt = (
                "As a world-class art director, analyze the overall content and atmosphere of the following Game Design Document (GDD). "
                "Then, create an 'art style guide' string for an AI image generator by combining 5-7 English keywords that best represent the core visual theme and art style of this game. "
                "For example, for a world of 'dark medieval fantasy with remnants of ancient technology', you should generate something like: "
                "'dark medieval fantasy, post-apocalyptic, ancient technology ruins, overgrown nature, solemn atmosphere, muted color palette, cinematic matte painting'.\n\n"
                "--- GDD TEXT ---"
                f"{gdd_text[:4000]}" # 토큰 제한을 고려하여 GDD 텍스트 일부 사용
                "\n--- END OF GDD ---\n\n"
                "Now, generate the art style guide string."
            )

            generated_style = self.llm_service.generate(prompt, temperature=0.6)
            if generated_style:
                self.dynamic_art_style_guide = generated_style.strip().replace('"', '') # Corrected: escaped quote
                logger.info(f"Successfully generated dynamic art style guide: {self.dynamic_art_style_guide}")
            else:
                logger.warning("Dynamic art style generation resulted in an empty string.")

        except Exception as e:
            logger.error(f"Failed to create dynamic art style guide: {e}", exc_info=True)
            self.dynamic_art_style_guide = None # 실패 시 None으로 명시적 초기화

    def _create_character_sheet(self, character: Dict[str, Any]) -> str:
        # ... (이전과 동일, 변경 없음)
        try:
            name = character.get("name")
            desc = character.get("description")
            if not (name and desc): return ""
            prompt = (
                f"Based on the following character information, create a concise and detailed paragraph in English that describes ONLY the character's physical appearance. "
                f"Focus strictly on visual traits like hair style, eye color, clothing, gear, and distinct features. Do not include personality, background, or story elements. "
                f"The output should be a single, coherent paragraph, perfect for an AI image generator's subject description.\n\n"
                f"Character Name: {name}\n"
                f"Character Description: {desc}"
            )
            character_sheet = self.llm_service.generate(prompt, temperature=0.4)
            return character_sheet.strip().replace("\n", " ").replace('"', '')
        except Exception as e:
            logger.error(f"Failed to create character sheet for '{character.get('name')}': {e}")
            return ""

    def _generate_image_prompts(self, metadata: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """
        3-Tier 우선순위에 따라 최종 아트 스타일을 결정하고, 계층적 프롬프트를 생성합니다.
        """
        logger.info("Generating hierarchical image prompts with prioritized art style...")
        
        # --- 최종 아트 스타일 결정 (3-Tier Priority) ---
        final_art_style = ""
        if self.user_provided_style:
            final_art_style = self.user_provided_style
            logger.info(f"Using [Priority 1] User-Provided Art Style: {final_art_style}")
        elif self.dynamic_art_style_guide:
            final_art_style = self.dynamic_art_style_guide
            logger.info(f"Using [Priority 2] Dynamic Art Style: {final_art_style}")
        else:
            final_art_style = self.ART_STYLE_GUIDE
            logger.info(f"Using [Priority 3] Default Fallback Art Style: {final_art_style}")

        prompts = {"characters": {}, "levels": {}}
        
        # --- 캐릭터/레벨 프롬프트 생성 (결정된 final_art_style 사용) ---
        for item_info in metadata.get("characters", []):
            name = item_info.get("name")
            description = item_info.get("description")
            if not (name and description): continue

            subject_prompt = self._create_character_sheet(item_info)
            action_prompt_template = (
                "You are a prompt engineer. Based on the character info, create a comma-separated list of keywords in English describing the character's ACTION, POSE, and the SCENE. "
                "Focus on dynamic elements like 'dramatic pose', 'running through a neon-lit alley', 'subtle smile', 'cinematic action scene'. "
                "DO NOT describe physical appearance like hair or eyes.\n\n"
                "Info: {description}\n\n"
                "Generate the action/scene keywords now."
            )
            action_prompt = self.llm_service.generate(action_prompt_template.format(description=description), temperature=0.7).strip().replace('"', '')

            final_prompt_parts = [final_art_style, f"({subject_prompt})" if subject_prompt else "", action_prompt]
            prompts["characters"][name] = ", ".join(filter(None, final_prompt_parts))

        for item_info in metadata.get("levels", []):
            level_name = item_info.get("name")
            if not level_name: continue

            level_desc_template = (
                "You are a world-class concept artist. Based on the info below, create a vivid, epic, and detailed description of a game level as a comma-separated list of keywords in English. "
                "Combine all elements into a unified, atmospheric scene description.\n\n"
                "Name: {name}\nDescription: {description}\nTheme: {theme}\nAtmosphere: {atmosphere}\n\n"
                "Generate the scene description keywords now. Do not add any conversational text."
            )
            subject_prompt = self.llm_service.generate(level_desc_template.format(name=level_name, description=item_info.get("description", ""), theme=item_info.get("theme", ""), atmosphere=item_info.get("atmosphere", "")), temperature=0.7).strip().replace('"', '')

            final_prompt_parts = [final_art_style, subject_prompt]
            prompts["levels"][level_name] = ", ".join(filter(None, final_prompt_parts))

        return prompts

    def generate_images_from_metadata(self, metadata: Dict[str, Any], output_dir: str, gdd_text: str) -> List[str]:
        """
        GDD 텍스트를 받아 동적 스타일을 생성한 후, 메타데이터 기반으로 이미지를 생성/저장합니다.
        """
        logger.info(f"Starting intelligent image generation process...")
        
        if not self.user_provided_style:
            self._create_dynamic_art_style_guide(gdd_text)

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        image_prompts = self._generate_image_prompts(metadata)
        if not (image_prompts["characters"] or image_prompts["levels"]):
            logger.warning("No image prompts were generated. Skipping image creation.")
            return []

        saved_image_paths = []
        all_prompts = {f"character_{k}": v for k, v in image_prompts["characters"].items()}
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
                        logger.warning(f"Attempt {attempt + 1} for '{entity_key}' failed: {e}. Retrying...")
                        if attempt + 1 == max_retries: raise
                        time.sleep(retry_delay_seconds)
                        retry_delay_seconds *= 2
                if not response: continue

                images_saved_for_this_prompt = 0
                text_parts = []
                if not response.candidates: continue

                for i, part in enumerate(response.candidates[0].content.parts):
                    if hasattr(part, 'inline_data') and part.inline_data and part.inline_data.mime_type.startswith('image/'):
                        image_data = part.inline_data.data
                        image = Image.open(BytesIO(image_data))
                        safe_filename_base = re.sub(r'[\\/*?:\"<>|]', '_', entity_key).strip() # Corrected: escaped quote
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
                        error_details = "No valid image data in response."
                        try:
                            if response.prompt_feedback: error_details += f" | Prompt Feedback: {response.prompt_feedback}"
                            if response.candidates and response.candidates[0].safety_ratings: error_details += f" | Candidate Safety Ratings: {response.candidates[0].safety_ratings}"
                        except (AttributeError, IndexError): pass
                        logger.error(f"Image generation failed for '{entity_key}'. {error_details}")
            except Exception as e:
                logger.error(f"An unexpected error occurred while processing '{entity_key}': {e}", exc_info=False)
        
        logger.info(f"Image generation process finished. Saved {len(saved_image_paths)}/{total_requests} images.")
        return saved_image_paths