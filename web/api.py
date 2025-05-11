"""
웹 인터페이스 API 서버

React 프론트엔드와 Python 백엔드를 연결하는 Flask 기반 API 서버
"""

import os
import sys
import json
import uuid
import logging
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# 부모 디렉토리를 시스템 경로에 추가 (상대 경로 지원)
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

# 모델 모듈 임포트
from models.game_design_generator import GameDesignGenerator
from models.storyline_generator import StorylineGenerator
from models.document_generator import DocumentGenerator
from models.knowledge_graph_service import KnowledgeGraphService
from models.graph_rag import GraphRAG

# 앱 초기화
app = Flask(__name__, static_folder='build')
CORS(app)  # CORS 지원 활성화

# GDD와 스토리라인 저장용 디렉토리 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# 공유 서비스 인스턴스
doc_generator = DocumentGenerator(output_dir=OUTPUT_DIR)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.route('/api/generate_gdd', methods=['POST'])
def generate_gdd():
    """
    GDD 생성 API 엔드포인트
    
    요청 본문:
    {
        "idea": "게임 아이디어",
        "genre": "게임 장르",
        "target": "타겟 오디언스",
        "concept": "게임 컨셉"
    }
    
    응답:
    {
        "gdd": "생성된 GDD 내용",
        "id": "생성된 GDD ID",
        "downloads": {
            "md": "/downloads/gdd/{id}.md",
            "pdf": "/downloads/gdd/{id}.pdf",
            "txt": "/downloads/gdd/{id}.txt"
        }
    }
    """
    data = request.json
    
    try:
        # 필수 필드 검증
        required_fields = ['idea', 'genre', 'target', 'concept']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"필수 필드가 누락되었습니다: {field}"}), 400
        
        # GDD 생성
        logger.info(f"GDD 생성 요청: {data['idea'][:30]}...")
        gdd_generator = GameDesignGenerator()
        gdd_result = gdd_generator.generate_gdd(
            idea=data['idea'],
            genre=data['genre'],
            target=data['target'],
            concept=data['concept']
        )
        
        # GDD를 출력 디렉토리에 저장
        gdd_id = str(uuid.uuid4())[:8]  # 고유 ID 생성
        file_prefix = f"GDD_{gdd_id}"
        
        # 다양한 형식으로 저장
        files = doc_generator.save_multiple_formats(
            file_prefix, 
            gdd_result["full_text"], 
            formats=["md", "pdf", "txt"]
        )
        
        # 지식 그래프 생성
        try:
            # 게임 제목 추출
            game_title = ""
            for line in gdd_result["full_text"].split('\n')[:10]:
                if "Game Title:" in line:
                    game_title = line.split(':', 1)[1].strip()
                    break
            
            # 메타데이터 구성
            metadata = {
                "id": gdd_id,
                "title": game_title or f"Game {gdd_id}",
                "genre": data['genre'],
                "target_audience": data['target'],
                "concept": data['concept'],
                "created_at": str(datetime.now()),
                "file_paths": files,
                "relationships": gdd_result.get("relationships", {}),
                "levels": gdd_result.get("levels", [])
            }
            
            # 메타데이터 저장
            meta_path = os.path.join(OUTPUT_DIR, f"{file_prefix}_meta.json")
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # 지식 그래프 생성
            kg_service = KnowledgeGraphService()
            
            # 게임 메타데이터 구성
            game_metadata = {
                "title": game_title or f"Game {gdd_id}",
                "genre": data['genre'],
                "target_audience": data['target'],
                "concept": data['concept'],
                "character_relationships": gdd_result.get("relationships", {})
            }
            
            # 지식 그래프 저장
            kg_service.create_game_metadata(game_metadata)
            
        except Exception as e:
            logger.warning(f"지식 그래프 생성 경고: {e}")
        
        # 다운로드 링크 구성
        downloads = {}
        for fmt, path in files.items():
            if path:
                filename = os.path.basename(path)
                downloads[fmt] = f"/api/downloads/{filename}"
        
        # 응답 구성
        response = {
            "gdd": gdd_result["full_text"],
            "id": gdd_id,
            "downloads": downloads
        }
        
        logger.info(f"GDD 생성 완료: {gdd_id}")
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"GDD 생성 오류: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate_storyline', methods=['POST'])
def generate_storyline():
    """
    스토리라인 생성 API 엔드포인트
    
    요청 본문:
    {
        "gddId": "GDD ID",
        "chapters": 챕터 수(정수)
    }
    
    응답:
    {
        "storyline": "생성된 스토리라인 내용",
        "id": "생성된 스토리라인 ID",
        "downloads": {
            "md": "/downloads/storyline/{id}.md",
            "pdf": "/downloads/storyline/{id}.pdf",
            "txt": "/downloads/storyline/{id}.txt"
        }
    }
    """
    data = request.json
    
    try:
        # 필수 필드 검증
        if not data.get('gddId'):
            return jsonify({"error": "GDD ID가 필요합니다"}), 400
        
        chapters = int(data.get('chapters', 5))
        if chapters < 1 or chapters > 20:
            return jsonify({"error": "챕터 수는 1에서 20 사이여야 합니다"}), 400
        
        # GDD 메타데이터 로드
        gdd_meta_files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith(f"GDD_{data['gddId']}") and f.endswith("_meta.json")]
        
        if not gdd_meta_files:
            return jsonify({"error": "지정된 GDD를 찾을 수 없습니다"}), 404
        
        gdd_meta_path = os.path.join(OUTPUT_DIR, gdd_meta_files[0])
        
        with open(gdd_meta_path, 'r', encoding='utf-8') as f:
            gdd_meta = json.load(f)
        
        # GDD 내용 로드
        gdd_md_path = gdd_meta.get('file_paths', {}).get('md')
        if not gdd_md_path or not os.path.exists(gdd_md_path):
            return jsonify({"error": "GDD 파일을 찾을 수 없습니다"}), 404
        
        with open(gdd_md_path, 'r', encoding='utf-8') as f:
            gdd_content = f.read()
        
        # GDD 생성기 초기화
        gdd_generator = GameDesignGenerator()
        
        # GDD 핵심 요소 추출
        gdd_core = gdd_generator.extract_gdd_core(gdd_content)
        
        # 캐릭터 관계 정보 가져오기
        character_relationships = gdd_meta.get("relationships", {})
        
        # 레벨 디자인 정보 가져오기
        level_designs = gdd_meta.get("levels", [])
        
        # 정보가 없으면 GDD에서 추출 시도
        if not character_relationships:
            character_relationships = gdd_generator.extract_character_relationships(gdd_content)
            logger.info(f"GDD에서 {len(character_relationships)} 캐릭터 관계 추출")
        
        if not level_designs:
            level_designs = gdd_generator.extract_level_design(gdd_content)
            logger.info(f"GDD에서 {len(level_designs)} 레벨 디자인 정보 추출")
        
        # 스토리라인 생성
        logger.info(f"스토리라인 생성 요청: GDD={data['gddId']}, 챕터={chapters}")
        storyline_generator = StorylineGenerator()
        storyline_result = storyline_generator.generate_storyline(
            gdd_core=gdd_core,
            chapters=chapters,
            character_relationships=character_relationships,
            level_designs=level_designs
        )
        
        # 스토리라인을 출력 디렉토리에 저장
        storyline_id = str(uuid.uuid4())[:8]  # 고유 ID 생성
        file_prefix = f"Storyline_{data['gddId']}_{storyline_id}"
        
        # 다양한 형식으로 저장
        files = doc_generator.save_multiple_formats(
            file_prefix, 
            storyline_result["full_text"], 
            formats=["md", "pdf", "txt"]
        )
        
        # 지식 그래프 업데이트
        try:
            kg_service = KnowledgeGraphService()
            
            # 챕터 정보 추출
            graph_data = storyline_generator.extract_graph_data(storyline_result["chapters"])
            
            # 퀘스트 정보 추출
            quest_data = storyline_generator.extract_quest_data(storyline_result["chapters"])
            
            # 지식 그래프에 챕터 추가
            kg_service.create_chapters(graph_data)
            
            # TODO: 퀘스트 정보 그래프에 추가하는 로직 구현
            
        except Exception as e:
            logger.warning(f"지식 그래프 업데이트 경고: {e}")
        
        # 메타데이터 파일 저장
        metadata = {
            "id": storyline_id,
            "gdd_id": data['gddId'],
            "chapters": chapters,
            "created_at": str(datetime.now()),
            "file_paths": files,
            "chapter_data": storyline_result.get("chapters", [])
        }
        
        metadata_path = os.path.join(OUTPUT_DIR, f"{file_prefix}_meta.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        # 다운로드 링크 구성
        downloads = {}
        for fmt, path in files.items():
            if path:
                filename = os.path.basename(path)
                downloads[fmt] = f"/api/downloads/{filename}"
        
        # 응답 구성
        response = {
            "storyline": storyline_result["full_text"],
            "id": storyline_id,
            "downloads": downloads
        }
        
        logger.info(f"스토리라인 생성 완료: {storyline_id}")
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"스토리라인 생성 오류: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/available_gdds', methods=['GET'])
def get_available_gdds():
    """
    사용 가능한 GDD 목록 조회 API 엔드포인트
    
    응답:
    {
        "gdds": [
            {
                "id": "GDD ID",
                "title": "GDD 제목",
                "genre": "게임 장르",
                "created_at": "생성 일시"
            },
            ...
        ]
    }
    """
    try:
        gdds = []
        
        # 메타데이터 파일 검색
        meta_files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith("GDD_") and f.endswith("_meta.json")]
        
        for meta_file in meta_files:
            meta_path = os.path.join(OUTPUT_DIR, meta_file)
            
            try:
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                
                # 기본 정보만 추출
                gdd_info = {
                    "id": meta.get("id", ""),
                    "title": meta.get("title", "Untitled Game"),
                    "genre": meta.get("genre", ""),
                    "target_audience": meta.get("target_audience", ""),
                    "concept": meta.get("concept", ""),
                    "created_at": meta.get("created_at", ""),
                    "has_levels": len(meta.get("levels", [])) > 0,
                    "has_relationships": len(meta.get("relationships", {})) > 0
                }
                
                gdds.append(gdd_info)
            except Exception as e:
                logger.warning(f"메타데이터 파일 로드 실패: {meta_file} - {e}")
        
        # 최신순 정렬
        gdds.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return jsonify({"gdds": gdds})
    
    except Exception as e:
        logger.error(f"GDD 목록 조회 오류: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/available_storylines', methods=['GET'])
def get_available_storylines():
    """
    사용 가능한 스토리라인 목록 조회 API 엔드포인트
    
    요청 파라미터:
    ?gddId=xxx (선택적) - 특정 GDD의 스토리라인만 조회
    
    응답:
    {
        "storylines": [
            {
                "id": "스토리라인 ID",
                "gdd_id": "관련 GDD ID",
                "chapters": 챕터 수,
                "created_at": "생성 일시"
            },
            ...
        ]
    }
    """
    try:
        gdd_id = request.args.get('gddId')
        storylines = []
        
        # 메타데이터 파일 검색
        meta_files = [
            f for f in os.listdir(OUTPUT_DIR) 
            if f.startswith("Storyline_") and f.endswith("_meta.json") and
            (gdd_id is None or f"GDD_{gdd_id}" in f)
        ]
        
        for meta_file in meta_files:
            meta_path = os.path.join(OUTPUT_DIR, meta_file)
            
            try:
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                
                # 기본 정보만 추출
                storyline_info = {
                    "id": meta.get("id", ""),
                    "gdd_id": meta.get("gdd_id", ""),
                    "chapters": meta.get("chapters", 0),
                    "created_at": meta.get("created_at", ""),
                    "chapter_count": len(meta.get("chapter_data", []))
                }
                
                storylines.append(storyline_info)
            except Exception as e:
                logger.warning(f"메타데이터 파일 로드 실패: {meta_file} - {e}")
        
        # 최신순 정렬
        storylines.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return jsonify({"storylines": storylines})
    
    except Exception as e:
        logger.error(f"스토리라인 목록 조회 오류: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/gdd/<gdd_id>', methods=['GET'])
def get_gdd_details(gdd_id):
    """
    특정 GDD의 상세 정보 조회 API 엔드포인트
    
    응답:
    {
        "id": "GDD ID",
        "title": "GDD 제목",
        "genre": "게임 장르",
        ...
        "content": "GDD 내용",
        "downloads": {
            "md": "/downloads/xxx.md",
            ...
        }
    }
    """
    try:
        # 메타데이터 파일 검색
        meta_files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith(f"GDD_{gdd_id}") and f.endswith("_meta.json")]
        
        if not meta_files:
            return jsonify({"error": "지정된 GDD를 찾을 수 없습니다"}), 404
        
        meta_path = os.path.join(OUTPUT_DIR, meta_files[0])
        
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        # GDD 내용 로드
        gdd_md_path = meta.get('file_paths', {}).get('md')
        if not gdd_md_path or not os.path.exists(gdd_md_path):
            return jsonify({"error": "GDD 파일을 찾을 수 없습니다"}), 404
        
        with open(gdd_md_path, 'r', encoding='utf-8') as f:
            gdd_content = f.read()
        
        # 다운로드 링크 구성
        downloads = {}
        for fmt, path in meta.get('file_paths', {}).items():
            if path:
                filename = os.path.basename(path)
                downloads[fmt] = f"/api/downloads/{filename}"
        
        # 응답 구성
        response = {
            "id": meta.get("id", ""),
            "title": meta.get("title", "Untitled Game"),
            "genre": meta.get("genre", ""),
            "target_audience": meta.get("target_audience", ""),
            "concept": meta.get("concept", ""),
            "created_at": meta.get("created_at", ""),
            "content": gdd_content,
            "relationships": meta.get("relationships", {}),
            "levels": meta.get("levels", []),
            "downloads": downloads
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"GDD 상세 정보 조회 오류: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/storyline/<storyline_id>', methods=['GET'])
def get_storyline_details(storyline_id):
    """
    특정 스토리라인의 상세 정보 조회 API 엔드포인트
    
    응답:
    {
        "id": "스토리라인 ID",
        "gdd_id": "관련 GDD ID",
        "chapters": 챕터 수,
        "content": "스토리라인 내용",
        "chapter_data": 챕터별 상세 정보,
        "downloads": {
            "md": "/downloads/xxx.md",
            ...
        }
    }
    """
    try:
        # 메타데이터 파일 검색
        meta_files = [f for f in os.listdir(OUTPUT_DIR) if "Storyline_" in f and f"_{storyline_id}_meta.json" in f]
        
        if not meta_files:
            return jsonify({"error": "지정된 스토리라인을 찾을 수 없습니다"}), 404
        
        meta_path = os.path.join(OUTPUT_DIR, meta_files[0])
        
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        # 스토리라인 내용 로드
        storyline_md_path = meta.get('file_paths', {}).get('md')
        if not storyline_md_path or not os.path.exists(storyline_md_path):
            return jsonify({"error": "스토리라인 파일을 찾을 수 없습니다"}), 404
        
        with open(storyline_md_path, 'r', encoding='utf-8') as f:
            storyline_content = f.read()
        
        # 다운로드 링크 구성
        downloads = {}
        for fmt, path in meta.get('file_paths', {}).items():
            if path:
                filename = os.path.basename(path)
                downloads[fmt] = f"/api/downloads/{filename}"
        
        # 응답 구성
        response = {
            "id": meta.get("id", ""),
            "gdd_id": meta.get("gdd_id", ""),
            "chapters": meta.get("chapters", 0),
            "created_at": meta.get("created_at", ""),
            "content": storyline_content,
            "chapter_data": meta.get("chapter_data", []),
            "downloads": downloads
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"스토리라인 상세 정보 조회 오류: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/downloads/<path:filename>', methods=['GET'])
def download_file(filename):
    """
    파일 다운로드 API 엔드포인트
    """
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

@app.route('/api/graph/<entity_type>', methods=['GET'])
def get_graph_data(entity_type):
    """
    지식 그래프 데이터 조회 API 엔드포인트
    
    요청 파라미터:
    ?id=xxx (선택적) - 특정 엔티티 ID
    
    응답:
    {
        "nodes": [...],
        "edges": [...]
    }
    """
    try:
        entity_id = request.args.get('id')
        
        kg_service = KnowledgeGraphService()
        
        if entity_type == 'characters':
            data = kg_service.get_characters()
        elif entity_type == 'locations':
            data = kg_service.get_locations()
        elif entity_type == 'chapters':
            if entity_id:
                data = kg_service.get_chapter_details(int(entity_id))
            else:
                data = []  # 모든 챕터 조회 로직 필요
        else:
            return jsonify({"error": "지원하지 않는 엔티티 유형입니다"}), 400
        
        return jsonify(data)
    
    except Exception as e:
        logger.error(f"그래프 데이터 조회 오류: {e}")
        return jsonify({"error": str(e)}), 500

# SPA용 캐치올 라우트
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
