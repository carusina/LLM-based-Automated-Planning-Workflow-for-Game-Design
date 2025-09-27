#!/usr/bin/env python3
"""
Game Design Document(GDD) & Storyline Generator

LLM을 활용한 게임 기획 문서 및 스토리라인 생성 도구
"""

import os
import sys
import argparse
import logging
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# 상대 경로 임포트 지원
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# 모델 모듈 임포트
from models.game_design_generator import GameDesignGenerator
from models.storyline_generator import StorylineGenerator
from models.document_generator import DocumentGenerator

# Neo4j 없이 실행하기 위한 임시 클래스
class MockKnowledgeGraphService:
    def __init__(self):
        self.logger = logging.getLogger("KnowledgeGraphService")
        self.logger.info("Initialized Mock Neo4j connection (neo4j 모듈 없음)")
    
    def create_game_node(self, *args, **kwargs):
        self.logger.info("Mock: 게임 노드 생성 (실제로는 생성되지 않음)")
        return "mock-id"
    
    def add_levels(self, *args, **kwargs):
        self.logger.info("Mock: 레벨 정보 추가 (실제로는 추가되지 않음)")
    
    def create_chapters(self, *args, **kwargs):
        self.logger.info("Mock: 챗터 정보 추가 (실제로는 추가되지 않음)")
    
    def close(self):
        self.logger.info("Mock: Neo4j 연결 종료 (실제로는 종료되지 않음)")

# Neo4j 의존성 처리
try:
    from models.knowledge_graph_service import KnowledgeGraphService
    from models.graph_rag import GraphRAG
    neo4j_available = True
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("Neo4j 모듈을 찾을 수 없습니다. 임시 Mock 서비스를 사용합니다.")
    KnowledgeGraphService = MockKnowledgeGraphService
    GraphRAG = None
    neo4j_available = False

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_gdd(args):
    """
    GDD 생성 기능
    
    Args:
        args: 명령줄 인자
    """
    logger.info("🔄 게임 디자인 문서(GDD) 생성 시작...")
    
    try:
        # 1. GDD 생성
        gdd_generator = GameDesignGenerator()
        gdd_full_text = gdd_generator.generate_gdd(
            idea=args.idea,
            genre=args.genre,
            target=args.target,
            concept=args.concept
        )
        
        # 출력 디렉토리 설정
        output_dir = os.path.join(BASE_DIR, 'output')
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 파일명 설정 (타임스탬프 포함)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"GDD_{timestamp}"
        
        # 2. GDD 마크다운 파일 저장
        doc_generator = DocumentGenerator(output_dir=output_dir)
        formats = args.formats.split(',') if args.formats else ["md"]
        saved_files = {}
        
        for fmt in formats:
            try:
                path = doc_generator.save_document(filename, gdd_full_text, fmt.strip())
                saved_files[fmt] = path
                logger.info(f"✅ {fmt.upper()} 형식으로 저장됨: {path}")
            except Exception as e:
                logger.error(f"❌ {fmt} 형식 저장 실패: {e}")

        # 3. 메타데이터 추출 및 저장
        logger.info("🔄 GDD로부터 메타데이터 추출 시작...")
        kg_service = KnowledgeGraphService()
        metadata = kg_service.extract_metadata_from_gdd(gdd_full_text)

        if not metadata:
            logger.error("❌ 메타데이터 추출에 실패하여 이후 프로세스를 중단합니다.")
            return

        # 추가 정보 병합
        metadata["id"] = timestamp
        metadata["created_at"] = str(datetime.now())
        metadata["file_paths"] = saved_files

        try:
            meta_path = os.path.join(output_dir, f"{filename}_meta.json")
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 메타데이터 저장됨: {meta_path}")
        except Exception as e:
            logger.error(f"❌ 메타데이터 저장 실패: {e}")

        # 4. 지식 그래프 생성 (--skip-graph 옵션이 없는 경우)
        if not args.skip_graph and neo4j_available:
            try:
                logger.info("🔄 지식 그래프 생성 중...")
                
                # 게임 메타데이터 구성
                game_metadata_for_graph = {
                    "title": metadata.get("title", "Untitled Game"),
                    "genre": metadata.get("genre", ""),
                    "target_audience": metadata.get("target_audience", ""),
                    "concept": metadata.get("concept", "")
                }
                
                # 지식 그래프 저장
                game_id = kg_service.create_game_node(game_metadata_for_graph)
                
                # 레벨 정보가 있으면 그래프에 추가
                if "levels" in metadata and metadata["levels"]:
                    try:
                        kg_service.add_levels(game_id, metadata["levels"])
                        logger.info(f"✅ {len(metadata['levels'])} 레벨 정보를 그래프에 추가했습니다.")
                    except Exception as e:
                        logger.error(f"❌ 레벨 정보 그래프 추가 실패: {e}")
                
                logger.info("✅ 지식 그래프 생성 완료")
                
            except Exception as e:
                logger.error(f"❌ 지식 그래프 생성 실패: {e}")
            finally:
                kg_service.close()

        logger.info("✅ GDD 생성 및 처리 완료!")
        
    except Exception as e:
        logger.error(f"❌ GDD 생성 중 오류 발생: {e}")
        sys.exit(1)

def generate_storyline(args):
    """
    스토리라인 생성 기능
    
    Args:
        args: 명령줄 인자
    """
    logger.info("🔄 스토리라인 생성 시작...")
    
    try:
        # GDD 파일 확인
        if not os.path.isfile(args.gdd_file):
            logger.error(f"❌ GDD 파일을 찾을 수 없습니다: {args.gdd_file}")
            sys.exit(1)
        
        # GDD 파일 읽기
        with open(args.gdd_file, 'r', encoding='utf-8') as f:
            gdd_content = f.read()
        
        # GDD 메타데이터 파일 경로 찾기
        gdd_path = os.path.abspath(args.gdd_file)
        gdd_dir = os.path.dirname(gdd_path)
        gdd_filename = os.path.basename(gdd_path)
        gdd_basename, _ = os.path.splitext(gdd_filename)
        
        # 메타데이터 파일 경로
        meta_filename = f"{gdd_basename}_meta.json"
        meta_path = os.path.join(gdd_dir, meta_filename)
        
        # 캐릭터 관계 및 레벨 디자인 정보 초기화
        character_relationships = {}
        level_designs = []
        
        # 메타데이터 파일이 있는 경우 읽기
        if os.path.isfile(meta_path):
            try:
                with open(meta_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # 캐릭터 관계 정보 추출
                character_relationships = metadata.get("relationships", {})
                
                # 레벨 디자인 정보 추출
                level_designs = metadata.get("levels", [])
                
                logger.info(f"✅ 메타데이터 파일에서 {len(character_relationships)} 캐릭터 관계와 {len(level_designs)} 레벨 디자인 정보를 로드했습니다.")
            except Exception as e:
                logger.warning(f"⚠️ 메타데이터 파일 로드 실패: {e}")
        
        # GDD 생성기 초기화
        gdd_generator = GameDesignGenerator()
        
        # GDD 핵심 요소 추출
        gdd_core = gdd_generator.extract_gdd_core(gdd_content)
        
        # 캐릭터 관계 및 레벨 디자인 정보가 없는 경우 추출 시도
        if not character_relationships:
            character_relationships = gdd_generator.extract_character_relationships(gdd_content)
            logger.info(f"📝 GDD 내용에서 {len(character_relationships)} 캐릭터 관계 정보를 추출했습니다.")
        
        if not level_designs:
            level_designs = gdd_generator.extract_level_design(gdd_content)
            logger.info(f"📝 GDD 내용에서 {len(level_designs)} 레벨 디자인 정보를 추출했습니다.")
        
        # 스토리라인 생성기 초기화
        storyline_generator = StorylineGenerator()
        
        # 스토리라인 생성
        storyline_result = storyline_generator.generate_storyline(
            gdd_core=gdd_core,
            chapters=args.chapters,
            character_relationships=character_relationships,
            level_designs=level_designs
        )
        
        # 출력 디렉토리 설정
        output_dir = os.path.join(BASE_DIR, 'output')
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 문서 생성기 초기화
        doc_generator = DocumentGenerator(output_dir=output_dir)
        
        # 파일명 설정 (타임스탬프 포함)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        gdd_basename = os.path.splitext(os.path.basename(args.gdd_file))[0]
        filename = f"Storyline_{gdd_basename}_{timestamp}"
        
        # 파일 저장
        formats = args.formats.split(',') if args.formats else ["md"]
        saved_files = {}
        
        for fmt in formats:
            try:
                path = doc_generator.save_document(filename, storyline_result["full_text"], fmt.strip())
                saved_files[fmt] = path
                logger.info(f"✅ {fmt.upper()} 형식으로 저장됨: {path}")
            except Exception as e:
                logger.error(f"❌ {fmt} 형식 저장 실패: {e}")
        
        # 메타데이터 저장
        try:
            # 메타데이터 구성
            metadata = {
                "id": timestamp,
                "gdd_id": gdd_basename,
                "chapters": args.chapters,
                "created_at": str(datetime.now()),
                "file_paths": saved_files,
                "chapter_data": storyline_result.get("chapters", [])
            }
            
            # 메타데이터 저장
            meta_path = os.path.join(output_dir, f"{filename}_meta.json")
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 메타데이터 저장됨: {meta_path}")
        except Exception as e:
            logger.error(f"❌ 메타데이터 저장 실패: {e}")
        
        # 지식 그래프 업데이트 (--skip-graph 옵션이 없는 경우)
        if not args.skip_graph:
            try:
                logger.info("🔄 지식 그래프 업데이트 중...")
                kg_service = KnowledgeGraphService()
                
                # 챕터 정보 추출
                graph_data = storyline_generator.extract_graph_data(storyline_result["chapters"])
                
                # 퀘스트 정보 추출 (새로 추가된 기능)
                quest_data = storyline_generator.extract_quest_data(storyline_result["chapters"])
                logger.info(f"📝 스토리라인에서 {len(quest_data)} 퀘스트 정보를 추출했습니다.")
                
                # 지식 그래프에 챕터 추가
                kg_service.create_chapters(graph_data)
                
                # TODO: 퀘스트 정보 그래프에 추가하는 로직 구현
                
                logger.info("✅ 지식 그래프 업데이트 완료")
                
            except Exception as e:
                logger.error(f"❌ 지식 그래프 업데이트 실패: {e}")
        
        logger.info("✅ 스토리라인 생성 완료!")
        
    except Exception as e:
        logger.error(f"❌ 스토리라인 생성 중 오류 발생: {e}")
        sys.exit(1)

def run_web_interface(args):
    """
    웹 인터페이스 실행
    
    Args:
        args: 명령줄 인자
    """
    try:
        from web.api import app
        logger.info(f"🌐 웹 인터페이스 시작 (포트: {args.port})...")
        app.run(host=args.host, port=args.port, debug=args.debug)
    except ImportError:
        logger.error("❌ 웹 인터페이스 모듈을 찾을 수 없습니다.")
        logger.error("Flask 설치 여부 확인: pip install flask")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 웹 인터페이스 실행 중 오류 발생: {e}")
        sys.exit(1)

def main():
    """메인 함수"""
    # 명령줄 인자 파서 설정
    parser = argparse.ArgumentParser(
        description="게임 디자인 문서(GDD) 및 스토리라인 생성 도구"
    )
    subparsers = parser.add_subparsers(dest='command', help='명령')
    
    # GDD 생성 명령
    gdd_parser = subparsers.add_parser('gdd', help='게임 디자인 문서(GDD) 생성')
    gdd_parser.add_argument('--idea', required=True, help='게임 아이디어')
    gdd_parser.add_argument('--genre', required=True, help='게임 장르')
    gdd_parser.add_argument('--target', required=True, help='타겟 오디언스')
    gdd_parser.add_argument('--concept', required=True, help='핵심 컨셉')
    gdd_parser.add_argument('--formats', help='출력 형식 (예: md,pdf,txt)')
    gdd_parser.add_argument('--skip-graph', action='store_true', help='지식 그래프 생성 건너뛰기')
    
    # 스토리라인 생성 명령
    storyline_parser = subparsers.add_parser('storyline', help='스토리라인 생성')
    storyline_parser.add_argument('--gdd-file', required=True, help='GDD 파일 경로')
    storyline_parser.add_argument('--chapters', type=int, default=5, help='챕터 수')
    storyline_parser.add_argument('--formats', help='출력 형식 (예: md,pdf,txt)')
    storyline_parser.add_argument('--skip-graph', action='store_true', help='지식 그래프 업데이트 건너뛰기')
    
    # 웹 인터페이스 명령
    web_parser = subparsers.add_parser('web', help='웹 인터페이스 실행')
    web_parser.add_argument('--host', default='127.0.0.1', help='호스트 주소')
    web_parser.add_argument('--port', type=int, default=5000, help='포트 번호')
    web_parser.add_argument('--debug', action='store_true', help='디버그 모드 활성화')
    
    # 명령줄 인자 파싱
    args = parser.parse_args()
    
    # 명령에 따라 기능 실행
    if args.command == 'gdd':
        generate_gdd(args)
    elif args.command == 'storyline':
        generate_storyline(args)
    elif args.command == 'web':
        run_web_interface(args)
    else:
        parser.print_help()
        sys.exit(0)

if __name__ == '__main__':
    main()
