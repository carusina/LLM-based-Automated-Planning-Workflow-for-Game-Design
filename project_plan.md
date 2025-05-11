# Project Plan: Game Design Document & Storyline Generator

## 개요
이 프로젝트는 LLM(Large Language Model)을 활용하여 게임 디자인 문서(GDD)와 스토리라인을 생성하고, 이를 지식 그래프로 변환하여 저장하는 시스템입니다.

## 기능 요약
1. 게임 기획 문서(GDD) 생성
2. 챕터별 스토리라인 생성
3. 지식 그래프 변환 및 저장 (Neo4j)
4. Graph-RAG를 활용한 문서 업데이트
5. 웹 인터페이스를 통한 입력 처리

## 작업 상태

### 완료된 작업
- ✅ 기본 디렉토리 구조 생성
- ✅ 모델 모듈 구조화 및 개선
  - ✅ llm_service.py: 여러 LLM 지원 (OpenAI, Anthropic)
  - ✅ game_design_generator.py: GDD 생성 기능 개선
  - ✅ storyline_generator.py: 스토리라인 생성 및 파싱 기능 개선
  - ✅ knowledge_graph_service.py: Neo4j 그래프 변환 기능 확장
  - ✅ graph_rag.py: 그래프 기반 RAG 구현
  - ✅ document_generator.py: 다양한 출력 형식 지원 (MD, PDF, TXT)
- ✅ 웹 인터페이스 개발 (React)
  - ✅ 웹 프론트엔드 구현
  - ✅ Flask 백엔드 API 구현
- ✅ CLI 인터페이스 강화
- ✅ 문서화 (README.md, 주석)
- ✅ 환경 설정 (.env 추가)

### 업그레이드 하이라이트
1. **다중 LLM 지원**
   - OpenAI 뿐만 아니라 Anthropic Claude 등 다양한 LLM 지원
   - 팩토리 패턴을 사용한 LLM 클라이언트 추상화

2. **GDD 및 스토리라인 생성 고도화**
   - 캐릭터 관계 추출 및 활용
   - 챕터 정보 구조화 파싱

3. **지식 그래프 기능 강화**
   - 캐릭터, 장소, 종족 간 관계 모델링
   - 챕터 순서와 스토리 요소 연결

4. **Graph-RAG 구현**
   - 지식 그래프 컨텍스트를 활용한 문서 업데이트
   - 일관성 유지를 위한 관계 분석

5. **확장된 문서 생성 기능**
   - PDF 출력 지원 (Pandoc 활용)
   - 다양한 형식으로 동시 저장

6. **웹 인터페이스 개발**
   - 직관적인 React 폼 구성
   - RESTful API 설계

## 향후 작업
- Neo4j 그래프 시각화 개선
- 제안된 스토리 요소 평가 기능
- 다국어 지원
- 유닛 테스트 및 통합 테스트 작성
- 사용자 인증 및 프로젝트 관리 기능

## 기술 스택
- Python 3.8+
- OpenAI API & Anthropic API
- Neo4j
- React
- Flask
- Pandoc (PDF 변환용)

## 설치 및 실행
자세한 내용은 README.md 파일을 참조하세요.
