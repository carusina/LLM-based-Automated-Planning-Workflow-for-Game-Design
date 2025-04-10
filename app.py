# app.py
from flask import Flask, render_template, request, jsonify, send_file
import os
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
from models.llm_service import LLMService
from models.game_design_generator import GameDesignGenerator
from models.document_generator import DocumentGenerator
from models.storyline_generator import StorylineGenerator

# 환경 변수 로드
load_dotenv()

# Flask 앱 초기화
app = Flask(__name__)

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

# 스토리라인 생성기 초기화
storyline_generator = StorylineGenerator(llm_service)

@app.route('/')
def index():
    """메인 페이지 렌더링"""
    return render_template('index.html')

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
            # 여기서 게임 기획서 정보를 다시 재구성해야 합니다.
            # 간단한 구현을 위해 임시로 기본 딕셔너리 반환
            return {
                "game_title": "Game Design",
                "narrative": {},
                "gameplay": {},
                "art_direction": {}
            }
    except Exception as e:
        print(f"게임 기획서 로드 중 오류: {e}")
        return {}
    

if __name__ == '__main__':
    app.run(debug=True)