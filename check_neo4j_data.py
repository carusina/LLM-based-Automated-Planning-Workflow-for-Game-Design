#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Neo4j 데이터베이스에 저장된 챕터 지식 그래프를 확인합니다.
"""

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# Neo4j 연결 정보
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

def run_query(driver, query, parameters=None):
    """Neo4j Cypher 쿼리를 실행합니다."""
    with driver.session() as session:
        result = session.run(query, parameters or {})
        return list(result)

def print_section(title):
    """섹션 제목을 출력합니다."""
    print("\n" + "=" * 50)
    print(f" {title}")
    print("=" * 50)

def main():
    """메인 함수"""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        # 게임 정보 조회
        print_section("게임 정보")
        game_query = "MATCH (g:Game) RETURN g.title AS title"
        games = run_query(driver, game_query)
        
        for game in games:
            print(f"게임 제목: {game['title']}")
        
        # 챕터 정보 조회
        print_section("챕터 정보")
        chapter_query = """
        MATCH (g:Game)-[:HAS_CHAPTER]->(c:Chapter)
        RETURN g.title AS game, c.number AS number, c.title AS title
        ORDER BY g.title, c.number
        """
        chapters = run_query(driver, chapter_query)
        
        current_game = None
        for chapter in chapters:
            if current_game != chapter['game']:
                current_game = chapter['game']
                print(f"\n[{current_game}]")
            print(f"  챕터 {chapter['number']}: {chapter['title']}")
        
        # 캐릭터 정보 조회
        print_section("캐릭터 정보")
        character_query = """
        MATCH (g:Game)-[:HAS_CHARACTER]->(c:Character)
        RETURN g.title AS game, c.name AS name, c.role AS role
        ORDER BY g.title
        """
        characters = run_query(driver, character_query)
        
        current_game = None
        for character in characters:
            if current_game != character['game']:
                current_game = character['game']
                print(f"\n[{current_game}]")
            print(f"  {character['name']} ({character['role']})")
        
        # 챕터별 위치 정보 조회
        print_section("위치 정보")
        location_query = """
        MATCH (g:Game)-[:HAS_CHAPTER]->(c:Chapter)-[:TAKES_PLACE_AT]->(l:Location)
        RETURN g.title AS game, c.number AS chapter, c.title as chapter_title, 
               l.name AS location, l.type AS type
        ORDER BY g.title, c.number
        """
        locations = run_query(driver, location_query)
        
        current_chapter = None
        for location in locations:
            chapter_key = f"{location['game']} - 챕터 {location['chapter']}"
            if current_chapter != chapter_key:
                current_chapter = chapter_key
                print(f"\n[{chapter_key}: {location['chapter_title']}]")
            print(f"  {location['location']} ({location['type']})")
        
        # 챕터별 사건 정보 조회
        print_section("사건 정보")
        event_query = """
        MATCH (g:Game)-[:HAS_CHAPTER]->(c:Chapter)-[:CONTAINS_EVENT]->(e:Event)
        RETURN g.title AS game, c.number AS chapter, e.name AS event
        ORDER BY g.title, c.number
        """
        events = run_query(driver, event_query)
        
        current_chapter = None
        for event in events:
            chapter_key = f"{event['game']} - 챕터 {event['chapter']}"
            if current_chapter != chapter_key:
                current_chapter = chapter_key
                print(f"\n[{chapter_key}]")
            print(f"  {event['event']}")
        
        # 챕터 순서 관계 조회
        print_section("챕터 순서")
        chapter_order_query = """
        MATCH (g:Game)-[:HAS_CHAPTER]->(c1:Chapter)-[:FOLLOWED_BY]->(c2:Chapter)
        RETURN g.title AS game, c1.number AS from_chapter, c1.title AS from_title,
               c2.number AS to_chapter, c2.title AS to_title
        ORDER BY g.title, c1.number
        """
        chapter_orders = run_query(driver, chapter_order_query)
        
        current_game = None
        for order in chapter_orders:
            if current_game != order['game']:
                current_game = order['game']
                print(f"\n[{current_game}]")
            print(f"  챕터 {order['from_chapter']} ({order['from_title']}) -> 챕터 {order['to_chapter']} ({order['to_title']})")
        
        # 캐릭터와 이벤트 관계 조회
        print_section("캐릭터-이벤트 관계")
        character_event_query = """
        MATCH (g:Game)-[:HAS_CHARACTER]->(ch:Character)-[:PARTICIPATES_IN]->(e:Event)<-[:CONTAINS_EVENT]-(c:Chapter)
        RETURN g.title AS game, ch.name AS character, e.name AS event, c.number AS chapter
        ORDER BY g.title, c.number
        """
        character_events = run_query(driver, character_event_query)
        
        current_character = None
        for relation in character_events:
            character_key = f"{relation['game']} - {relation['character']}"
            if current_character != character_key:
                current_character = character_key
                print(f"\n[{character_key}]")
            print(f"  챕터 {relation['chapter']}: {relation['event']}")
        
    finally:
        driver.close()

if __name__ == "__main__":
    main()
