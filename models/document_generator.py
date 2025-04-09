# models/document_generator.py
import os
import json
import datetime
from typing import Dict, Any, List, Optional, Union
import markdown
from fpdf import FPDF
import docx

class DocumentGenerator:
    """게임 기획서 문서 생성기"""
    
    def __init__(self, output_dir: str = "output"):
        """
        문서 생성기 초기화
        
        Args:
            output_dir: 문서 출력 디렉토리
        """
        self.output_dir = output_dir
        
        # 출력 디렉토리가 없으면 생성
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def create_document(self, 
                       game_design: Dict[str, Any], 
                       format: str = "markdown",
                       filename: str = None) -> str:
        """
        게임 기획서 문서 생성
        
        Args:
            game_design: 게임 기획 정보
            format: 출력 형식 ("markdown", "pdf", "docx")
            filename: 파일 이름 (지정하지 않으면 자동 생성)
            
        Returns:
            생성된 문서 경로
        """
        # 파일 이름이 지정되지 않은 경우 자동 생성
        if not filename:
            game_title = game_design.get("game_title", "게임기획서")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{game_title.replace(' ', '_')}_{timestamp}"
        
        # 파일 경로 생성
        if format.lower() == "markdown":
            file_path = os.path.join(self.output_dir, f"{filename}.md")
            self._create_markdown(game_design, file_path)
        elif format.lower() == "pdf":
            file_path = os.path.join(self.output_dir, f"{filename}.pdf")
            self._create_pdf(game_design, file_path)
        elif format.lower() == "docx":
            file_path = os.path.join(self.output_dir, f"{filename}.docx")
            self._create_docx(game_design, file_path)
        else:
            raise ValueError(f"지원되지 않는 형식: {format}")
        
        return file_path
    
    def _create_markdown(self, game_design: Dict[str, Any], file_path: str) -> None:
        """
        마크다운 형식으로 게임 기획서 생성
        
        Args:
            game_design: 게임 기획 정보
            file_path: 출력 파일 경로
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            # 제목 및 기본 정보
            f.write(f"# {game_design.get('game_title', '게임 기획서')}\n\n")
            f.write(f"**고수준 컨셉:** {game_design.get('high_concept', '')}\n\n")
            f.write(f"**타겟 사용자층:** {game_design.get('target_audience', '')}\n")
            f.write(f"**장르:** {game_design.get('genre', '')}\n")
            f.write(f"**플랫폼:** {game_design.get('platform', '')}\n\n")
            
            # 컨셉 세부사항
            f.write("## 게임 컨셉\n\n")
            concept_details = game_design.get("concept_details", {})
            f.write(f"### 확장된 컨셉\n{concept_details.get('extended_concept', '')}\n\n")
            
            f.write("### 차별화 포인트\n")
            for usp in concept_details.get("unique_selling_points", []):
                f.write(f"- {usp}\n")
            f.write("\n")
            
            f.write(f"### 분위기\n{concept_details.get('mood', '')}\n\n")
            
            # 게임플레이
            f.write("## 게임플레이\n\n")
            gameplay = game_design.get("gameplay", {})
            f.write(f"### 핵심 게임플레이 루프\n{gameplay.get('core_gameplay_loop', '')}\n\n")
            
            f.write("### 플레이어 액션\n")
            for action in gameplay.get("player_actions", []):
                f.write(f"- {action}\n")
            f.write("\n")
            
            f.write(f"### 진행 시스템\n{gameplay.get('progression_system', '')}\n\n")
            
            f.write("### 도전 유형\n")
            for challenge in gameplay.get("challenge_types", []):
                f.write(f"- {challenge}\n")
            f.write("\n")
            
            f.write("### 보상 시스템\n")
            for reward in gameplay.get("reward_systems", []):
                f.write(f"- {reward}\n")
            f.write("\n")
            
            f.write("### 게임 모드\n")
            for mode in gameplay.get("game_modes", []):
                f.write(f"- {mode}\n")
            f.write("\n")
            
            f.write(f"### 조작 방식\n{gameplay.get('controls', '')}\n\n")
            
            f.write("### 독특한 메커니즘\n")
            for mechanic in gameplay.get("unique_mechanics", []):
                f.write(f"- {mechanic}\n")
            f.write("\n")
            
            # 내러티브
            f.write("## 내러티브\n\n")
            narrative = game_design.get("narrative", {})
            f.write(f"### 세계관\n{narrative.get('setting', '')}\n\n")
            f.write(f"### 배경 스토리\n{narrative.get('background_lore', '')}\n\n")
            f.write(f"### 주요 스토리라인\n{narrative.get('main_plot', '')}\n\n")
            f.write(f"### 스토리 구조\n{narrative.get('plot_structure', '')}\n\n")
            
            f.write("### 주요 테마\n")
            for theme in narrative.get("themes", []):
                f.write(f"- {theme}\n")
            f.write("\n")
            
            f.write("### 캐릭터\n")
            for character in narrative.get("characters", []):
                f.write(f"#### {character.get('name', '이름 없음')}\n")
                f.write(f"- **역할:** {character.get('role', '')}\n")
                f.write(f"- **배경:** {character.get('background', '')}\n")
                f.write(f"- **동기:** {character.get('motivation', '')}\n")
                f.write(f"- **캐릭터 아크:** {character.get('arc', '')}\n\n")
            
            f.write("### 내러티브 장치\n")
            for device in narrative.get("narrative_devices", []):
                f.write(f"- {device}\n")
            f.write("\n")
            
            f.write(f"### 플레이어 선택\n{narrative.get('player_agency', '')}\n\n")
            f.write(f"### 게임플레이와 내러티브 통합\n{narrative.get('integration_with_gameplay', '')}\n\n")
            
            # 아트 디렉션
            f.write("## 아트 디렉션\n\n")
            art = game_design.get("art_direction", {})
            f.write(f"### 시각적 스타일\n{art.get('visual_style', '')}\n\n")
            f.write(f"### 색상 팔레트\n{art.get('color_palette', '')}\n\n")
            
            f.write("### 참고 아트 스타일\n")
            for ref in art.get("art_references", []):
                f.write(f"- {ref}\n")
            f.write("\n")
            
            f.write(f"### 캐릭터 디자인\n{art.get('character_design', '')}\n\n")
            f.write(f"### 환경 디자인\n{art.get('environment_design', '')}\n\n")
            f.write(f"### UI 디자인\n{art.get('ui_design', '')}\n\n")
            f.write(f"### 애니메이션 스타일\n{art.get('animation_style', '')}\n\n")
            f.write(f"### 조명\n{art.get('lighting', '')}\n\n")
            f.write(f"### 사운드 디자인\n{art.get('sound_design', '')}\n\n")
            f.write(f"### 음악 방향\n{art.get('music_direction', '')}\n\n")
            
            # 기술 사양
            f.write("## 기술 사양\n\n")
            tech = game_design.get("technical_specs", {})
            
            f.write("### 타겟 플랫폼\n")
            for platform in tech.get("target_platforms", []):
                f.write(f"- {platform}\n")
            f.write("\n")
            
            f.write(f"### 최소 사양\n{tech.get('minimum_specs', '')}\n\n")
            f.write(f"### 권장 사양\n{tech.get('recommended_specs', '')}\n\n")
            f.write(f"### 게임 엔진\n{tech.get('engine', '')}\n\n")
            
            f.write("### 핵심 기술\n")
            for technology in tech.get("key_technologies", []):
                f.write(f"- {technology}\n")
            f.write("\n")
            
            f.write(f"### 네트워킹\n{tech.get('networking', '')}\n\n")
            f.write(f"### 성능 목표\n{tech.get('performance_targets', '')}\n\n")
            
            f.write("### 개발 도전 과제\n")
            for challenge in tech.get("development_challenges", []):
                f.write(f"- {challenge}\n")
            f.write("\n")
            
            f.write(f"### 에셋 요구사항\n{tech.get('asset_requirements', '')}\n\n")
            f.write(f"### 예상 개발 리소스\n{tech.get('estimated_development_resources', '')}\n\n")
            
            # 수익화 계획
            f.write("## 수익화 계획\n\n")
            monetization = game_design.get("monetization", {})
            f.write(f"### 수익화 모델\n{monetization.get('monetization_model', '')}\n\n")
            f.write(f"### 가격 책정\n{monetization.get('price_point', '')}\n\n")
            f.write(f"### 인앱 구매\n{monetization.get('in_app_purchases', '')}\n\n")
            f.write(f"### 가상 화폐\n{monetization.get('virtual_currency', '')}\n\n")
            f.write(f"### 배틀패스\n{monetization.get('battle_pass', '')}\n\n")
            f.write(f"### 광고\n{monetization.get('advertising', '')}\n\n")
            f.write(f"### DLC/확장팩\n{monetization.get('dlc_expansion', '')}\n\n")
            f.write(f"### 구독\n{monetization.get('subscription', '')}\n\n")
            
            f.write("### 플레이어 유지 전략\n")
            for strategy in monetization.get("player_retention_strategies", []):
                f.write(f"- {strategy}\n")
            f.write("\n")
            
            f.write(f"### 수익 예상\n{monetization.get('revenue_projections', '')}\n\n")
            f.write(f"### 시장 분석\n{monetization.get('market_analysis', '')}\n\n")
            
            # 개발 로드맵
            f.write("## 개발 로드맵\n\n")
            roadmap = game_design.get("development_roadmap", {})
            timeline = roadmap.get("development_timeline", {})
            
            f.write("### 개발 타임라인\n")
            f.write(f"- **사전 제작:** {timeline.get('pre_production', '')}\n")
            f.write(f"- **프로토타입:** {timeline.get('prototype', '')}\n")
            f.write(f"- **본 제작:** {timeline.get('production', '')}\n")
            f.write(f"- **알파:** {timeline.get('alpha', '')}\n")
            f.write(f"- **베타:** {timeline.get('beta', '')}\n")
            f.write(f"- **골드 마스터:** {timeline.get('gold', '')}\n")
            f.write(f"- **출시 후 지원:** {timeline.get('post_launch', '')}\n\n")
            
            team = roadmap.get("team_structure", {})
            f.write("### 팀 구성\n")
            
            f.write("#### 핵심 팀\n")
            for role in team.get("core_team", []):
                f.write(f"- {role}\n")
            f.write("\n")
            
            f.write("#### 확장 팀\n")
            for role in team.get("expanded_team", []):
                f.write(f"- {role}\n")
            f.write("\n")
            
            f.write("#### 외주\n")
            for outsource in team.get("outsourcing", []):
                f.write(f"- {outsource}\n")
            f.write("\n")
            
            f.write(f"### 예산 추정\n{roadmap.get('budget_estimate', '')}\n\n")
            
            f.write("### 리스크 평가\n")
            for risk in roadmap.get("risk_assessment", []):
                f.write(f"- {risk}\n")
            f.write("\n")
            
            f.write(f"### 테스트 계획\n{roadmap.get('testing_plan', '')}\n\n")
            f.write(f"### 마케팅 타임라인\n{roadmap.get('marketing_timeline', '')}\n\n")
            
            f.write("### 주요 산출물\n")
            for deliverable in roadmap.get("key_deliverables", []):
                f.write(f"- {deliverable}\n")
            f.write("\n")
            
            f.write("### 성공 지표\n")
            for metric in roadmap.get("success_metrics", []):
                f.write(f"- {metric}\n")
            f.write("\n")
            
            # 경쟁 분석 (있는 경우)
            if "competition_analysis" in game_design:
                f.write("## 경쟁 분석\n\n")
                competition = game_design.get("competition_analysis", {})
                
                for i, competitor in enumerate(competition.get("competitors", []), 1):
                    f.write(f"### 경쟁작 {i}: {competitor.get('game_name', '이름 없음')}\n\n")
                    f.write(f"**개발사:** {competitor.get('developer', '')}\n")
                    f.write(f"**퍼블리셔:** {competitor.get('publisher', '')}\n")
                    f.write(f"**출시일:** {competitor.get('release_date', '')}\n")
                    f.write(f"**장르:** {competitor.get('genre', '')}\n")
                    f.write(f"**타겟 사용자층:** {competitor.get('target_audience', '')}\n\n")
                    
                    f.write("#### 주요 특징\n")
                    for feature in competitor.get("key_features", []):
                        f.write(f"- {feature}\n")
                    f.write("\n")
                    
                    f.write(f"#### 게임플레이 분석\n{competitor.get('gameplay_analysis', '')}\n\n")
                    f.write(f"#### 내러티브 분석\n{competitor.get('narrative_analysis', '')}\n\n")
                    f.write(f"#### 아트 스타일 분석\n{competitor.get('art_style_analysis', '')}\n\n")
                    f.write(f"#### 수익화 모델\n{competitor.get('monetization_model', '')}\n\n")
                    
                    reception = competitor.get("reception", {})
                    f.write("#### 시장 반응\n")
                    f.write(f"- **평론가 점수:** {reception.get('critic_score', '')}\n")
                    f.write(f"- **사용자 평점:** {reception.get('user_score', '')}\n")
                    f.write(f"- **판매 실적:** {reception.get('sales_performance', '')}\n\n")
                    
                    f.write("#### 강점\n")
                    for strength in competitor.get("strengths", []):
                        f.write(f"- {strength}\n")
                    f.write("\n")
                    
                    f.write("#### 약점\n")
                    for weakness in competitor.get("weaknesses", []):
                        f.write(f"- {weakness}\n")
                    f.write("\n")
                    
                    f.write("#### 배울 점\n")
                    for lesson in competitor.get("lessons", []):
                        f.write(f"- {lesson}\n")
                    f.write("\n")
    
    def _create_pdf(self, game_design: Dict[str, Any], file_path: str) -> None:
        """
        PDF 형식으로 게임 기획서 생성
        
        Args:
            game_design: 게임 기획 정보
            file_path: 출력 파일 경로
        """
        # 먼저 마크다운으로 변환
        temp_md_path = file_path.replace('.pdf', '_temp.md')
        self._create_markdown(game_design, temp_md_path)
        
        # 마크다운을 HTML로 변환
        with open(temp_md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
        
        # PDF 생성
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # 폰트 설정 (기본 폰트는 한글을 지원하지 않으므로 주의)
        pdf.add_font('NanumGothic', '', 'NanumGothic.ttf', uni=True)
        pdf.set_font('NanumGothic', '', 12)
        
        # HTML을 PDF로 변환 (간단한 구현)
        # 실제로는 HTML 파싱과 스타일링이 필요함
        # 여기서는 단순화된 방식 사용
        
        # 제목
        pdf.set_font('NanumGothic', '', 24)
        pdf.cell(0, 10, game_design.get('game_title', '게임 기획서'), 0, 1, 'C')
        pdf.ln(10)
        
        # 기본 내용
        pdf.set_font('NanumGothic', '', 12)
        
        # 마크다운 내용을 라인별로 파싱하여 PDF에 추가
        # (간단한 구현이므로 마크다운 문법은 부분적으로만 처리됨)
        lines = md_content.split('\n')
        for line in lines:
            # 제목 처리
            if line.startswith('# '):
                pdf.set_font('NanumGothic', '', 20)
                pdf.cell(0, 10, line[2:], 0, 1, 'L')
                pdf.ln(5)
                pdf.set_font('NanumGothic', '', 12)
            elif line.startswith('## '):
                pdf.set_font('NanumGothic', '', 18)
                pdf.cell(0, 10, line[3:], 0, 1, 'L')
                pdf.ln(5)
                pdf.set_font('NanumGothic', '', 12)
            elif line.startswith('### '):
                pdf.set_font('NanumGothic', '', 16)
                pdf.cell(0, 10, line[4:], 0, 1, 'L')
                pdf.ln(5)
                pdf.set_font('NanumGothic', '', 12)
            elif line.startswith('#### '):
                pdf.set_font('NanumGothic', '', 14)
                pdf.cell(0, 10, line[5:], 0, 1, 'L')
                pdf.ln(5)
                pdf.set_font('NanumGothic', '', 12)
            # 목록 처리
            elif line.startswith('- '):
                pdf.cell(10, 10, '•', 0, 0, 'L')
                pdf.multi_cell(0, 10, line[2:], 0, 'L')
            # 일반 텍스트
            elif line.strip():
                pdf.multi_cell(0, 10, line, 0, 'L')
            # 빈 줄
            else:
                pdf.ln(5)
        
        # PDF 저장
        pdf.output(file_path)
        
        # 임시 파일 삭제
        os.remove(temp_md_path)
    
    def _create_docx(self, game_design: Dict[str, Any], file_path: str) -> None:
        """
        Word 문서 형식으로 게임 기획서 생성
        
        Args:
            game_design: 게임 기획 정보
            file_path: 출력 파일 경로
        """
        doc = docx.Document()
        
        # 제목 및 기본 정보
        doc.add_heading(game_design.get('game_title', '게임 기획서'), 0)
        
        p = doc.add_paragraph()
        p.add_run('고수준 컨셉: ').bold = True
        p.add_run(game_design.get('high_concept', ''))
        
        p = doc.add_paragraph()
        p.add_run('타겟 사용자층: ').bold = True
        p.add_run(game_design.get('target_audience', ''))
        
        p = doc.add_paragraph()
        p.add_run('장르: ').bold = True
        p.add_run(game_design.get('genre', ''))
        
        p = doc.add_paragraph()
        p.add_run('플랫폼: ').bold = True
        p.add_run(game_design.get('platform', ''))
        
        doc.add_paragraph()
        
        # 컨셉 세부사항
        doc.add_heading('게임 컨셉', 1)
        concept_details = game_design.get("concept_details", {})
        
        doc.add_heading('확장된 컨셉', 2)
        doc.add_paragraph(concept_details.get('extended_concept', ''))
        
        doc.add_heading('차별화 포인트', 2)
        for usp in concept_details.get("unique_selling_points", []):
            doc.add_paragraph(usp, style='List Bullet')
        
        doc.add_heading('분위기', 2)
        doc.add_paragraph(concept_details.get('mood', ''))
        
        # 게임플레이
        doc.add_heading('게임플레이', 1)
        gameplay = game_design.get("gameplay", {})
        
        doc.add_heading('핵심 게임플레이 루프', 2)
        doc.add_paragraph(gameplay.get('core_gameplay_loop', ''))
        
        doc.add_heading('플레이어 액션', 2)
        for action in gameplay.get("player_actions", []):
            doc.add_paragraph(action, style='List Bullet')
        
        doc.add_heading('진행 시스템', 2)
        doc.add_paragraph(gameplay.get('progression_system', ''))
        
        doc.add_heading('도전 유형', 2)
        for challenge in gameplay.get("challenge_types", []):
            doc.add_paragraph(challenge, style='List Bullet')
        
        doc.add_heading('보상 시스템', 2)
        for reward in gameplay.get("reward_systems", []):
            doc.add_paragraph(reward, style='List Bullet')
        
        doc.add_heading('게임 모드', 2)
        for mode in gameplay.get("game_modes", []):
            doc.add_paragraph(mode, style='List Bullet')
        
        doc.add_heading('조작 방식', 2)
        doc.add_paragraph(gameplay.get('controls', ''))
        
        doc.add_heading('독특한 메커니즘', 2)
        for mechanic in gameplay.get("unique_mechanics", []):
            doc.add_paragraph(mechanic, style='List Bullet')
        
        # 내러티브
        doc.add_heading('내러티브', 1)
        narrative = game_design.get("narrative", {})
        
        doc.add_heading('세계관', 2)
        doc.add_paragraph(narrative.get('setting', ''))
        
        doc.add_heading('배경 스토리', 2)
        doc.add_paragraph(narrative.get('background_lore', ''))
        
        doc.add_heading('주요 스토리라인', 2)
        doc.add_paragraph(narrative.get('main_plot', ''))
        
        doc.add_heading('스토리 구조', 2)
        doc.add_paragraph(narrative.get('plot_structure', ''))
        
        doc.add_heading('주요 테마', 2)
        for theme in narrative.get("themes", []):
            doc.add_paragraph(theme, style='List Bullet')
        
        doc.add_heading('캐릭터', 2)
        for character in narrative.get("characters", []):
            doc.add_heading(character.get('name', '이름 없음'), 3)
            
            p = doc.add_paragraph()
            p.add_run('역할: ').bold = True
            p.add_run(character.get('role', ''))
            
            p = doc.add_paragraph()
            p.add_run('배경: ').bold = True
            p.add_run(character.get('background', ''))
            
            p = doc.add_paragraph()
            p.add_run('동기: ').bold = True
            p.add_run(character.get('motivation', ''))
            
            p = doc.add_paragraph()
            p.add_run('캐릭터 아크: ').bold = True
            p.add_run(character.get('arc', ''))
        
        doc.add_heading('내러티브 장치', 2)
        for device in narrative.get("narrative_devices", []):
            doc.add_paragraph(device, style='List Bullet')
        
        doc.add_heading('플레이어 선택', 2)
        doc.add_paragraph(narrative.get('player_agency', ''))
        
        doc.add_heading('게임플레이와 내러티브 통합', 2)
        doc.add_paragraph(narrative.get('integration_with_gameplay', ''))
        
        # 아트 디렉션
        doc.add_heading('아트 디렉션', 1)
        art = game_design.get("art_direction", {})
        
        doc.add_heading('시각적 스타일', 2)
        doc.add_paragraph(art.get('visual_style', ''))
        
        doc.add_heading('색상 팔레트', 2)
        doc.add_paragraph(art.get('color_palette', ''))
        
        doc.add_heading('참고 아트 스타일', 2)
        for ref in art.get("art_references", []):
            doc.add_paragraph(ref, style='List Bullet')
        
        doc.add_heading('캐릭터 디자인', 2)
        doc.add_paragraph(art.get('character_design', ''))
        
        doc.add_heading('환경 디자인', 2)
        doc.add_paragraph(art.get('environment_design', ''))
        
        doc.add_heading('UI 디자인', 2)
        doc.add_paragraph(art.get('ui_design', ''))
        
        doc.add_heading('애니메이션 스타일', 2)
        doc.add_paragraph(art.get('animation_style', ''))
        
        doc.add_heading('조명', 2)
        doc.add_paragraph(art.get('lighting', ''))
        
        doc.add_heading('사운드 디자인', 2)
        doc.add_paragraph(art.get('sound_design', ''))
        
        doc.add_heading('음악 방향', 2)
        doc.add_paragraph(art.get('music', ''))