# LLM 기반 게임 기획 및 콘셉트 아트 자동 생성기

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

LLM(Large Language Model)을 활용하여 간단한 아이디어만으로 게임 디자인 문서(GDD) 전문과 그에 맞는 캐릭터 및 배경 콘셉트 아트를 자동으로 생성하는 파이프라인입니다.

## 🚀 핵심 기능

- **GDD 자동 생성**: 게임 아이디어, 장르, 타겟, 핵심 컨셉 네 가지 정보만으로 체계적인 게임 디자인 문서를 생성합니다.
- **AI 콘셉트 아트 생성**: 생성된 GDD의 메타데이터(캐릭터, 레벨)를 기반으로 Google Gemini API를 호출하여 고품질 콘셉트 아트를 자동으로 생성합니다.
- **지능형 메타데이터 추출**: GDD 텍스트를 다시 LLM으로 분석하여, 구조화된 JSON 형식의 메타데이터(등장인물, 레벨, 아이템 등)를 추출합니다.
- **지식 그래프 연동 (선택 사항)**: 추출된 메타데이터를 Neo4j 데이터베이스에 저장하여 관계를 시각화하고 복잡한 쿼리로 분석할 수 있습니다.
- **강력한 CLI 인터페이스**: 모든 기능은 스크립트화 및 자동화에 용이한 커맨드 라인 인터페이스를 통해 제어됩니다.
- **확장 가능한 LLM 지원**: Gemini, OpenAI, Anthropic 등 다양한 LLM 제공자를 유연하게 변경하며 사용할 수 있습니다.

## ⚙️ 아키텍처 및 데이터 흐름

프로젝트는 다음과 같은 순서로 작업을 처리합니다.

1.  **입력**: 사용자가 `main.py`에 게임 아이디어, 장르, 타겟, 컨셉을 인자로 전달합니다.
2.  **GDD 생성**: `GameDesignGenerator`가 LLM(`llm_service`)을 호출하여 GDD 텍스트 초안을 생성합니다.
3.  **메타데이터 추출**: `KnowledgeGraphService`가 생성된 GDD 텍스트를 다시 LLM(`llm_service`)에 보내 캐릭터, 레벨 등의 정형화된 JSON 데이터를 추출합니다.
4.  **콘셉트 아트 생성**: `GeminiImageGenerator`가 추출된 메타데이터를 기반으로 각 항목(캐릭터, 레벨)에 대한 이미지 생성 프롬프트를 만들고, Gemini 이미지 생성 API를 호출하여 콘셉트 아트를 생성합니다.
5.  **결과물 저장**: 모든 결과물(GDD 마크다운, 메타데이터 JSON, 이미지 파일)은 `output/` 디렉토리 아래에 타임스탬프 기반으로 체계적으로 저장됩니다.

## 🛠️ 설치 방법

### 1. 저장소 복제

```bash
git clone https://github.com/carusina/LLM-based-Automated-Planning-Workflow-for-Game-Design.git
cd LLM-based-Automated-Planning-Workflow-for-Game-Design
```

### 2. 가상 환경 생성 및 활성화

```bash
# 가상 환경 생성
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 의존성 설치

프로젝트에 필요한 모든 라이브러리를 `requirements.txt` 파일을 통해 설치합니다.

```bash
pip install -r requirements.txt
```

### 4. `.env` 파일 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고, 아래 내용을 참고하여 API 키를 입력합니다. **이미지 생성을 위해서는 `GEMINI_API_KEY`가 반드시 필요합니다.**

```env
# .env

# Google Gemini API Key (텍스트 및 이미지 생성에 필수)
GEMINI_API_KEY="여기에_당신의_Gemini_API_키를_입력하세요"

# (선택) 다른 LLM 제공자 API 키
# OPENAI_API_KEY="..."
# ANTHROPIC_API_KEY="..."

# (선택) Neo4j 데이터베이스 연결 정보
# NEO4J_URI="bolt://localhost:7687"
# NEO4J_USER="neo4j"
# NEO4J_PASSWORD="your_neo4j_password"
```

## 🎮 사용법

모든 기능은 `main.py`를 통해 실행됩니다. 핵심 명령어는 `gdd`입니다.

### 기본 명령어 형식

```bash
python main.py gdd --idea "..." --genre "..." --target "..." --concept "..." --generate-images
```

- `--idea`: 게임의 핵심 아이디어
- `--genre`: 게임의 장르
- `--target`: 타겟 유저
- `--concept`: 핵심 플레이 방식
- `--generate-images`: 이 플래그를 추가해야 콘셉트 아트가 생성됩니다.

### 예시: 에픽 판타지 RPG 생성

아래는 바로 복사해서 실행해볼 수 있는 예시 명령어입니다.

```bash
python main.py gdd --idea "고대 드래곤의 힘을 이어받은 용기사가 타락한 왕국을 구원하기 위해 전설의 유물을 찾아 떠나는 여정" --genre "에픽 판타지 액션 RPG" --target "판타지 RPG 팬, '왕좌의 게임'이나 '반지의 제왕' 같은 서사시 팬" --concept "실시간 검술과 드래곤의 마법을 조합한 화려한 전투, 동료들과 함께 거대한 보스를 공략하는 레이드 시스템" --generate-images
```

## 📂 출력 구조

명령 실행 후, `output/` 디렉토리에 다음과 같은 구조로 결과물이 저장됩니다.

```
output/
├── GDD_20250927_183000.md         # 생성된 게임 디자인 문서
├── GDD_20250927_183000_meta.json  # 추출된 메타데이터
└── 20250927_183000/               # 생성된 콘셉트 아트 폴더
    ├── character_용기사_아키라_0.png
    ├── character_마법사_엘라라_0.png
    ├── level_무너진_왕성_0.png
    └── ...
```

## 📄 라이선스

이 프로젝트는 [MIT License](LICENSE)를 따릅니다.