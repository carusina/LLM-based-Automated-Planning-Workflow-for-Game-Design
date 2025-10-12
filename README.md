# LLM 기반 지능형 게임 기획 및 시각화 자동화 파이프라인

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

LLM(Large Language Model)의 추론 능력을 다단계로 활용하여, 단일 아이디어로부터 체계적인 게임 디자인 문서(GDD)를 생성하고, GDD의 전체 맥락을 이해하여 통일성 있는 콘셉트 아트까지 자동으로 시각화하는 지능형 워크플로우입니다.

## 🚀 핵심 기능 (Key Features)

이 프로젝트는 단순한 텍스트 생성을 넘어, 여러 LLM 에이전트가 유기적으로 협력하여 기획의 깊이를 더하고 시각적 결과물까지 만들어내는 자동화된 파이프라인을 구축하는 것을 목표로 합니다.

-   **지능형 GDD 생성**:
    -   **What:** 사용자의 추상적인 아이디어를 입력받아, 게임의 핵심 시스템, 캐릭터, 레벨, 스토리 등을 포함하는 체계적인 GDD를 생성합니다.
    -   **Why:** 산발적인 아이디어를 전문적인 기획 문서 형식으로 구조화하여, 후속 개발 단계의 기반을 마련합니다.

-   **2-Step 메타데이터 추출 파이프라인**:
    -   **What:** 생성된 GDD 텍스트를 다시 LLM이 분석하여, 캐릭터, 레벨, 아이템 등의 정보를 정확한 JSON 형식의 메타데이터로 추출합니다.
    -   **Why:** 정규식(Regex) 등 기존 방식의 불안정성을 해결하고, LLM의 문맥 이해 능력을 통해 복잡한 문서에서도 높은 정확도로 구조화된 데이터를 확보하는 안정적인 파이프라인입니다.

-   **AI 기반 콘셉트 아트 생성**:
    -   **What:** 추출된 메타데이터를 기반으로 Gemini API를 호출하여, 각 캐릭터와 레벨의 설명에 맞는 고품질 콘셉트 아트를 자동으로 생성합니다.
    -   **Why:** 기획 단계에서 텍스트로만 존재하던 아이디어를 즉시 시각화하여, 팀원 간의 비전 공유를 돕고 기획의 완성도를 높입니다.

-   **동적 아트 스타일 가이드 (AI Art Director)**:
    -   **What:** GDD 텍스트 전체의 맥락과 분위기를 AI가 스스로 분석하여, 게임의 고유한 비주얼 테마(예: `dark medieval fantasy, post-apocalyptic, ancient technology`)를 나타내는 '아트 스타일 가이드'를 동적으로 생성합니다.
    -   **Why:** 고정된 아트 스타일의 한계를 극복하고, GDD의 서사와 생성되는 모든 이미지의 화풍을 완벽하게 일치시켜 프로젝트의 시각적 통일성을 극대화합니다.

-   **사용자 정의 아트 스타일**:
    -   **What:** 사용자가 `--art-style` 명령어를 통해 AI의 판단을 덮어쓰고, `pixel art` 등 원하는 특정 화풍을 직접 지정할 수 있습니다.
    -   **Why:** 시스템의 자율성과 사용자의 창의적인 제어 사이의 균형을 맞추어, 다양한 시각적 탐색이 가능한 유연성을 제공합니다.

-   **지식 그래프 연동 (확장 예정)**:
    -   **What:** 생성된 모든 메타데이터를 Neo4j와 같은 그래프 데이터베이스에 저장하여, 엔티티 간의 복잡한 관계(예: 'A 캐릭터가 B 아이템을 사용하여 C 레벨의 D 몬스터를 처치')를 모델링합니다.
    -   **Why:** 단순 키-값 저장을 넘어, 데이터의 관계성을 기반으로 한 고급 질의응답 및 RAG(Retrieval-Augmented Generation) 시스템 구축의 기반을 마련하는 확장성을 제공합니다.

## ⚙️ 아키텍처 워크플로우

본 프로젝트는 여러 LLM 에이전트가 체인처럼 연결되어, 단계적으로 정보를 구체화하고 풍부하게 만드는 다단계 파이프라인 구조를 가집니다.

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
[3. GeminiImageGenerator (이미지 생성)]
   |
   +--- [메타데이터 기반 '주제/연출 프롬프트' 생성] ----> (4차 LLM 호출: 프롬프트 엔지니어)
   |
   +--- [최종 프롬프트 조합 및 생성] ----> (Gemini Image API 호출)
        |
        V
[ 최종 결과물: GDD 문서 + 메타데이터 JSON + 콘셉트 아트 이미지들 ]
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

### 3. `.env` 파일 설정
프로젝트 루트에 `.env` 파일을 생성하고, API 키를 설정합니다. **본 프로젝트의 모든 기능을 사용하려면 `GEMINI_API_KEY`가 반드시 필요합니다.**

```env
# .env

# Google Gemini API Key (텍스트 분석, 동적 스타일 생성, 이미지 생성에 필수)
GEMINI_API_KEY="여기에_당신의_Gemini_API_키를_입력하세요"

# (선택) 텍스트 생성에 다른 모델을 사용하고 싶을 경우
# OPENAI_API_KEY="sk-..."
```

## 🎮 사용 방법 (Usage)

모든 기능은 `main.py`의 `gdd` 명령어를 통해 실행됩니다.

### 기본 사용법
-   `--idea`, `--genre`, `--target`, `--concept` 4가지 인자를 필수로 전달합니다.
-   `--generate-images` 플래그를 추가하면 GDD 생성 후 이미지 시각화가 진행됩니다.
-   아래와 같이 실행하면, AI가 GDD 내용을 분석하여 최적의 **동적 아트 스타일**을 자동으로 적용합니다.

```bash
python main.py gdd --idea "고대 드래곤의 힘을 이어받은 용기사가 타락한 왕국을 구원하는 여정" --genre "에픽 판타지 액션 RPG" --target "판타지 RPG 팬" --concept "실시간 검술과 드래곤 마법을 조합한 전투" --generate-images
```

### 사용자 정의 아트 스타일 적용
`--art-style` 옵션을 사용하여 AI의 판단을 덮어쓰고 원하는 스타일을 직접 지정할 수 있습니다.

```bash
python main.py gdd --idea "고대 드래곤의 힘을 이어받은 용기사가 타락한 왕국을 구원하는 여정" --genre "에픽 판타지 액션 RPG" --target "판타지 RPG 팬" --concept "실시간 검술과 드래곤 마법을 조합한 전투" --generate-images --art-style "pixel art, 16-bit, vibrant, style of chrono trigger, detailed characters"
```

## 📂 출력 구조

실행 완료 후, `output/` 디렉토리에 타임스탬프 기반으로 결과물이 저장됩니다.

```
output/
├── GDD_20251004_193000.md         # 생성된 게임 디자인 문서
├── GDD_20251004_193000_meta.json  # 추출된 메타데이터
└── 20251004_193000/               # 생성된 콘셉트 아트 폴더
    ├── character_용기사_아키라_0.png
    ├── character_마법사_엘라라_0.png
    └── level_무너진_왕성_0.png
```

## 📄 라이선스

이 프로젝트는 [MIT License](LICENSE)를 따릅니다.
