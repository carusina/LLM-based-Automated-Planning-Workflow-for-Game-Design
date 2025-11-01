# LLM 기반 지능형 게임 기획 및 시각화 자동화 파이프라인

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

LLM(Large Language Model)의 추론 능력을 다단계로 활용하여, 단일 아이디어로부터 체계적인 게임 디자인 문서(GDD)를 생성하고, GDD의 전체 맥락을 이해하여 통일성 있는 콘셉트 아트와 시네마틱 비디오까지 자동으로 생성하는 지능형 워크플로우입니다.

## 🚀 핵심 기능 (Key Features)

이 프로젝트는 단순한 텍스트 생성을 넘어, 여러 LLM 에이전트가 유기적으로 협력하여 기획의 깊이를 더하고 시각적 결과물까지 만들어내는 자동화된 파이프라인을 구축하는 것을 목표로 합니다.

-   **지능형 GDD 생성**: 사용자의 추상적인 아이디어를 입력받아, 게임의 핵심 시스템, 캐릭터, 레벨, 스토리 등을 포함하는 체계적인 GDD를 생성합니다.
-   **2-Step 메타데이터 추출**: 생성된 GDD 텍스트를 다시 LLM이 분석하여, 캐릭터, 레벨, 아이템 등의 정보를 정확한 JSON 형식의 메타데이터로 추출합니다. 정규식의 불안정성을 해결하고 문맥 이해를 통해 높은 정확도를 보장합니다.
-   **AI 기반 콘셉트 아트 생성**: 추출된 메타데이터를 기반으로 Gemini API를 호출하여, 각 요소에 맞는 고품질 콘셉트 아트를 자동으로 생성하여 아이디어를 즉시 시각화합니다.
-   **동적 아트 스타일 가이드 (AI Art Director)**: GDD 전체의 맥락과 분위기를 AI가 분석하여, 게임의 고유한 비주얼 테마를 나타내는 '아트 스타일 가이드'를 동적으로 생성하고 모든 이미지에 일관되게 적용합니다.
-   **🎬 시네마틱 비디오 생성 (Cinematic Video Generation)**: 생성된 스토리라인과 비주얼 아이덴티티를 기반으로, 각 장면에 대한 동적인 비디오 클립을 자동 생성하여 게임의 순간들을 영상으로 구체화합니다.
-   **사용자 정의 아트 스타일**: 사용자가 `--art-style` 명령어를 통해 AI의 판단을 덮어쓰고, `pixel art` 등 원하는 특정 화풍을 직접 지정할 수 있습니다.
-   **지식 그래프 연동**: 생성된 메타데이터를 Neo4j 같은 그래프 데이터베이스에 저장하여, 엔티티 간의 복잡한 관계를 모델링하고 고급 질의응답 시스템의 기반을 마련합니다。
-   **GraphRAG (지식 그래프 기반 문서 업데이트)**: Neo4j에 저장된 지식 그래프를 활용하여 기존 GDD를 업데이트합니다. LLM이 지식 그래프의 컨텍스트를 참조하여 문서의 일관성을 유지하며 내용을 수정할 수 있도록 돕습니다.

## ⚙️ 아키텍처 워크플로우

```
[사용자 아이디어 입력]
        |
        V
[1. GameDesignGenerator (GDD 생성)] ----> (1차 LLM 호출: 창의적 작가)
        |
        V
[ 생성된 GDD 텍스트 (.md) ]
        |
        +----------------------------------------------------------+
        |                                                          |
        V                                                          V
[2. KnowledgeGraphService (메타데이터 추출)] ----> (2차 LLM 호출: 분석 전문가)   [3. GeminiImageGenerator (GDD 분석)] ----> (3차 LLM 호출: 아트 디렉터)
        |                                                          |
        V                                                          V
[ 구조화된 JSON 메타데이터 ]                               [ '동적 아트 스타일 가이드' 생성 ]
        |                                                          |
        +---------------------->+----------------------------------+
                                |
                                V
[4. GeminiImageGenerator (이미지 생성)]
   |
   +--- [메타데이터 기반 '주제/연출 프롬프트' 생성] ----> (4차 LLM 호출: 프롬프트 엔지니어)
   |
   +--- [최종 프롬프트 조합 및 생성] ----> (Gemini Image API 호출)
        |
        V
[5. CinematicGenerator (비디오 생성)] ----> (Google Veo API 호출)
        |
        V
[ 최종 결과물: GDD 문서 + 메타데이터 JSON + 콘셉트 아트 이미지 + 시네마틱 비디오 클립 ]
```

## 🛠️ 설치 및 환경설정

### 1. 저장소 복제 및 이동
```bash
git clone https://github.com/carusina/LLM-based-Automated-Planning-Workflow-for-Game-Design.git
cd LLM-based-Automated-Planning-Workflow-for-Game-Design
```

### 2. 가상 환경 생성 및 의존성 설치
```bash
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화 (Windows)
venv\Scripts\activate
# 가상 환경 활성화 (macOS/Linux)
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```
*참고: `requirements.txt`에는 최신 Google AI 모델을 위한 `google-genai`와 비디오 처리를 위한 `moviepy` 라이브러리가 포함되어 있습니다.*

### 3. `.env` 파일 설정
프로젝트 루트에 `.env` 파일을 생성하고, API 키를 설정합니다. **본 프로젝트의 모든 기능을 사용하려면 `GEMINI_API_KEY`가 반드시 필요합니다.**

```env
# .env

# Google Gemini API Key (텍스트 분석, 동적 스타일 생성, 이미지 및 비디오 생성에 필수)
GEMINI_API_KEY="여기에_당신의_Gemini_API_키를_입력하세요"

# (선택) 텍스트 생성에 다른 모델을 사용하고 싶을 경우
# OPENAI_API_KEY="sk-..."
```

## 🎮 사용 방법 (Usage)

본 프로젝트는 `Typer`로 구축된 CLI(명령줄 인터페이스)를 통해 제어됩니다. `gdd`와 같은 하위 명령어를 사용하여 원하는 기능을 실행할 수 있습니다.

터미널에서 `--help` 옵션을 사용하면 언제든지 전체 명령어 목록이나 특정 명령어의 상세 옵션을 확인할 수 있습니다.

```bash
# 전체 명령어 목록 확인
python main.py --help

# gdd 명령어의 상세 옵션 확인
python main.py gdd --help
```

### `gdd` 명령어

게임 디자인 문서(GDD) 생성부터 콘셉트 아트, 비디오 클립 시각화까지 파이프라인의 핵심 기능을 실행합니다.

#### 빠른 시작 (Quick Start)

아래 예시는 GDD를 생성하고, 그 내용에 기반하여 콘셉트 아트와 시네마틱 비디오 클립까지 자동으로 생성하는 가장 일반적인 명령어입니다.

```bash
python main.py gdd --idea "고대 드래곤의 힘을 이어받은 용기사가 타락한 왕국을 구원하는 여정" --genre "에픽 판타지 액션 RPG" --target "판타지 RPG 팬" --concept "실시간 검술과 드래곤 마법을 조합한 전투" --art-style "다크 판타지" --generate-images
```

#### 명령어 옵션 (Options)

`gdd` 명령어는 다음과 같은 옵션을 제공합니다.

| 옵션                  | 단축키 | 설명                                                                 | 필수 | 기본값    |
| --------------------- | ------ | -------------------------------------------------------------------- | ---- | --------- |
| `--idea`              |        | 게임의 핵심 아이디어 (한 문장)                                       | 예   | -         |
| `--genre`             |        | 게임의 장르 (예: `에픽 판타지 액션 RPG`)                             | 예   | -         |
| `--target`            |        | 게임의 타겟 유저                                                     | 예   | -         |
| `--concept`           |        | 핵심 게임플레이 콘셉트 및 시스템                                     | 예   | -         |
| `--art-style`         |        | 콘셉트 아트의 아트 스타일 (예: `Ghibli-inspired`, `Cyberpunk`)       | 아니오 | `Default` |
| `--output-dir`        | `-o`   | 생성된 모든 파일이 저장될 디렉토리                                   | 아니오 | `output`  |
| `--generate-images`   |        | GDD 생성 후 콘셉트 아트와 시네마틱 비디오를 포함한 전체 시각 에셋을 생성할지 결정하는 플래그 | 아니오 | `False`   |
| `--chapters`          | `-c`   | 이미지/비디오 생성 시 만들 스토리라인 챕터 수                        | 아니오 | `5`       |
| `--skip-concepts`     |        | 개별 콘셉트 아트 생성을 건너뛸지 여부를 결정하는 플래그              | 아니오 | `False`   |

### `update-gdd` 명령어

기존에 생성된 GDD를 지식 그래프(Neo4j)의 컨텍스트를 활용하여 업데이트합니다.

#### 사용 예시

```bash
python main.py update-gdd --gdd-path "output/20251101_193404/GDD_Default_20251101_193404.md" --update-request "주인공 '카이'의 목표를 '잃어버린 동생을 찾는 것'으로 변경해주세요." --output-path "output/20251101_193404/GDD_updated.md"
```

#### 명령어 옵션 (Options)

`update-gdd` 명령어는 다음과 같은 옵션을 제공합니다.

| 옵션              | 설명                                                                 | 필수 | 기본값 |
| ----------------- | -------------------------------------------------------------------- | ---- | ------ |
| `--gdd-path`      | 업데이트할 원본 GDD 마크다운 파일의 경로                             | 예   | -      |
| `--update-request`| GDD에 적용할 변경 사항을 설명하는 프롬프트                           | 예   | -      |
| `--output-path`   | 업데이트된 GDD 파일을 저장할 경로                                    | 예   | -      |

## 📂 출력 구조

실행 완료 후, `output/` 디렉토리에 타임스탬프 기반으로 결과물이 저장됩니다.

```
output/
├── GDD_Dark_Fantasy_20251012_183000.md         # 생성된 게임 디자인 문서
├── GDD_Dark_Fantasy_20251012_183000_meta.json  # 추출된 메타데이터
└── 20251012_183000/                             # 생성된 시각 에셋 폴더
    ├── concepts/                                # 콘셉트 아트
    │   ├── character_용기사_아키라_0.png
    │   └── ...
    └── scenes/                                  # 시네마틱 비디오 클립
        ├── scene_01.mp4
        └── ...
```

## 📄 라이선스

이 프로젝트는 [MIT License](LICENSE)를 따릅니다.
