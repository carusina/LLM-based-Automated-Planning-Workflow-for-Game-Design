# 챕터 지식 그래프 변환기 (Chapter to Knowledge Graph)

이 도구는 게임 기획서(마크다운 파일)에서 챕터 개요 정보를 추출하여 Neo4j 지식 그래프로 변환합니다.

## 기능 개요

- 게임 기획서에서 챕터 정보(제목, 목표, 위치, 사건, 도전 과제) 추출
- 캐릭터 정보 추출
- Neo4j 지식 그래프 생성
- 챕터 간 관계, 캐릭터와 이벤트 간 관계 등 다양한 관계 정의

## 요구 사항

- Python 3.8 이상
- Neo4j 데이터베이스 (로컬 또는 클라우드)

## 지식 그래프 변환 방법

### 기본 사용법

```bash
python chapter_to_knowledge_graph.py
```

이 명령은 기본적으로 output 폴더에서 가장 최근의 마크다운 파일을 찾아 처리합니다.

### 특정 파일 처리

```bash
python chapter_to_knowledge_graph.py --input=path/to/game_design.md
```

### 데이터베이스 초기화 옵션

```bash
python chapter_to_knowledge_graph.py --clear
```

`--clear` 옵션은 실행 전에 Neo4j 데이터베이스의 모든 노드와 관계를 삭제합니다.

### 디버그 모드

```bash
python chapter_to_knowledge_graph.py --debug
```

`--debug` 옵션은 추출 과정의 상세 정보를 출력합니다.

## 데이터베이스 연결 설정

`.env` 파일에 Neo4j 연결 정보를 설정하세요:

```
NEO4J_URI=neo4j+s://your-neo4j-uri
NEO4J_USER=your-username
NEO4J_PASSWORD=your-password
```

## 데이터 확인하기

저장된 데이터를 확인하려면 다음 명령을 실행하세요:

```bash
python check_neo4j_data.py
```

## 지식 그래프 스키마

이 도구는 다음과 같은 노드와 관계를 생성합니다:

### 노드

- **Game**: 게임 정보
- **Chapter**: 챕터 정보 (제목, 번호, 설명)
- **Goal**: 챕터의 목표
- **Location**: 챕터의 주요 위치
- **Event**: 챕터에서 발생하는 주요 사건
- **Challenge**: 챕터의 도전 과제
- **Character**: 게임의 캐릭터

### 관계

- `(:Game)-[:HAS_CHAPTER]->(:Chapter)`: 게임과 챕터 관계
- `(:Game)-[:HAS_CHARACTER]->(:Character)`: 게임과 캐릭터 관계
- `(:Chapter)-[:HAS_GOAL]->(:Goal)`: 챕터와 목표 관계
- `(:Chapter)-[:TAKES_PLACE_AT]->(:Location)`: 챕터와 위치 관계
- `(:Chapter)-[:CONTAINS_EVENT]->(:Event)`: 챕터와 사건 관계
- `(:Chapter)-[:PRESENTS_CHALLENGE]->(:Challenge)`: 챕터와 도전 과제 관계
- `(:Chapter)-[:FOLLOWED_BY]->(:Chapter)`: 챕터 간 순서 관계
- `(:Character)-[:PARTICIPATES_IN]->(:Event)`: 캐릭터와 사건 참여 관계
- `(:Location)-[:LOCATED_ON]->(:Location)`: 위치 간 관계 (예: 시설이 행성 위에 있음)

## 유용한 Neo4j 쿼리 예시

### 모든 노드 조회

```cypher
MATCH (n) RETURN n LIMIT 100;
```

### 게임별 챕터 조회

```cypher
MATCH (g:Game)-[:HAS_CHAPTER]->(c:Chapter)
RETURN g.title AS game, c.number AS chapter, c.title AS title
ORDER BY g.title, c.number;
```

### 챕터별 목표 조회

```cypher
MATCH (c:Chapter)-[:HAS_GOAL]->(g:Goal)
RETURN c.title AS chapter, collect(g.description) AS goals;
```

### 캐릭터가 참여한 이벤트 조회

```cypher
MATCH (ch:Character {name: 'Alex Ryn'})-[:PARTICIPATES_IN]->(e:Event)<-[:CONTAINS_EVENT]-(c:Chapter)
RETURN ch.name AS character, e.name AS event, c.title AS chapter
ORDER BY c.number;
```

### 챕터 간 경로 조회

```cypher
MATCH path = (c1:Chapter)-[:FOLLOWED_BY*]->(c2:Chapter)
WHERE NOT (c1)<-[:FOLLOWED_BY]-()
RETURN path;
```

## 예상되는 마크다운 형식

이 도구는 다음과 같은 형식의 마크다운을 기대합니다:

```markdown
# 게임 제목

...

### 챕터 개요

#### 챕터 1: 챕터 제목
챕터 설명

**목표:**
- 목표 1
- 목표 2

**주요 위치:**
- 위치 1
- 위치 2

**주요 사건:**
- 사건 1
- 사건 2

**도전 과제:**
- 도전 과제 1
- 도전 과제 2

#### 챕터 2: 챕터 제목
...
```

## 주의 사항

- 이 도구는 특정 형식의 게임 기획서를 처리하도록 설계되었습니다.
- 마크다운 형식이 다르면 제대로 작동하지 않을 수 있습니다.
- 대용량 데이터 처리 시 메모리 사용량을 고려하세요.
