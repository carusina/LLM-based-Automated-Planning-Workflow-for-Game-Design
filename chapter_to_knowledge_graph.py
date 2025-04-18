#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
챕터 개요 -> Neo4j 지식 그래프 변환기

게임 기획서(마크다운 파일)에서 챕터 개요 정보를 추출하여 
Neo4j 지식 그래프를 구축합니다.
"""

import os
import re
import glob
import argparse
from datetime import datetime
from neo4j import GraphDatabase
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# Neo4j 연결 정보
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

class ChapterKnowledgeGraphGenerator:
    def __init__(self, uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD):
        """Neo4j 데이터베이스에 연결합니다."""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.debug = False
        
    def set_debug(self, debug=True):
        """디버그 모드를 설정합니다."""
        self.debug = debug
        
    def close(self):
        """Neo4j 연결을 종료합니다."""
        self.driver.close()
        
    def run_query(self, query, parameters=None):
        """Cypher 쿼리를 실행합니다."""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return list(result)
    
    def clear_database(self):
        """데이터베이스의 모든 데이터를 삭제합니다."""
        try:
            self.run_query("MATCH (n) DETACH DELETE n")
            print("데이터베이스의 모든 데이터가 삭제되었습니다.")
            return True
        except Exception as e:
            print(f"데이터베이스 초기화 중 오류 발생: {e}")
            return False
    
    def extract_chapters_from_markdown(self, markdown_content):
        """마크다운 파일에서 챕터 정보를 추출합니다."""
        chapters = []
        unique_chapters = set()  # 중복 방지용 세트
        
        # 챕터 개요 섹션 찾기 
        overview_match = re.search(r'### 챕터 개요(.*?)(?=### 챕터 상세 내용|$)', markdown_content, re.DOTALL)
        chapter_section = ""
        
        # 챕터 상세 내용 섹션 찾기
        details_match = re.search(r'### 챕터 상세 내용(.*?)(?=##|$)', markdown_content, re.DOTALL)
        details_section = ""
        
        if overview_match:
            chapter_section = overview_match.group(1)
        else:
            # 챕터 개요 섹션이 없으면 전체 스토리라인 섹션에서 찾기
            storyline_match = re.search(r'## 스토리라인(.*?)(?=##|$)', markdown_content, re.DOTALL)
            if storyline_match:
                chapter_section = storyline_match.group(1)
                
        if details_match:
            details_section = details_match.group(1)
        
        if chapter_section:
            # 챕터 패턴
            chapter_pattern = r'#### 챕터 (\d+): ([^\n]+)\s*([^\n]*)'
            
            # 챕터 찾기
            chapter_matches = list(re.finditer(chapter_pattern, chapter_section))
            
            if self.debug:
                print(f"\n총 {len(chapter_matches)}개의 챕터를 찾았습니다.\n")
            
            for i, chapter_match in enumerate(chapter_matches):
                chapter_number = int(chapter_match.group(1))
                chapter_title = chapter_match.group(2).strip()
                chapter_description = chapter_match.group(3).strip()
                
                # 이미 처리한 챕터는 건너뛰기
                chapter_key = f"{chapter_number}:{chapter_title}"
                if chapter_key in unique_chapters:
                    continue
                
                unique_chapters.add(chapter_key)
                
                if self.debug:
                    print(f"챕터 {chapter_number}: {chapter_title}")
                
                # 챕터 시작과 끝 위치 찾기
                chapter_start = chapter_match.end()
                chapter_end = None
                
                if i < len(chapter_matches) - 1:
                    chapter_end = chapter_matches[i + 1].start()
                else:
                    # 마지막 챕터라면 다음 섹션까지
                    next_section = re.search(r'###|####', chapter_section[chapter_start:])
                    if next_section:
                        chapter_end = chapter_start + next_section.start()
                
                # 챕터 내용 추출
                if chapter_end:
                    chapter_content = chapter_section[chapter_start:chapter_end]
                else:
                    chapter_content = chapter_section[chapter_start:]
                
                # 목표, 위치, 사건, 도전 과제 패턴
                goals_pattern = r'\*\*목표:\*\*\s*\n((?:- [^\n]+\n)+)'
                locations_pattern = r'\*\*주요 위치:\*\*\s*\n((?:- [^\n]+\n)+)'
                events_pattern = r'\*\*주요 사건:\*\*\s*\n((?:- [^\n]+\n)+)'
                challenges_pattern = r'\*\*도전 과제:\*\*\s*\n((?:- [^\n]+\n)+)'
                
                # 목표, 위치, 사건, 도전 과제 추출
                goals = []
                locations = []
                events = []
                challenges = []
                
                goals_match = re.search(goals_pattern, chapter_content)
                if goals_match:
                    goals_text = goals_match.group(1)
                    goals = [goal.strip()[2:] for goal in goals_text.strip().split('\n') if goal.strip()]
                    if self.debug:
                        print(f"  목표: {goals}")
                
                locations_match = re.search(locations_pattern, chapter_content)
                if locations_match:
                    locations_text = locations_match.group(1)
                    locations = [location.strip()[2:] for location in locations_text.strip().split('\n') if location.strip()]
                    if self.debug:
                        print(f"  위치: {locations}")
                
                events_match = re.search(events_pattern, chapter_content)
                if events_match:
                    events_text = events_match.group(1)
                    events = [event.strip()[2:] for event in events_text.strip().split('\n') if event.strip()]
                    if self.debug:
                        print(f"  사건: {events}")
                
                challenges_match = re.search(challenges_pattern, chapter_content)
                if challenges_match:
                    challenges_text = challenges_match.group(1)
                    challenges = [challenge.strip()[2:] for challenge in challenges_text.strip().split('\n') if challenge.strip()]
                    if self.debug:
                        print(f"  도전 과제: {challenges}")
                
                # 챕터 상세 내용 추출 (있는 경우)
                chapter_details = ""
                if details_section:
                    # 현재 챕터의 상세 내용 패턴
                    details_pattern = rf'#### 챕터 {chapter_number}: {re.escape(chapter_title)}\s*([\s\S]*?)(?=#### 챕터|### |## |$)'
                    details_match = re.search(details_pattern, details_section)
                    if details_match:
                        chapter_details = details_match.group(1).strip()
                        if self.debug:
                            print(f"  상세 내용: {chapter_details[:100]}...")
                
                # 챕터 정보 저장
                chapter_info = {
                    'number': chapter_number,
                    'title': chapter_title,
                    'description': chapter_description if chapter_description else "",
                    'goals': goals,
                    'locations': locations,
                    'events': events,
                    'challenges': challenges,
                    'details': chapter_details
                }
                
                chapters.append(chapter_info)
        
        # 챕터를 번호 순으로 정렬
        chapters.sort(key=lambda x: x['number'])
        
        return chapters
    
    def extract_characters(self, markdown_content):
        """마크다운 파일에서 캐릭터 정보를 추출합니다."""
        characters = []
        
        # 직접 패턴으로 추출 시도 - 역할과 배경이 연속되어 있는 경우
        direct_patterns = [
            r'####\s*([^\n]+)\s*- \*\*역할:\*\* ([^\n]+)\s*- \*\*배경:\*\* ([^\n]+)',
            r'####\s*([^\n]+)\s*- \*\*Role:\*\* ([^\n]+)\s*- \*\*Background:\*\* ([^\n]+)'
        ]
        
        for pattern in direct_patterns:
            matches = re.finditer(pattern, markdown_content)
            for match in matches:
                name = match.group(1).strip()
                role = match.group(2).strip()
                background = match.group(3).strip()
                
                # 이미 추가된 캐릭터인지 확인 (중복 방지)
                if not any(c['name'] == name for c in characters):
                    characters.append({
                        'name': name,
                        'role': role,
                        'background': background
                    })
                    if self.debug:
                        print(f"  캐릭터 추가: {name} ({role})")
        
        # 역할과 배경이 따로 있는 경우
        separate_patterns = [
            r'####\s*([^\n]+)[\s\S]*?\*\*역할:\*\* ([^\n]+)[\s\S]*?\*\*배경:\*\* ([^\n]+)',
            r'####\s*([^\n]+)[\s\S]*?\*\*Role:\*\* ([^\n]+)[\s\S]*?\*\*Background:\*\* ([^\n]+)'
        ]
        
        for pattern in separate_patterns:
            matches = re.finditer(pattern, markdown_content)
            for match in matches:
                name = match.group(1).strip()
                role = match.group(2).strip()
                background = match.group(3).strip()
                
                # 이미 추가된 캐릭터인지 확인 (중복 방지)
                if not any(c['name'] == name for c in characters):
                    characters.append({
                        'name': name,
                        'role': role,
                        'background': background
                    })
                    if self.debug:
                        print(f"  캐릭터 추가 (분리 패턴): {name} ({role})")
        
        if self.debug and characters:
            print(f"\n총 {len(characters)}개의 캐릭터를 추출했습니다.")
            for char in characters:
                print(f"  - {char['name']} ({char['role']}): {char['background'][:50]}...")
                
        return characters
    
    def extract_game_title(self, markdown_content):
        """마크다운 파일에서 게임 제목을 추출합니다."""
        title_match = re.search(r'^# ([^\n]+)', markdown_content)
        return title_match.group(1) if title_match else "Game"
    
    def create_knowledge_graph(self, game_title, chapters, characters):
        """추출된 챕터 정보를 바탕으로 Neo4j 지식 그래프를 생성합니다."""
        try:
            # 게임 노드 생성
            game_node_query = """
            CREATE (g:Game {title: $title, created_at: datetime()})
            RETURN g
            """
            self.run_query(game_node_query, {"title": game_title})
            print(f"게임 노드 생성: {game_title}")
            
            # 챕터 노드 생성
            for chapter in chapters:
                chapter_node_query = """
                CREATE (c:Chapter {
                    title: $title,
                    number: $number,
                    description: $description,
                    details: $details
                })
                WITH c
                MATCH (g:Game {title: $game_title})
                CREATE (g)-[:HAS_CHAPTER]->(c)
                RETURN c
                """
                self.run_query(chapter_node_query, {
                    "title": chapter["title"],
                    "number": chapter["number"],
                    "description": chapter["description"],
                    "details": chapter.get("details", ""),
                    "game_title": game_title
                })
                print(f"챕터 노드 생성: 챕터 {chapter['number']} - {chapter['title']}")
                
                # 목표 노드 생성
                for goal in chapter["goals"]:
                    goal_node_query = """
                    CREATE (g:Goal {description: $description})
                    WITH g
                    MATCH (c:Chapter {title: $chapter_title, number: $chapter_number})
                    CREATE (c)-[:HAS_GOAL]->(g)
                    RETURN g
                    """
                    self.run_query(goal_node_query, {
                        "description": goal,
                        "chapter_title": chapter["title"],
                        "chapter_number": chapter["number"]
                    })
                
                # 위치 노드 생성
                for location in chapter["locations"]:
                    # 간단한 위치 타입 추출 로직
                    location_type = "Location"
                    if "station" in location.lower():
                        location_type = "Space Station"
                    elif "planet" in location.lower():
                        location_type = "Planet"
                    elif "ruins" in location.lower():
                        location_type = "Ruins"
                    elif "facility" in location.lower():
                        location_type = "Research Facility"
                    elif "megastructure" in location.lower() or "heart" in location.lower():
                        location_type = "Megastructure"
                    elif "wilderness" in location.lower() or "expanse" in location.lower():
                        location_type = "Wilderness"
                    
                    location_node_query = """
                    MERGE (l:Location {name: $name})
                    ON CREATE SET l.type = $type
                    WITH l
                    MATCH (c:Chapter {title: $chapter_title, number: $chapter_number})
                    MERGE (c)-[:TAKES_PLACE_AT]->(l)
                    RETURN l
                    """
                    self.run_query(location_node_query, {
                        "name": location,
                        "type": location_type,
                        "chapter_title": chapter["title"],
                        "chapter_number": chapter["number"]
                    })
                
                # 사건 노드 생성
                for event in chapter["events"]:
                    # 포맷팅: 이벤트 이름에서 마크다운 서식 제거
                    clean_event = re.sub(r'\*\*([^*]+)\*\*: ', '', event)
                    
                    event_node_query = """
                    CREATE (e:Event {name: $name, description: $description})
                    WITH e
                    MATCH (c:Chapter {title: $chapter_title, number: $chapter_number})
                    CREATE (c)-[:CONTAINS_EVENT]->(e)
                    RETURN e
                    """
                    self.run_query(event_node_query, {
                        "name": clean_event,
                        "description": event,
                        "chapter_title": chapter["title"],
                        "chapter_number": chapter["number"]
                    })
                
                # 도전 과제 노드 생성
                for challenge in chapter["challenges"]:
                    # 난이도 추정
                    difficulty = "Medium"
                    if "harsh" in challenge.lower() or "defending" in challenge.lower():
                        difficulty = "Medium"
                    elif "solving" in challenge.lower() or "battles" in challenge.lower():
                        difficulty = "Hard"
                    elif "interfacing" in challenge.lower() or "alien" in challenge.lower():
                        difficulty = "Very Hard"
                    
                    challenge_node_query = """
                    CREATE (ch:Challenge {name: $name, difficulty: $difficulty})
                    WITH ch
                    MATCH (c:Chapter {title: $chapter_title, number: $chapter_number})
                    CREATE (c)-[:PRESENTS_CHALLENGE]->(ch)
                    RETURN ch
                    """
                    self.run_query(challenge_node_query, {
                        "name": challenge,
                        "difficulty": difficulty,
                        "chapter_title": chapter["title"],
                        "chapter_number": chapter["number"]
                    })
            
            # 캐릭터 노드 생성
            for character in characters:
                role_clean = "Side Character"
                if "protagonist" in character["role"].lower() or "main" in character["role"].lower() or "주인공" in character["role"]:
                    role_clean = "Protagonist"
                elif "antagonist" in character["role"].lower():
                    role_clean = "Antagonist"
                elif "guardian" in character["role"].lower():
                    role_clean = "Guardian"
                
                if self.debug:
                    print(f"  역할 변환: '{character['role']}' -> '{role_clean}'")
                
                character_node_query = """
                CREATE (ch:Character {name: $name, role: $role, background: $background})
                WITH ch
                MATCH (g:Game {title: $game_title})
                CREATE (g)-[:HAS_CHARACTER]->(ch)
                RETURN ch
                """
                self.run_query(character_node_query, {
                    "name": character["name"],
                    "role": role_clean,
                    "background": character["background"],
                    "game_title": game_title
                })
                print(f"캐릭터 노드 생성: {character['name']} ({role_clean})")
            
            # 챕터 간 순서 관계 생성
            for i in range(1, len(chapters)):
                chapter_order_query = """
                MATCH (c1:Chapter {number: $prev_number})
                MATCH (c2:Chapter {number: $next_number})
                CREATE (c1)-[:FOLLOWED_BY]->(c2)
                """
                self.run_query(chapter_order_query, {
                    "prev_number": chapters[i-1]["number"],
                    "next_number": chapters[i]["number"]
                })
                print(f"챕터 순서 관계 생성: 챕터 {chapters[i-1]['number']} -> 챕터 {chapters[i]['number']}")
            
            # 이벤트와 캐릭터의 관계 생성 (주인공은 모든 이벤트에 참여)
            protagonist_query = """
            MATCH (c:Character)
            WHERE c.role = 'Protagonist'
            RETURN c.name AS name LIMIT 1
            """
            result = self.run_query(protagonist_query)
            
            if result:
                protagonist_name = result[0]["name"]
                
                event_character_query = """
                MATCH (p:Character {name: $protagonist_name})
                MATCH (e:Event)
                CREATE (p)-[:PARTICIPATES_IN]->(e)
                """
                self.run_query(event_character_query, {"protagonist_name": protagonist_name})
                print(f"주인공 '{protagonist_name}'이(가) 모든 이벤트에 참여하는 관계 생성")
            else:
                print("주인공을 찾을 수 없어 이벤트-캐릭터 관계를 생성하지 않았습니다.")
            
            # 위치 간 관계 생성 (예: 행성 위에 있는 시설)
            for chapter in chapters:
                if len(chapter["locations"]) >= 2:
                    for i in range(len(chapter["locations"]) - 1):
                        for j in range(i+1, len(chapter["locations"])):
                            loc1 = chapter["locations"][i]
                            loc2 = chapter["locations"][j]
                            
                            # 행성과 시설 관계 추정
                            if "planet" in loc1.lower() and ("facility" in loc2.lower() or "ruins" in loc2.lower()):
                                location_relation_query = """
                                MATCH (l1:Location {name: $loc1})
                                MATCH (l2:Location {name: $loc2})
                                MERGE (l2)-[:LOCATED_ON]->(l1)
                                """
                                self.run_query(location_relation_query, {"loc1": loc1, "loc2": loc2})
                                print(f"위치 관계 생성: {loc2} -> {loc1}")
                            elif "planet" in loc2.lower() and ("facility" in loc1.lower() or "ruins" in loc1.lower()):
                                location_relation_query = """
                                MATCH (l1:Location {name: $loc1})
                                MATCH (l2:Location {name: $loc2})
                                MERGE (l1)-[:LOCATED_ON]->(l2)
                                """
                                self.run_query(location_relation_query, {"loc1": loc1, "loc2": loc2})
                                print(f"위치 관계 생성: {loc1} -> {loc2}")
                                
                            # 추가 관계: 우주선과 행성
                            if ("station" in loc1.lower() or "orbital" in loc1.lower()) and "planet" in loc2.lower():
                                location_relation_query = """
                                MATCH (l1:Location {name: $loc1})
                                MATCH (l2:Location {name: $loc2})
                                MERGE (l1)-[:ORBITS]->(l2)
                                """
                                self.run_query(location_relation_query, {"loc1": loc1, "loc2": loc2})
                                print(f"궤도 관계 생성: {loc1} -> {loc2}")
                            elif ("station" in loc2.lower() or "orbital" in loc2.lower()) and "planet" in loc1.lower():
                                location_relation_query = """
                                MATCH (l1:Location {name: $loc1})
                                MATCH (l2:Location {name: $loc2})
                                MERGE (l2)-[:ORBITS]->(l1)
                                """
                                self.run_query(location_relation_query, {"loc1": loc1, "loc2": loc2})
                                print(f"궤도 관계 생성: {loc2} -> {loc1}")
            
            # 노드 수 확인
            count_query = "MATCH (n) RETURN count(n) AS count"
            count_result = self.run_query(count_query)
            total_nodes = count_result[0]["count"] if count_result else 0
            
            # 관계 수 확인
            rel_count_query = "MATCH ()-[r]->() RETURN count(r) AS count"
            rel_count_result = self.run_query(rel_count_query)
            total_rels = rel_count_result[0]["count"] if rel_count_result else 0
            
            print(f"""
지식 그래프 생성 완료: {game_title}
총 {len(chapters)}개 챕터, {len(characters)}개 캐릭터의 정보가 그래프에 저장되었습니다.
데이터베이스 통계: {total_nodes}개 노드, {total_rels}개 관계""")
            
            return True
        except Exception as e:
            print(f"지식 그래프 생성 중 오류 발생: {e}")
            return False
    
    def process_design_document(self, file_path, clear_db=False):
        """게임 기획서 파일을 처리하여 지식 그래프를 생성합니다."""
        try:
            print(f"\n입력 파일: {file_path}")
            
            # 게임 기획서 읽기
            with open(file_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # 데이터베이스 초기화 (요청 시)
            if clear_db:
                self.clear_database()
            
            # 게임 제목 추출
            game_title = self.extract_game_title(markdown_content)
            print(f"\n게임 제목: {game_title}")
            
            # 챕터 정보 추출
            chapters = self.extract_chapters_from_markdown(markdown_content)
            if not chapters:
                print("경고: 챕터 정보를 찾을 수 없습니다.")
                print("참고: 챕터 개요 섹션에 '#### 챕터 N: 제목' 형식으로 챕터 정보가 있어야 합니다.")
                return False
            
            print(f"\n총 {len(chapters)}개 챕터 정보를 추출했습니다.")
            
            # 캐릭터 정보 추출
            characters = self.extract_characters(markdown_content)
            if not characters:
                print("캐릭터 정보를 찾을 수 없어서 기본 캐릭터를 사용합니다.")
                # 기본 캐릭터 추가
                if "Cosmic Drifters" in game_title:
                    characters.append({
                        'name': 'Alex Ryn',
                        'role': 'Protagonist',
                        'background': 'Rookie explorer driven by curiosity'
                    })
                elif "Arcana Quest" in game_title:
                    characters.append({
                        'name': 'Lumina',
                        'role': 'Protagonist',
                        'background': 'Young mage from a small village'
                    })
                else:
                    characters.append({
                        'name': '주인공',
                        'role': 'Protagonist',
                        'background': '게임의 주인공 캐릭터'
                    })
            else:
                print(f"\n총 {len(characters)}개의 캐릭터를 찾았습니다.")
            
            # 지식 그래프 생성
            success = self.create_knowledge_graph(game_title, chapters, characters)
            
            return success
        
        except Exception as e:
            print(f"게임 기획서 처리 중 오류 발생: {e}")
            return False

def find_latest_design_doc(output_dir):
    """output 폴더에서 가장 최근의 게임 기획서를 찾습니다."""
    md_files = glob.glob(os.path.join(output_dir, "*.md"))
    if not md_files:
        return None
    
    # 최근 파일 찾기
    latest_file = max(md_files, key=os.path.getmtime)
    return latest_file

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='게임 기획서의 챕터 개요를 Neo4j 지식 그래프로 변환')
    parser.add_argument('--input', type=str, help='게임 기획서 파일 경로')
    parser.add_argument('--clear', action='store_true', help='기존 Neo4j 데이터베이스를 초기화')
    parser.add_argument('--debug', action='store_true', help='디버그 모드 활성화')
    
    args = parser.parse_args()
    
    # 입력 파일 경로가 없으면 output 폴더에서 최신 파일 찾기
    input_file = args.input
    if not input_file:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
        input_file = find_latest_design_doc(output_dir)
        if not input_file:
            print("오류: 게임 기획서 파일을 찾을 수 없습니다.")
            return
    
    # 지식 그래프 생성기 초기화
    generator = ChapterKnowledgeGraphGenerator()
    
    if args.debug:
        generator.set_debug(True)
    
    try:
        # 게임 기획서 처리 및 지식 그래프 생성
        success = generator.process_design_document(input_file, args.clear)
        
        if success:
            print("\n처리가 완료되었습니다.")
        else:
            print("\n처리 중 오류가 발생했습니다.")
    
    finally:
        # 연결 종료
        generator.close()

if __name__ == "__main__":
    main()
