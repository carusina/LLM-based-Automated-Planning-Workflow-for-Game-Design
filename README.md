# 게임 기획을 위한 LLM 기반 기획 자동화

대규모 언어 모델(LLM)을 활용하여 게임 기획을 자동화하는 웹 애플리케이션입니다. 사용자가 기본적인 게임 컨셉만 입력하면 AI가 상세한 게임 기획서를 자동으로 생성합니다.

## 주요 기능

- **완전한 게임 기획서 생성**: 게임 컨셉, 게임플레이 메커니즘, 내러티브, 아트 디렉션, 기술 사양, 수익화 계획, 개발 로드맵을 포함한 종합적인 게임 기획서를 자동 생성합니다.
- **경쟁 분석**: 입력한 경쟁 게임에 대한 분석을 통해 차별화 포인트를 도출합니다.
- **다양한 문서 형식 지원**: 마크다운(.md), 워드 문서(.docx), PDF(.pdf) 형식으로 기획서를 다운로드할 수 있습니다.
- **사용자 친화적 인터페이스**: 직관적인 웹 인터페이스를 통해 손쉽게 기획서를 생성하고 결과를 확인할 수 있습니다.

## 기술 스택

- **백엔드**: Python, Flask
- **프론트엔드**: HTML, CSS, JavaScript, Bootstrap 5
- **AI/ML**: OpenAI GPT, Anthropic Claude
- **문서 생성**: Markdown, python-docx, FPDF

## 설치 방법

### 요구사항

- Python 3.8 이상
- OpenAI API 키
- Anthropic API 키 (선택 사항)

### 설치 단계

1. 리포지토리를 복제합니다:
   ```bash
   git clone https://github.com/carusina/LLM-based-Automated-Planning-Workflow-for-Game-Design.git
   cd LLM-based-Automated-Planning-Workflow-for-Game-Design
   ```

2. 가상 환경을 생성하고 활성화합니다:
   ```bash
   # 가상 환경 생성
   python3 -m venv venv
   
   # 가상 환경 활성화 (Windows)
   venv\Scripts\activate
   
   # 가상 환경 활성화 (macOS/Linux)
   source venv/bin/activate
   ```

3. 필요한 패키지를 설치합니다:
   ```bash
   pip install -r requirements.txt
   ```

4. `.env` 파일을 생성하고 API 키를 설정합니다:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here (선택사항)
   ```

## 사용 방법

1. 애플리케이션을 실행합니다:
   ```bash
   python app.py
   ```

2. 웹 브라우저에서 `http://localhost:5000`으로 접속합니다.

3. 게임 컨셉, 장르, 플랫폼 등 기본 정보를 입력합니다.

4. 심화 정보(게임플레이 메커니즘, 아트 스타일, 스토리 요소)와 경쟁 게임을 선택적으로 입력합니다.

5. "게임 기획서 생성" 버튼을 클릭하고 결과를 확인합니다.

6. 원하는 형식(마크다운, 워드, PDF)으로 기획서를 다운로드할 수 있습니다.

## 시스템 구조

- **app.py**: 메인 애플리케이션 파일 및 API 엔드포인트
- **models/llm_service.py**: LLM API 통합을 위한 서비스 클래스
- **models/game_design_generator.py**: 게임 기획 생성 로직
- **models/storyline_generator.py**: 게임 스토리라인 생성 로직
- **models/document_generator.py**: 다양한 형식의 문서 생성 로직
- **templates/index.html**: 웹 인터페이스 템플릿

## 사용 예시

1. 기본 게임 컨셉 입력:
   ```
   공룡 캐릭터가 주인공인 2D 플랫포머 게임으로, 시간 여행 요소가 있어 다양한 시대를 탐험하며 퍼즐을 푸는 게임
   ```

2. 결과로 생성되는 게임 기획서는 다음과 같은 섹션을 포함합니다:
   - 게임 개요 및 컨셉
   - 핵심 게임플레이 메커니즘
   - 스토리 및 세계관
   - 캐릭터 설정
   - 레벨 디자인 방향
   - 아트 스타일 및 사운드 디자인
   - 수익화 전략

## 기여 방법

1. 이 리포지토리를 포크합니다.
2. 새 브랜치를 생성합니다 (e.g.,`git checkout -b feature/amazing-feature`).
3. 변경사항을 커밋합니다 (e.g., `git commit -m 'Add some amazing feature'`).
4. 브랜치에 푸시합니다 (e.g., `git push origin feature/amazing-feature`).
5. Pull Request를 생성합니다.

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.