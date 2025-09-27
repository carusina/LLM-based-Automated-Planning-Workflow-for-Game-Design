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
from models.llm_service import LLMService
from models.local_image_generator import GeminiImageGenerator

# Neo4j 없이 실행하기 위한 임시 클래스
class MockKnowledgeGraphService:
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger("KnowledgeGraphService")
        self.logger.info("Initialized Mock Neo4j connection (neo4j 모듈 없음)")
    
    def create_graph_from_metadata(self, *args, **kwargs):
        self.logger.info("Mock: 그래프 생성 (실제로는 생성되지 않음)")

    def extract_metadata_from_gdd(self, *args, **kwargs):
        self.logger.warning("Mock: 메타데이터 추출 (실제로는 추출되지 않음)")
        return {}

    def close(self):
        self.logger.info("Mock: Neo4j 연결 종료 (실제로는 종료되지 않음)")

# Neo4j 의존성 처리
try:
    from models.knowledge_graph_service import KnowledgeGraphService
    from models.graph_rag import GraphRAG
    neo4j_available = True
except ImportError:
    # logger가 아직 설정되지 않았을 수 있으므로 기본 로거 사용
    logging.warning("Neo4j 모듈을 찾을 수 없습니다. 임시 Mock 서비스를 사용합니다.")
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
    logger.info("🔄 게임 디자인 문서(GDD) 생성 프로세스 시작...")
    
    try:
        # 1. [공통] LLM 서비스 객체 생성 (모든 하위 모듈이 공유)
        # --text-model 인자가 있으면 해당 모델을, 없으면 .env의 기본 설정을 사용
        llm_service = LLMService(model_name=args.text_model)
        logger.info(f"Text generation model set to: {llm_service.client.model_name}")

        # 2. GDD 생성
        logger.info("📄 GDD 텍스트 생성 중...")
        gdd_generator = GameDesignGenerator(llm_service=llm_service)
        gdd_full_text = gdd_generator.generate_gdd(
            idea=args.idea,
            genre=args.genre,
            target=args.target,
            concept=args.concept
        )
        
        # 출력 디렉토리 및 파일명 설정
        output_dir = os.path.join(BASE_DIR, 'output')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"GDD_{timestamp}"
        
        # 3. GDD 문서 파일 저장
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

        # 4. 메타데이터 추출 및 저장
        logger.info("📊 GDD로부터 메타데이터 추출 시작...")
        kg_service = KnowledgeGraphService(llm_service=llm_service)
        metadata = kg_service.extract_metadata_from_gdd(gdd_full_text)

        if not metadata:
            logger.error("❌ 메타데이터 추출에 실패하여 이후 프로세스를 중단합니다.")
            return

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

        # 5. 이미지 생성 (--generate-images 옵션이 있는 경우)
        if args.generate_images:
            logger.info("🎨 GDD 메타데이터 기반 이미지 생성 시작...")
            try:
                # llm_service는 프롬프트 엔지니어링에 필요하므로 재사용
                image_generator = GeminiImageGenerator(llm_service=llm_service)
                image_output_dir = os.path.join(output_dir, timestamp)
                
                generated_paths = image_generator.generate_images_from_metadata(
                    metadata=metadata,
                    output_dir=image_output_dir
                )
                
                if generated_paths:
                    logger.info(f"✅ {len(generated_paths)}개의 이미지를 성공적으로 생성했습니다: {image_output_dir}")
                else:
                    logger.warning("⚠️ 이미지 생성은 완료되었지만, 저장된 파일이 없습니다.")

            except Exception as e:
                logger.error(f"❌ 이미지 생성 중 오류 발생: {e}", exc_info=True)

        # 6. 지식 그래프 생성 (--skip-graph 옵션이 없는 경우)
        if not args.skip_graph and neo4j_available:
            try:
                logger.info("🕸️ 지식 그래프 생성 중...")
                # kg_service 인스턴스는 이미 위에서 생성되었으므로 재사용
                kg_service.create_graph_from_metadata(metadata)
            except Exception as e:
                logger.error(f"❌ 지식 그래프 생성 실패: {e}", exc_info=True)
            finally:
                if kg_service:
                    kg_service.close()

        logger.info("🎉 GDD 생성 및 모든 후속 처리 완료!")
        
    except Exception as e:
        logger.error(f"❌ GDD 생성 중 심각한 오류 발생: {e}", exc_info=True)
        sys.exit(1)

# storyline 및 web 기능는 기존과 동일하게 유지 (생략)

def generate_storyline(args):
    logger.info("스토리라인 생성 기능은 현재 수정 범위에 포함되지 않습니다.")
    pass

def run_web_interface(args):
    logger.info("웹 인터페이스 기능은 현재 수정 범위에 포함되지 않습니다.")
    pass

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="게임 디자인 문서(GDD) 및 스토리라인 생성 도구"
    )
    subparsers = parser.add_subparsers(dest='command', help='명령', required=True)
    
    # GDD 생성 명령
    gdd_parser = subparsers.add_parser('gdd', help='게임 디자인 문서(GDD) 생성')
    gdd_parser.add_argument('--idea', required=True, help='게임 아이디어')
    gdd_parser.add_argument('--genre', required=True, help='게임 장르')
    gdd_parser.add_argument('--target', required=True, help='타겟 오디언스')
    gdd_parser.add_argument('--concept', required=True, help='핵심 컨셉')
    gdd_parser.add_argument('--formats', help='출력 형식 (예: md,pdf,txt)')
    gdd_parser.add_argument('--text-model', help='텍스트 생성을 위한 LLM 모델 이름 지정 (예: gemini-1.5-pro-latest)')
    gdd_parser.add_argument('--skip-graph', action='store_true', help='지식 그래프 생성 건너뛰기')
    gdd_parser.add_argument('--generate-images', action='store_true', help='메타데이터를 기반으로 콘셉트 아트 이미지 생성')

    # 스토리라인 생성 명령 (기존과 동일)
    storyline_parser = subparsers.add_parser('storyline', help='스토리라인 생성')
    storyline_parser.add_argument('--gdd-file', required=True, help='GDD 파일 경로')
    # ... (이하 생략)

    # 웹 인터페이스 명령 (기존과 동일)
    web_parser = subparsers.add_parser('web', help='웹 인터페이스 실행')
    # ... (이하 생략)

    args = parser.parse_args()
    
    if args.command == 'gdd':
        generate_gdd(args)
    elif args.command == 'storyline':
        # generate_storyline(args) # 현재는 비활성화
        parser.print_help()
    elif args.command == 'web':
        # run_web_interface(args) # 현재는 비활성화
        parser.print_help()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
