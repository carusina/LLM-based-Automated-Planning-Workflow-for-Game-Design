"""
Cinematic Storyline Generator

This module is responsible for generating a structured cinematic storyline based on the
metadata extracted from a Game Design Document (GDD).

Design Rationale (3-Step Pipeline):
1.  **Consistency & Coherence**: By first creating a high-level plot outline (the "blueprint"),
    we ensure the entire story follows a logical progression (Exposition, Rising Action, Climax,
    Falling Action, Resolution). This prevents the LLM from generating disjointed or
    inconsistent scenes.
2.  **Structured Elaboration**: The pipeline gradually increases the level of detail, moving
    from a broad outline to chapter summaries, and finally to specific scenes. This mimics
    how human writers often work, ensuring a well-developed narrative.
3.  **Structured JSON Output for Interoperability**: The final output is a list of JSON
    objects, where each object represents a scene. This structured format is crucial for
    seamless integration with subsequent modules in the automated video generation
    workflow (e.g., image generation, video editing). It acts as a clear "API contract"
    between the story generation and visual generation phases.
"""
import json
from typing import Any, Dict, List

from .llm_service import LLMService


class StorylineGenerator:
    """
    Generates a structured cinematic storyline from GDD metadata using a 3-step pipeline.
    """

    def __init__(self, llm_service: LLMService):
        """
        Initializes the StorylineGenerator.

        Args:
            llm_service: An instance of LLMService to communicate with the language model.
        """
        self.llm_service = llm_service

    def generate(self, metadata: Dict[str, Any], num_chapters: int) -> List[Dict[str, Any]]:
        """
        Generates the full storyline by executing the 3-step pipeline.

        Args:
            metadata: The GDD metadata dictionary.
            num_chapters: The desired number of chapters.

        Returns:
            A list of scene dictionaries representing the complete storyline.
        """
        print("Step 1: Creating plot outline...")
        plot_outline = self._create_plot_outline(metadata)

        print("Step 2: Creating chapter summaries...")
        chapter_summaries = self._create_chapter_summaries(plot_outline, num_chapters)

        print("Step 3: Creating scenes for each chapter...")
        all_scenes = []
        for i, summary in enumerate(chapter_summaries):
            chapter_number = i + 1
            print(f"  - Generating scenes for Chapter {chapter_number}...")
            scenes = self._create_scenes_for_chapter(summary, chapter_number, metadata)
            all_scenes.extend(scenes)

        return all_scenes

    def _create_plot_outline(self, metadata: Dict[str, Any]) -> str:
        """
        Step 1: Creates the overall plot outline based on the 5-act structure.
        """
        prompt = f"""
        당신은 전문 스토리 작가입니다. 아래에 제공되는 게임 디자인 메타데이터를 기반으로, 소설의 '기승전결' 구조에 따른 흥미진진한 전체 스토리 줄거리(Plot Outline)를 작성해주세요. 이 줄거리는 앞으로 생성될 모든 챕터와 씬의 청사진이 됩니다.

        **게임 메타데이터:**
        - 제목: {metadata.get('title', 'N/A')}
        - 장르: {metadata.get('genre', 'N/A')}
        - 핵심 컨셉: {metadata.get('concept', 'N/A')}
        - 주요 캐릭터: {', '.join([char['name'] for char in metadata.get('characters', [])])}
        - 배경 설정: {', '.join([level['name'] for level in metadata.get('levels', [])])}

        **요구사항:**
        1.  **서막 (Exposition):** 주인공과 주요 인물, 그리고 그들이 처한 초기 상황을 소개합니다.
        2.  **상승 (Rising Action):** 갈등이 시작되고, 주인공이 목표를 향해 나아가면서 겪는 일련의 사건들을 묘사합니다.
        3.  **절정 (Climax):** 이야기의 가장 긴장감 넘치는 순간, 주인공이 최대의 위기에 직면하는 부분을 그립니다.
        4.  **하강 (Falling Action):** 절정의 사건 이후, 긴장이 완화되고 이야기의 결과가 서서히 드러나는 과정을 보여줍니다.
        5.  **결말 (Resolution):** 모든 갈등이 해결되고, 주인공과 세계의 최종적인 운명이 결정되는 마지막 장면을 작성합니다.

        위 5단계 구조에 맞춰 전체 줄거리를 서술해주세요.
        """
        return self.llm_service.generate(prompt, max_tokens=1500)

    def _create_chapter_summaries(self, plot_outline: str, num_chapters: int) -> List[str]:
        """
        Step 2: Divides the plot outline into chapter summaries.
        """
        prompt = f"""
        당신은 편집자입니다. 아래의 전체 줄거리를 총 {num_chapters}개의 챕터로 나누고, 각 챕터에서 일어날 핵심 사건을 요약해주세요.

        **전체 줄거리 (Plot Outline):**
        {plot_outline}

        **요구사항:**
        - 전체 줄거리의 흐름을 자연스럽게 {num_chapters}개의 부분으로 나누세요.
        - 각 챕터 요약은 다음 챕터에 대한 기대감을 유발해야 합니다.
        - 결과는 아래와 같이 "CHAPTER 1:", "CHAPTER 2:" 형식으로 각 챕터를 구분하여 작성해주세요.

        **출력 형식:**
        CHAPTER 1: [1챕터 요약]
        CHAPTER 2: [2챕터 요약]
        ...
        CHAPTER {num_chapters}: [{num_chapters}챕터 요약]
        """
        response = self.llm_service.generate(prompt, max_tokens=2000)
        # Split the response into summaries based on "CHAPTER X:" delimiter
        summaries = [s.strip() for s in response.split("CHAPTER ")[1:]]
        return [s.split(":", 1)[1].strip() if ":" in s else s for s in summaries]


    def _create_scenes_for_chapter(self, chapter_summary: str, chapter_number: int, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Step 3: Creates detailed, structured scenes for a given chapter summary.
        """
        character_names = [char['name'] for char in metadata.get('characters', [])]
        level_names = [level['name'] for level in metadata.get('levels', [])]

        prompt = f"""
        당신은 시나리오 작가입니다. 아래의 챕터 요약과 게임 설정 정보를 바탕으로, 이 챕터를 구성하는 상세한 씬(Scene)들을 JSON 배열 형식으로 작성해주세요.

        **이번 챕터의 핵심 줄거리:**
        {chapter_summary}

        **게임 설정 정보:**
        - 등장인물 리스트: {character_names}
        - 주요 장소 리스트: {level_names}

        **JSON 출력 규칙 (매우 중요):**
        - 반드시 유효한 JSON 배열(List of Objects) 형식으로만 응답해야 합니다.
        - 각 JSON 객체는 하나의 씬(Scene)을 의미하며, 다음 키(key)들을 포함해야 합니다.
          - `scene_id`: "C{chapter_number}_S{{scene_number}}" 형식의 고유 ID (예: "C{chapter_number}_S1", "C{chapter_number}_S2").
          - `setting`: 씬의 배경이 되는 장소. 반드시 **주요 장소 리스트**에 있는 이름 중 하나를 사용해야 합니다.
          - `characters`: 씬에 등장하는 인물들의 이름 배열. 반드시 **등장인물 리스트**에 있는 이름들로 구성해야 합니다.
          - `description`: 씬의 상황, 인물의 행동과 대사, 분위기를 상세하고 생생하게 묘사합니다. (3-4 문장 내외)
          - `key_event`: 이 씬에서 발생하는 가장 핵심적인 사건이나 전환점을 한 문장으로 요약합니다.

        **출력 예시:**
        [
          {{
            "scene_id": "C1_S1",
            "setting": "네온 거리",
            "characters": ["나비", "유키"],
            "description": "비가 내리는 네온 거리의 뒷골목, 나비는 쓰레기 더미 속에서 기억을 잃은 채 깨어난다. 그때, 조력자 유키로부터 첫 통신이 들어온다.",
            "key_event": "주인공이 깨어나고, 조력자와 처음으로 접촉한다."
          }},
          {{
            "scene_id": "C1_S2",
            "setting": "안전 가옥",
            "characters": ["나비"],
            "description": "유키의 안내에 따라 도착한 허름한 안전 가옥. 나비는 낡은 단말기를 통해 자신의 임무에 대한 첫 번째 단서를 발견한다.",
            "key_event": "주인공이 자신의 임무에 대한 실마리를 얻는다."
          }}
        ]

        이제, 위 규칙에 따라 챕터 {chapter_number}의 씬들을 JSON으로 작성해주세요. 다른 설명 없이 JSON 배열만 출력해야 합니다.
        """
        response_text = self.llm_service.generate(prompt, max_tokens=4000)
        try:
            # LLM이 JSON 마크다운 형식(```json ... ```)으로 반환하는 경우를 대비하여 파싱
            if response_text.strip().startswith("```json"):
                response_text = response_text.strip()[7:-3].strip()
            elif response_text.strip().startswith("["):
                 response_text = response_text.strip()
            
            scenes = json.loads(response_text)
            # scene_id에 챕터 번호가 올바르게 부여되었는지 다시 한번 확인하고 수정
            for i, scene in enumerate(scenes):
                scene['scene_id'] = f"C{chapter_number}_S{i+1}"
            return scenes
        except json.JSONDecodeError:
            print(f"Error: Failed to decode JSON for Chapter {chapter_number}.")
            print(f"LLM Response:\n{response_text}")
            return []
