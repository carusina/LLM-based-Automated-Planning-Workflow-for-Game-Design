# app.py
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
from models.llm_service import LLMService
from models.game_design_generator import GameDesignGenerator
from models.document_generator import DocumentGenerator
from models.storyline_generator import StorylineGenerator
from models.knowledge_graph_service import KnowledgeGraphService
from models.graph_rag import GraphRAG
from chapter_to_knowledge_graph import ChapterKnowledgeGraphGenerator

# 환경 변수 로드
load_dotenv()

# Flask 앱 초기화
app = Flask(__name__)

# 출력 디렉토리 설정
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

# OpenAI 클라이언트 초기화
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# API 키 설정
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

# LLM 서비스 초기화
llm_service = LLMService(
    openai_api_key=os.getenv("OPENAI_API_KEY"), 
    anthropic_api_key=anthropic_api_key
)

# 게임 기획 생성기 및 문서 생성기 초기화
game_design_generator = GameDesignGenerator(llm_service)
document_generator = DocumentGenerator()

# Neo4j 지식 그래프 서비스 초기화
knowledge_graph_service = KnowledgeGraphService()

# 챕터 지식 그래프 생성기 초기화
chapter_graph_generator = ChapterKnowledgeGraphGenerator()

# GraphRAG 초기화
graph_rag = GraphRAG(llm_service, knowledge_graph_service)

# 스토리라인 생성기 초기화
storyline_generator = StorylineGenerator(llm_service)

@app.route('/')
def index():
    """메인 페이지 렌더링"""
    return render_template('index.html')

@app.route('/view/<filename>')
def view_document(filename):
    """기획서 보기 페이지 렌더링"""
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 파일명에서 확장자 제거
        base_filename = os.path.splitext(filename)[0]
        
        return render_template('view.html', 
                              content=content, 
                              filename=base_filename,
                              full_filename=filename)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/edit/<filename>')
def edit_document(filename):
    """기획서 편집 페이지 렌더링"""
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 파일명에서 확장자 제거
        base_filename = os.path.splitext(filename)[0]
        
        # Neo4j에서 기존 데이터 불러오기
        graph_data = knowledge_graph_service.get_graph_overview()
        
        return render_template('editor.html', 
                              content=content, 
                              filename=base_filename,
                              full_filename=filename,
                              graph_data=graph_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents')
def list_documents():
    """출력 디렉토리에 있는 문서 목록 반환"""
    try:
        # 마크다운 파일만 필터링
        documents = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.md')]
        documents.sort(key=lambda f: os.path.getmtime(os.path.join(OUTPUT_DIR, f)), reverse=True)
        
        # 각 파일에 대한 메타데이터 추가
        doc_list = []
        for doc in documents:
            file_path = os.path.join(OUTPUT_DIR, doc)
            with open(file_path, 'r', encoding='utf-8') as f:
                # 첫 줄은 제목으로 간주
                first_line = f.readline().strip()
                title = first_line.replace('#', '').strip() if first_line.startswith('#') else doc
            
            # 메타데이터 추가
            doc_list.append({
                'filename': doc,
                'title': title,
                'last_modified': os.path.getmtime(file_path),
                'size': os.path.getsize(file_path)
            })
        
        return jsonify(doc_list)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
@app.route('/api/chapter/update', methods=['POST'])
def update_chapter():
    """챕터 내용 업데이트 API 엔드포인트"""
    data = request.json
    
    print(f"[API 디버그] 챕터 업데이트 요청 데이터: {data.keys()}")
    
    if not data or 'filename' not in data or 'chapter_number' not in data:
        return jsonify({'error': '필수 매개변수가 누락되었습니다.'}), 400
    
    filename = data['filename']
    chapter_number = data['chapter_number']
    chapter_title = data.get('chapter_title', f'챕터 {chapter_number}')
    outline_content = data.get('outline', '')    # 챕터 개요 내용
    details_content = data.get('details', '')    # 챕터 상세 내용
    
    print(f"[API 디버그] 챕터 업데이트 - 파일명: {filename}, 챕터 번호: {chapter_number}")
    print(f"[API 디버그] 개요 길이: {len(outline_content)}, 상세 내용 길이: {len(details_content)}")
    
    if not filename.endswith('.md'):
        filename += '.md'
    
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404
    
    try:
        # 파일 읽기
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # 1. 챕터 개요 섹션 업데이트 (outline_content 사용)
        if outline_content:
            # 스토리라인 섹션 찾기
            storyline_pattern = r"## 스토리라인[\s\S]*?(?=^## |\Z)"
            storyline_match = re.search(storyline_pattern, file_content, re.MULTILINE)
            
            if storyline_match:
                storyline_content = storyline_match.group(0)
                
                # 챕터 개요 섹션 찾기
                chapter_outline_pattern = r"### 챕터 개요[\s\S]*?(?=### |## |$)"
                chapter_outline_match = re.search(chapter_outline_pattern, storyline_content, re.MULTILINE)
                
                if chapter_outline_match:
                    # 챕터 개요 섹션이 있는 경우
                    chapter_outline_content = chapter_outline_match.group(0)
                    
                    # 해당 챕터가 이미 있는지 확인
                    chapter_pattern = rf"#### 챕터 {chapter_number}:[\s\S]*?(?=#### 챕터|### |## |$)"
                    chapter_match = re.search(chapter_pattern, chapter_outline_content, re.DOTALL)
                    
                    if chapter_match:
                        # 기존 챕터 업데이트 - 여기가 핵심입니다!
                        old_chapter_content = chapter_match.group(0)
                        updated_outline = chapter_outline_content.replace(old_chapter_content, outline_content)
                        updated_storyline = storyline_content.replace(chapter_outline_content, updated_outline)
                        file_content = file_content.replace(storyline_content, updated_storyline)
                    else:
                        # 새 챕터 추가
                        new_chapter_content = f"\n\n{outline_content}"
                        updated_outline = chapter_outline_content + new_chapter_content
                        updated_storyline = storyline_content.replace(chapter_outline_content, updated_outline)
                        file_content = file_content.replace(storyline_content, updated_storyline)
                else:
                    # 챕터 개요 섹션이 없는 경우 추가
                    new_section = f"\n\n### 챕터 개요\n\n{outline_content}"
                    updated_storyline = storyline_content + new_section
                    file_content = file_content.replace(storyline_content, updated_storyline)
            else:
                # 스토리라인 섹션이 없는 경우 추가
                new_section = f"\n\n## 스토리라인\n\n### 챕터 개요\n\n{outline_content}"
                file_content += new_section
        
        # 2. 챕터 상세 내용 섹션 업데이트 (details_content 사용)
        if details_content:
            # 스토리라인 섹션 찾기 (다시 찾아야 함 - 위에서 변경됐을 수 있음)
            storyline_pattern = r"## 스토리라인[\s\S]*?(?=^## |\Z)"
            storyline_match = re.search(storyline_pattern, file_content, re.MULTILINE)
            
            if storyline_match:
                storyline_content = storyline_match.group(0)
                
                # 챕터 상세 내용 섹션 찾기
                chapter_details_pattern = r"### 챕터 상세 내용[\s\S]*?(?=### |## |$)"
                chapter_details_match = re.search(chapter_details_pattern, storyline_content, re.MULTILINE)
                
                if chapter_details_match:
                    # 챕터 상세 내용 섹션이 있는 경우
                    chapter_details_content = chapter_details_match.group(0)
                    
                    # 해당 챕터가 이미 있는지 확인
                    chapter_pattern = rf"#### 챕터 {chapter_number}:[\s\S]*?(?=#### 챕터|### |## |$)"
                    chapter_match = re.search(chapter_pattern, chapter_details_content, re.DOTALL)
                    
                    if chapter_match:
                        # 기존 챕터 업데이트 - 여기도 핵심입니다!
                        old_chapter_content = chapter_match.group(0)
                        updated_details = chapter_details_content.replace(old_chapter_content, details_content)
                        updated_storyline = storyline_content.replace(chapter_details_content, updated_details)
                        file_content = file_content.replace(storyline_content, updated_storyline)
                    else:
                        # 새 챕터 추가
                        new_chapter_content = f"\n\n{details_content}"
                        updated_details = chapter_details_content + new_chapter_content
                        updated_storyline = storyline_content.replace(chapter_details_content, updated_details)
                        file_content = file_content.replace(storyline_content, updated_storyline)
                else:
                    # 챕터 상세 내용 섹션이 없는 경우
                    
                    # 챕터 개요 섹션 찾기
                    chapter_outline_pattern = r"### 챕터 개요[\s\S]*?(?=### |## |$)"
                    chapter_outline_match = re.search(chapter_outline_pattern, storyline_content, re.MULTILINE)
                    
                    if chapter_outline_match:
                        # 챕터 개요 섹션 이후에 챕터 상세 내용 섹션 추가
                        chapter_outline_content = chapter_outline_match.group(0)
                        new_section = f"\n\n### 챕터 상세 내용\n\n{details_content}"
                        updated_storyline = storyline_content.replace(chapter_outline_content, chapter_outline_content + new_section)
                        file_content = file_content.replace(storyline_content, updated_storyline)
                    else:
                        # 챕터 개요 섹션도 없는 경우 (이미 앞에서 추가했을 수 있음)
                        new_section = f"\n\n### 챕터 상세 내용\n\n{details_content}"
                        updated_storyline = storyline_content + new_section
                        file_content = file_content.replace(storyline_content, updated_storyline)
            else:
                # 스토리라인 섹션이 없는 경우 (이미 앞에서 추가했을 수 있음)
                storyline_pattern = r"## 스토리라인[\s\S]*?(?=^## |\Z)"
                storyline_match = re.search(storyline_pattern, file_content, re.MULTILINE)
                
                if storyline_match:
                    # 스토리라인 섹션이 이미 추가된 경우
                    storyline_content = storyline_match.group(0)
                    new_section = f"\n\n### 챕터 상세 내용\n\n{details_content}"
                    updated_storyline = storyline_content + new_section
                    file_content = file_content.replace(storyline_content, updated_storyline)
                else:
                    # 스토리라인 섹션도 없는 경우 (이상한 경우, 이미 앞에서 추가했을 것)
                    pass
        
        # 파일 업데이트
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        # Neo4j 데이터 업데이트
        success = chapter_graph_generator.process_design_document(file_path, clear_db=True)
        
        print(f"[API 디버그] 챕터 업데이트 완료: 챕터 {chapter_number}")
        return jsonify({
            'success': True,
            'message': f'챕터 {chapter_number} 업데이트 완료 (지식 그래프 업데이트: {success})'
        })
    
    except Exception as e:
        print(f"[디버그] 챕터 업데이트 오류: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chapter/delete', methods=['DELETE'])
def delete_chapter():
    """챕터 삭제 API 엔드포인트"""
    data = request.json
    
    if not data or 'filename' not in data or 'chapter_number' not in data:
        return jsonify({'error': '필수 매개변수가 누락되었습니다.'}), 400
    
    filename = data['filename']
    chapter_number = data['chapter_number']
    
    if not filename.endswith('.md'):
        filename += '.md'
    
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404
    
    try:
        # 파일 읽기
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 해당 챕터 찾기
        chapter_pattern = fr"#### 챕터 {chapter_number}: [^\n]+[\s\S]*?(?=#### 챕터|### |## |$)"
        chapter_match = re.search(chapter_pattern, content)
        
        if not chapter_match:
            return jsonify({'error': f'챕터 {chapter_number}을 찾을 수 없습니다.'}), 404
        
        # 챕터 제거
        chapter_content = chapter_match.group(0)
        content = content.replace(chapter_content, '')
        
        # 멸량한 줄 정리
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 파일 업데이트
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Neo4j 데이터 업데이트
        knowledge_graph_service.delete_chapter(filename, chapter_number)
        
        return jsonify({
            'success': True,
            'message': f'챕터 {chapter_number} 삭제 완료'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chapter/suggest', methods=['POST'])
def suggest_chapter_content():
    """챕터 내용 추천 API 엔드포인트 (GraphRAG 기반)"""
    data = request.json
    
    if not data or 'filename' not in data or 'chapter_number' not in data:
        return jsonify({'error': '필수 매개변수가 누락되었습니다.'}), 400
    
    filename = data['filename']
    chapter_number = data['chapter_number']
    chapter_title = data.get('chapter_title', '')
    guideline = data.get('guideline', '')
    
    if not filename.endswith('.md'):
        filename += '.md'
    
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404
    
    try:
        # 파일에서 게임 정보 로드
        game_design = _load_game_design(file_path)
        
        # GraphRAG를 사용하여 추천 내용 생성 (개요와 상세 내용 모두)
        print(f"[API 디버그] GraphRAG 추천 요청: 챕터 {chapter_number}, 제목: {chapter_title}")
        chapter_content = graph_rag.generate_complete_chapter(
            game_title=game_design.get('game_title', ''),
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            guideline=guideline
        )
        print(f"[API 디버그] GraphRAG 추천 결과: {type(chapter_content)}, 키: {chapter_content.keys() if isinstance(chapter_content, dict) else 'N/A'}")
        
        response_data = {
            'success': True,
            'outline': chapter_content['outline'],  # 챕터 개요
            'details': chapter_content['details']   # 챕터 상세 내용
        }
        print(f"[API 디버그] 추천 API 응답: {response_data.keys()}")
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# /generate 라우트 수정 부분
@app.route('/generate', methods=['POST'])
def generate_game_design():
    """게임 기획 자동 생성 API 엔드포인트"""
    data = request.json
    
    # 사용자 입력 유효성 검사
    if not data or 'game_concept' not in data:
        return jsonify({'error': 'Game concept is required'}), 400
    
    # 필수 게임 정보 추출
    game_concept = data.get('game_concept', '')
    target_audience = data.get('target_audience', '일반 게이머')
    genre = data.get('genre', '미정')
    platform = data.get('platform', 'PC')
    
    # 선택적 상세 정보
    gameplay_mechanics = data.get('gameplay_mechanics', [])
    art_style = data.get('art_style', '')
    story_elements = data.get('story_elements', {})
    competitive_analysis = data.get('competitive_analysis', [])
    
    # 스토리라인 생성 여부
    generate_storyline = data.get('generate_storyline', False)
    num_chapters = data.get('num_chapters', 5)
    num_branches = data.get('num_branches', 3)
    
    # LLM을 통한 게임 기획 생성
    try:
        game_design = game_design_generator.generate_complete_design(
            game_concept=game_concept,
            target_audience=target_audience,
            genre=genre,
            platform=platform,
            gameplay_mechanics=gameplay_mechanics,
            art_style=art_style,
            story_elements=story_elements,
            competitive_analysis=competitive_analysis
        )
        
        # 스토리라인 생성이 요청된 경우
        storyline = None
        if generate_storyline and 'narrative' in game_design:
            storyline = storyline_generator.generate_complete_storyline(
                narrative_concept=game_design['narrative'],
                num_chapters=num_chapters,
                num_branches=num_branches
            )
            
            # 게임 디자인에 스토리라인 추가
            game_design['storyline'] = storyline
        
        # 문서 생성 및 저장
        document_path = document_generator.create_document(game_design)
        
        return jsonify({
            'success': True,
            'game_design': game_design,
            'document_path': document_path
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/refine', methods=['POST'])
def refine_game_design():
    """기존 게임 기획 개선 API 엔드포인트"""
    data = request.json
    
    if not data or 'current_design' not in data or 'feedback' not in data:
        return jsonify({'error': 'Current design and feedback are required'}), 400
    
    current_design = data['current_design']
    feedback = data['feedback']
    
    try:
        refined_design = game_design_generator.refine_design(current_design, feedback)
        document_path = document_generator.create_document(refined_design)
        
        return jsonify({
            'success': True,
            'refined_design': refined_design,
            'document_path': document_path
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze-competitor', methods=['POST'])
def analyze_competitor():
    """경쟁 게임 분석 API 엔드포인트"""
    data = request.json
    
    if not data or 'competitor_name' not in data:
        return jsonify({'error': 'Competitor name is required'}), 400
    
    competitor_name = data['competitor_name']
    
    try:
        analysis = game_design_generator.analyze_competitor(competitor_name)
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-content', methods=['POST'])
def generate_specific_content():
    """특정 게임 콘텐츠 생성 API 엔드포인트"""
    data = request.json
    
    if not data or 'content_type' not in data or 'parameters' not in data:
        return jsonify({'error': 'Content type and parameters are required'}), 400
    
    content_type = data['content_type']
    parameters = data['parameters']
    
    try:
        content = game_design_generator.generate_specific_content(content_type, parameters)
        return jsonify({
            'success': True,
            'content': content
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/generate-storyline', methods=['POST'])
def generate_storyline():
    """게임 스토리라인 생성 API 엔드포인트"""
    data = request.json
    
    if not data or 'narrative_concept' not in data:
        return jsonify({'error': 'Narrative concept is required'}), 400
    
    narrative_concept = data.get('narrative_concept', {})
    num_chapters = data.get('num_chapters', 5)
    num_branches = data.get('num_branches', 3)
    
    try:
        # 스토리라인 생성
        storyline = storyline_generator.generate_complete_storyline(
            narrative_concept=narrative_concept,
            num_chapters=num_chapters,
            num_branches=num_branches
        )
        
        # 문서 생성 및 저장
        document_path = document_generator.create_document(
            game_design={
                "game_title": storyline.get("title", "게임 스토리라인"),
                "narrative": narrative_concept,
                "storyline": storyline
            },
            format="markdown"
        )
        
        return jsonify({
            'success': True,
            'storyline': storyline,
            'document_path': document_path
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download_document():
    """문서 다운로드 API 엔드포인트"""
    data = request.json
    
    if not data or 'format' not in data:
        return jsonify({'error': 'Format is required'}), 400
    
    download_format = data['format']
    
    try:
        # 기획서 데이터 가져오기
        game_design = data.get('current_design', {})
        
        if not game_design:
            return jsonify({'error': 'Game design data is required'}), 400
        
        # 게임 이름으로 파일명 생성
        game_title = game_design.get('game_title', '게임기획서')
        filename = f"{game_title.replace(' ', '_')}"
        
        # document_generator를 사용하여 해당 형식으로 문서 생성
        file_path = document_generator.create_document(
            game_design=game_design,
            format=download_format,
            filename=filename
        )
        
        # 파일이 존재하는지 확인
        if not os.path.exists(file_path):
            return jsonify({'error': 'Document creation failed'}), 500
        
        # 파일 다운로드
        return send_file(
            file_path, 
            as_attachment=True, 
            download_name=os.path.basename(file_path)
        )
    
    except Exception as e:
        print(f"다운로드 중 오류 발생: {str(e)}")
        return jsonify({'error': str(e)}), 500

def _load_game_design(markdown_path):
    """마크다운 파일에서 게임 기획 정보 로드"""
    try:
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 기획서 파싱 및 구조화된 데이터로 변환
            game_design = {}
            
            # 제목 추출
            title_match = re.search(r'^# ([^\n]+)', content)
            if title_match:
                game_design['game_title'] = title_match.group(1)
            else:
                game_design['game_title'] = os.path.basename(markdown_path).replace('.md', '')
            
            # 고수준 컨셉 추출
            concept_match = re.search(r'\*\*고수준 컨셉:\*\* ([^\n]+)', content)
            if concept_match:
                game_design['high_concept'] = concept_match.group(1)
            
            # 타겟 사용자층 추출
            target_match = re.search(r'\*\*타겟 사용자층:\*\* ([^\n]+)', content)
            if target_match:
                game_design['target_audience'] = target_match.group(1)
            
            # 장르 추출
            genre_match = re.search(r'\*\*장르:\*\* ([^\n]+)', content)
            if genre_match:
                game_design['genre'] = genre_match.group(1)
            
            # 플랫폼 추출
            platform_match = re.search(r'\*\*플랫폼:\*\* ([^\n]+)', content)
            if platform_match:
                game_design['platform'] = platform_match.group(1)
            
            # 내러티브 섹션 추출
            narrative_section = re.search(r'## 내러티브[\s\S]*?(?=## |$)', content)
            if narrative_section:
                narrative_content = narrative_section.group(0)
                game_design['narrative'] = {
                    'setting': _extract_section_content(narrative_content, '### 세계관'),
                    'background_lore': _extract_section_content(narrative_content, '### 배경 스토리'),
                    'main_plot': _extract_section_content(narrative_content, '### 주요 스토리라인'),
                    'themes': _extract_list_items(narrative_content, '### 주요 테마')
                }
                
                # 캐릭터 정보 추출
                characters = []
                character_sections = re.finditer(r'#### ([^\n]+)[\s\S]*?(?=#### |### |## |$)', narrative_content)
                for char_match in character_sections:
                    char_content = char_match.group(0)
                    char_name = char_match.group(1).strip()
                    
                    role_match = re.search(r'\*\*역할:\*\* ([^\n]+)', char_content)
                    background_match = re.search(r'\*\*배경:\*\* ([^\n]+)', char_content)
                    
                    if role_match and background_match:
                        characters.append({
                            'name': char_name,
                            'role': role_match.group(1),
                            'background': background_match.group(1)
                        })
                
                game_design['narrative']['characters'] = characters
            
            # 게임플레이 섹션 추출
            gameplay_section = re.search(r'## 게임플레이[\s\S]*?(?=## |$)', content)
            if gameplay_section:
                gameplay_content = gameplay_section.group(0)
                game_design['gameplay'] = {
                    'core_gameplay_loop': _extract_section_content(gameplay_content, '### 핵심 게임플레이 루프'),
                    'player_actions': _extract_list_items(gameplay_content, '### 플레이어 액션'),
                    'challenge_types': _extract_list_items(gameplay_content, '### 도전 유형')
                }
            
            # 아트 디렉션 섹션 추출
            art_section = re.search(r'## 아트 디렉션[\s\S]*?(?=## |$)', content)
            if art_section:
                art_content = art_section.group(0)
                game_design['art_direction'] = {
                    'visual_style': _extract_section_content(art_content, '### 시각적 스타일'),
                    'color_palette': _extract_section_content(art_content, '### 색상 팔레트'),
                    'character_design': _extract_section_content(art_content, '### 캐릭터 디자인')
                }
            
            # 스토리라인 섹션 추출
            storyline_section = re.search(r'## 스토리라인[\s\S]*?(?=## |$)', content)
            if storyline_section:
                storyline_content = storyline_section.group(0)
                
                # 챕터 개요 추출
                chapter_outlines = []
                chapter_pattern = r'#### 챕터 (\d+): ([^\n]+)[\s\S]*?(?=#### 챕터|### |## |$)'
                
                for chapter_match in re.finditer(chapter_pattern, storyline_content):
                    chapter_content = chapter_match.group(0)
                    chapter_num = int(chapter_match.group(1))
                    chapter_title = chapter_match.group(2).strip()
                    
                    # 챕터 시놉시스 추출
                    synopsis = re.search(r'#### 챕터 \d+: [^\n]+\s*([^\n]+)', chapter_content)
                    synopsis_text = synopsis.group(1).strip() if synopsis else ""
                    
                    # 목표, 위치, 사건, 도전 과제 추출
                    goals = _extract_list_items(chapter_content, r'\*\*목표:\*\*')
                    locations = _extract_list_items(chapter_content, r'\*\*주요 위치:\*\*')
                    events = _extract_list_items(chapter_content, r'\*\*주요 사건:\*\*')
                    challenges = _extract_list_items(chapter_content, r'\*\*도전 과제:\*\*')
                    
                    chapter_outlines.append({
                        'chapter_number': chapter_num,
                        'title': chapter_title,
                        'synopsis': synopsis_text,
                        'goals': goals,
                        'key_locations': locations,
                        'key_events': events,
                        'challenges': challenges
                    })
                
                # 챕터 개요를 번호 순으로 정렬
                chapter_outlines.sort(key=lambda x: x['chapter_number'])
                
                game_design['storyline'] = {
                    'title': _extract_section_content(storyline_content, '### 스토리 제목'),
                    'premise': _extract_section_content(storyline_content, '### 전제'),
                    'story_arc': _extract_section_content(storyline_content, '### 스토리 아크'),
                    'chapter_outlines': chapter_outlines
                }
            
            return game_design
            
    except Exception as e:
        print(f"게임 기획서 로드 중 오류: {e}")
        return {}

@app.route('/save_document', methods=['POST'])
def save_document():
    """문서 내용 저장 API 엔드포인트"""
    if 'content' not in request.form or 'filename' not in request.form:
        return jsonify({'error': '필수 매개변수가 누락되었습니다.'}), 400
    
    content = request.form['content']
    filename = request.form['filename']
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    try:
        # 파일 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Neo4j 데이터 업데이트
        print(f"[디버그] 문서 저장 후 지식 그래프 처리 시작: {file_path}")
        success = chapter_graph_generator.process_design_document(file_path, clear_db=True)
        print(f"[디버그] 지식 그래프 처리 결과: {success}")
        
        return jsonify({
            'success': True,
            'message': '문서가 저장되었습니다. (지식 그래프 업데이트: ' + str(success) + ')'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _extract_section_content(content, section_header):
    """섹션 헤더 아래의 내용을 추출"""
    pattern = fr"{section_header}\s*([^#]*?)(?=###|##|$)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def _extract_list_items(content, section_header):
    """섹션 헤더 아래의 리스트 항목들을 추출"""
    section_content = _extract_section_content(content, section_header)
    if not section_content:
        return []
        
    items = []
    for line in section_content.split('\n'):
        if line.strip().startswith('-'):
            item = line.strip()[1:].strip()
            if item:
                items.append(item)
    
    return items

if __name__ == '__main__':
    app.run(debug=True)