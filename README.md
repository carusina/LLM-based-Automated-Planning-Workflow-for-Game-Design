# 게임 디자인 문서 & 스토리라인 생성기

LLM(Large Language Model)을 활용하여 게임 디자인 문서(GDD)와 스토리라인을 생성하고, 
지식 그래프로 변환하여 저장하는 도구입니다.

## 주요 기능

- **게임 디자인 문서(GDD) 생성**: 게임 아이디어, 장르, 타겟 오디언스, 컨셉 정보를 바탕으로 포괄적인 게임 디자인 문서를 생성합니다.
- **스토리라인 생성**: GDD 정보를 바탕으로 챕터별 상세 스토리라인을 생성합니다.
- **지식 그래프 변환**: 생성된 문서와 스토리를 Neo4j 지식 그래프로 변환하여 저장합니다.
- **Graph-RAG**: 지식 그래프를 활용한 RAG(Retrieval Augmented Generation)로 문서 업데이트를 지원합니다.
- **다양한 출력 형식**: Markdown, PDF, Text 등 다양한 형식으로 결과물을 저장합니다.
- **웹 인터페이스**: 사용하기 쉬운 웹 UI를 제공합니다.

## 디렉토리 구조

```
SW_Project/
├── models/         # Python 스크립트
│   ├── llm_service.py
│   ├── game_design_generator.py
│   ├── storyline_generator.py
│   ├── knowledge_graph_service.py
│   ├── graph_rag.py
│   └── document_generator.py
├── templates/      # 문서 템플릿
│   └── GDD.md
├── output/         # 생성된 결과물 저장
├── web/            # 웹 입력 폼 (React)
│   ├── src/
│   │   ├── components/
│   │   │   ├── GameDesignForm.js
│   │   │   └── StorylineForm.js
│   │   ├── App.js
│   │   └── App.css
│   └── api.py      # Flask 백엔드
├── .env            # 환경 설정 (LLM·Neo4j 연결 정보)
├── main.py         # CLI 진입점
├── requirements.txt
└── README.md
```

## 설치 방법

### 요구 사항

- Python 3.8+
- Neo4j 데이터베이스
- Node.js & npm (웹 인터페이스용)

### 설치 단계

1. 저장소 클론

```bash
git clone https://github.com/yourusername/SW_Project.git
cd SW_Project
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

3. Python 의존성 설치

```bash
pip install -r requirements.txt
```

4. `.env` 파일 설정

```
# LLM API 설정
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Neo4j 연결 정보
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# 출력 설정
DEFAULT_OUTPUT_FORMAT=md
```

5. (선택) 웹 인터페이스 설치

```bash
cd web
npm install
npm run build
```

## 사용 방법

### CLI로 사용하기

1. GDD 생성

```bash
python main.py gdd --idea "전략 RPG 게임 아이디어" --genre "RPG" --target "10대 및 20대" --concept "판타지 세계관의 턴 기반 전략 게임"
```

2. 스토리라인 생성

```bash
python main.py storyline --gdd-file ./output/GDD_20250503_123456.md --chapters 5
```

3. 웹 인터페이스 실행

```bash
python main.py web
```

### 웹 인터페이스로 사용하기

1. 서버 실행

```bash
python main.py web
```

2. 웹 브라우저에서 `http://localhost:5000` 접속

3. 웹 폼에서 정보 입력 후 생성 버튼 클릭

## 고급 기능

### 다양한 LLM 사용하기

기본적으로 OpenAI의 API를 사용하지만, `.env` 파일에서 다른 LLM을 설정할 수 있습니다:

```
DEFAULT_LLM_PROVIDER=anthropic
DEFAULT_ANTHROPIC_MODEL=claude-3-opus-20240229
```

### PDF 출력하기

PDF 출력을 위해서는 Pandoc이 필요합니다:

```bash
# macOS
brew install pandoc

# Ubuntu/Debian
sudo apt-get install pandoc

# Windows
# https://pandoc.org/installing.html에서 인스톨러 다운로드
```

이후 다음과 같이 출력 형식을 지정할 수 있습니다:

```bash
python main.py gdd [...설정...] --formats md,pdf,txt
```

### 지식 그래프 활용하기

Neo4j 브라우저(`http://localhost:7474`)에 접속하여 생성된 그래프를 탐색할 수 있습니다.

일반적인 쿼리 예시:

```cypher
// 모든 캐릭터 조회
MATCH (c:Character) RETURN c

// 챕터와 등장인물 관계 조회
MATCH (chapter:Chapter)-[:FEATURES]->(character:Character)
RETURN chapter.title, chapter.order, collect(character.name) as characters
ORDER BY chapter.order

// 적대적 관계인 캐릭터 찾기
MATCH (c1:Character)-[:HOSTILE_WITH]->(c2:Character)
RETURN c1.name, c2.name
```

## 라이선스

MIT License

## 기여하기

이슈 및 PR은 언제나 환영합니다. 주요 변경 사항은 먼저 이슈를 열어 논의해주세요.
