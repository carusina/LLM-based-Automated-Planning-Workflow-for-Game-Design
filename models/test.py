# python -m models.test

from .game_design_generator import GameDesignGenerator

generator = GameDesignGenerator()

gdd = """
Game Design Document (GDD) Template

Cover Page
* Game Title: 차원의 수호자
* Genre: 액션 RPG
* Target Audience: 10대~20대 게이머
* Elevator Pitch: 차원을 넘나드는 모험을 통해 다양한 세계를 탐험하고 위기를 해결하는 액션 RPG

1. Project Overview
* Game Elements: 탐험, 전투, 퀘스트 수행, 차원 이동
* Number of Players: 싱글플레이

2. Technical Specifications
* Technical Form: 3D
* View: 3인칭
* Target Platform & Devices: PC, 콘솔
* Language & Engine: C#, Unity

3. Narrative Overview
* Story Synopsis: 주인공은 차원을 이동할 수 있는 능력을 가진 특별한 존재로, 각 차원에 숨겨진 위기를 해결하며 다양한 세계를 구해야 한다. 각 차원은 독특한 문화와 역사를 가지고 있으며, 주인공은 여정을 통해 자기 자신에 대한 진실을 발견하게 된다.
* Main Characters & Relationships:
  - 에리안: 차원 여행자로서 주인공의 길잡이 역할을 맡는 신비로운 존재. 지혜롭고 사려 깊은 성격으로, 주인공에게 조언을 아끼지 않는다.  
    플레이어와의 관계: 신뢰  
  - 카린: 불의 차원에서 만난 전사로, 강력한 전투력을 지녔다. 초기에 주인공을 경계하지만, 차차 우정을 쌓아간다.  
    플레이어와의 관계: 우호적  
  - 녹터: 어둠의 차원을 지배하는 강력한 마법사로, 여러 차원을 혼란에 빠뜨리려 한다. 주인공의 주요 적으로, 무자비하고 교활하다.  
    플레이어와의 관계: 적대적  
* World Lore & History: 차원들은 각각 고유의 역사와 문화를 가지고 있으며, 각 차원은 고대에 강력한 마법에 의해 연결되었다. 그러나 이 마법이 약해지면서 차원들 간의 균형이 깨지기 시작했다.
* Story Branching & Arcs: 특정 퀘스트나 선택에 따라 차원의 운명이 달라지며, 플레이어는 여러 가지 엔딩을 경험할 수 있다.

4. Gameplay Description
* Core Loop: 차원 탐험 → 적과의 전투 → 보상 획득 → 새로운 차원으로 이동
* Unique Mechanics: 차원 이동 능력, 차원별 고유 스킬
* Player Objectives: 
  - 장기 목표: 모든 차원의 위기를 해결하고 균형을 회복하기
  - 단기 목표: 퀘스트 완료, 특정 아이템 수집

5. Game Play Outline
* Start Flow: 게임 실행 → 메인 메뉴 → 옵션 선택 → 게임 시작
* Modes: 스토리 모드, 도전 모드
* Controls: 기본 이동(WASD), 공격(마우스 클릭), 스킬 사용(Q/E/R)
* Win/Lose Conditions: 
  - 승리: 모든 차원의 균형을 회복하고 주적을 물리침
  - 패배: 주인공의 체력이 모두 소진되거나 주요 퀘스트 실패
* Endings & Rewards: 선택에 따른 여러 가지 엔딩, 특별한 아이템 보상
* Fun Factor: 다양한 차원 탐험과 스킬 활용의 재미

6. Key Features
* 차원 이동을 통한 다양한 세계 탐험
* 차원마다 다른 전투 스킬과 전략 요구
* 선택에 따른 스토리 변형과 여러 가지 엔딩
* 독창적인 캐릭터와의 상호작용
* 몰입감 있는 배경음악과 사운드

7. Mechanics Design
1. Design Guidelines: 직관적인 차원 이동 및 전투 시스템
2. Game Design Definitions: 
   - 승리: 모든 차원의 문제 해결
   - 패배: 주요 퀘스트 실패 시
3. Flowchart: UI 흐름, 메인 루프, 상태 머신 다이어그램 (첨부 예정)

8. Player Definition
* Player Stats & Properties: 체력, 마나, 스킬 레벨
* Feedback Mechanisms: 피격 시 화면 흔들림, 사운드 효과
* Player Rewards: 파워업, 특별 아이템, 경험치

9. Level Design
  1. Level List & Unique Features
  * 불의 차원
    - Theme & Background Story: 화산과 용암이 흐르는 차원, 강력한 불의 생물들이 지키고 있다.  
    - Atmosphere & Art Direction: 붉은 톤의 하늘과 땅, 뜨거운 열기  
    - Core Mechanic & Unique Features: 
      - 용암 피하기 퍼즐  
      - 불의 정령들과의 전투  
      - 용암 속 숨겨진 보물 찾기  
    - Fun Elements: 스킬 연계를 통한 적 빠르게 처치하기, 숨겨진 보물 구역  
    
  * 물의 차원
    - Theme & Background Story: 물의 신비로운 생명체들이 사는 차원, 해류가 강하게 흐른다.  
    - Atmosphere & Art Direction: 푸른 바다와 하늘, 반짝이는 물결  
    - Core Mechanic & Unique Features: 
      - 해류를 이용한 이동 퍼즐  
      - 물속 생물들과의 전투  
      - 물 속 숨겨진 유물 찾기  
    - Fun Elements: 해류 타고 이동하기, 숨겨진 유물 수집 보너스  
    
  * 어둠의 차원
    - Theme & Background Story: 어둠의 힘이 지배하는 차원, 음울하고 불길한 분위기  
    - Atmosphere & Art Direction: 검은 하늘과 대지, 희미한 빛  
    - Core Mechanic & Unique Features: 
      - 어둠 속에서의 생존 퍼즐  
      - 어둠의 생명체들과의 전투  
      - 어둠 속 숨겨진 비밀 발견하기  
    - Fun Elements: 어둠 속 길 찾기, 랜덤 이벤트

  2. Difficulty Curve & Balancing
  * Difficulty Progression: 
    - 불의 차원: 초반(기본 전투, 쉬움) → 중반(용암 퍼즐, 보통) → 후반(보스 전투, 어려움)  
    - 물의 차원: 초반(해류 이용 이동, 보통) → 중반(물속 전투, 어려움) → 후반(숨겨진 유물 찾기, 매우 어려움)
    - 어둠의 차원: 초반(어둠 속 탐험, 보통) → 중반(어둠의 생물 전투, 어려움) → 후반(최종 보스, 매우 어려움)
  * Balancing Considerations: 
    - 스킬과 장비 업그레이드에 따른 적 난이도 조정
    - 주요 구간 전후 회복 아이템 배치
    - 첫 클리어 보상과 추가 도전 보상 차별화

10. UI/UX Design
* Control Mapping: WASD 이동, 마우스 클릭 공격, Q/E/R 스킬
* Wireframes & Mockups: 기본 화면 레이아웃 스케치 (첨부 예정)
* UX Considerations: 직관적인 메뉴, 접근성 설정

11. Art Direction
* Visual Style & References: 판타지 세계관, 다채로운 차원별 색상
* Character & Environment Art: 각 차원에 맞는 독특한 스타일
* UI Theme: 판타지 테마의 아이콘, 폰트, 컬러 팔레트

12. Audio Design
* Music Themes: 각 차원별 테마 음악
* Sound Effects: 전투, 이동, 상호작용 사운드
* Voice Over: 주요 캐릭터 대사, 내레이션

13. Monetization & Live Ops
* Business Model: F2P, 인앱결제
* Live Service Features: 이벤트, 시즌 패스
* Retention Mechanisms: 일일 보상, 주간 퀘스트

14. Metrics & KPIs
* Success Metrics: MAU, ARPU, 세션 길이
* Analytics Plan: 유니티 애널리틱스, 이벤트 트래킹

15. Production Plan
1. Roadmap & Milestones: MVP, 알파, 베타, 출시 일정 (첨부 예정)
2. Team & Roles: 기획, 아트, 개발, QA 담당자 (명단 첨부 예정)
3. Budget & Resources: 인건비, 소프트웨어 라이선스
4. Risk Assessment & Mitigation: 개발 일정 지연, 품질 이슈 대응 방안

16. Appendices
* Glossary: 주요 용어 정의
* References: 참고 자료, 레퍼런스 링크
* Diagrams & Charts: 전체 다이어그램 모음 (첨부 예정)
"""

gdd2 = """
# Game Design Document (GDD)

## Cover Page
* Game Title: 차원의 수호자
* Genre: 액션 RPG
* Target Audience: 10대~20대 게이머
* Elevator Pitch: 다양한 차원을 탐험하며 각 세계의 위기를 구하고 자신의 능력을 성장시키는 모험을 즐기는 게임

## 1. Project Overview
* Game Elements: 탐험, 전투, 퍼즐 해결, 캐릭터 성장
* Number of Players: 싱글 플레이어

## 2. Technical Specifications
* Technical Form: 3D
* View: 3인칭
* Target Platform & Devices: PC, Console
* Language & Engine: C#, Unity

## 3. Narrative Overview
* Story Synopsis: 차원 간 이동 능력을 가진 주인공이 각 차원의 위기를 해결하며 자신의 기원을 찾는 여정을 떠난다. 각 차원에는 고유의 도전과 비밀이 숨겨져 있다.
* Main Characters & Relationships:
    - 루시우스: 차원 이동 능력을 가진 주인공으로, 자신의 기원을 찾아 여러 차원을 여행한다.  
      플레이어와의 관계: 신뢰  
    - 엘라: 대지의 차원에서 만난 마법사로, 자연의 힘을 다룬다. 주인공에게 차원의 비밀을 알려주며 도움을 준다.  
      플레이어와의 관계: 우호적  
    - 모르가나: 어둠의 차원을 지배하는 악의 존재로, 주인공의 여행을 방해하며 차원에 혼란을 일으킨다.  
      플레이어와의 관계: 적대적  
* World Lore & History: 차원은 각기 다른 법칙과 생명체로 구성된 독립적인 세계이며, 이들 차원은 각각의 수호자에 의해 유지된다. 그러나 불균형이 발생하면서 주인공이 이를 해결하기 위한 여정을 시작한다.
* Story Branching & Arcs: 각 차원에서의 선택에 따라 다른 결과와 엔딩을 경험할 수 있으며, 주인공의 기원에 대한 진실도 변화한다.

## 4. Gameplay Description
* Core Loop: 탐험 → 전투 → 퍼즐 해결 → 보상 수집 → 능력 강화
* Unique Mechanics: 차원 이동을 통한 퍼즐 해결과 전투 방식, 각 차원의 고유한 능력 사용
* Player Objectives: 
  - 단기 목표: 각 차원의 위기 해결
  - 장기 목표: 모든 차원 탐험 및 자신의 기원을 찾기

## 5. Game Play Outline
* Start Flow: 게임 실행 → 인트로 시네마틱 → 메인 메뉴 → 옵션 설정 → 게임 시작
* Modes: 스토리 모드, 도전 모드
* Controls: 
  - 이동: WASD
  - 공격: 마우스 좌클릭
  - 차원 이동: 스페이스바
  - 능력 사용: 숫자 키 1~4
* Win/Lose Conditions: 각 차원의 보스를 물리치고 다음 차원으로 이동하면 승리, 주요 퀘스트 실패 시 패배
* Endings & Rewards: 선택에 따라 변화하는 엔딩, 엔딩에 따른 특별한 아이템 보상
* Fun Factor: 각기 다른 차원의 독특한 분위기와 도전 과제, 차원 이동을 통한 다양한 전략적 접근

## 6. Key Features
* 다양한 차원 세계와 고유한 비주얼
* 차원 이동을 활용한 창의적인 퍼즐과 전투
* 캐릭터 성장에 따른 다양한 스킬과 능력 해금
* 선택에 따른 다양한 스토리 분기와 엔딩
* 흥미로운 NPC와의 상호작용 및 관계 발전

## 7. Mechanics Design
1. Design Guidelines: 각 차원의 고유한 분위기를 살리면서도 일관된 게임 플레이 경험 제공
2. Game Design Definitions: 차원별 주요 퀘스트 완수로 승리, 모든 퀘스트 실패 시 패배
3. Flowchart: UI, 메인루프, 상태 머신 다이어그램

## 8. Player Definition
* Player Stats & Properties: 체력, 스태미나, 마나, 공격력, 방어력
* Feedback Mechanisms: 피격 시 캐릭터의 체력 감소와 시각적 이펙트, 사운드 피드백
* Player Rewards: 퀘스트 완료 시 경험치, 금화, 특별 아이템 보상

## 9. Level Design
  1. Level List & Unique Features
  * 대지의 차원
      - Theme & Background Story: 대지의 정령들이 지키는 풍요로운 자연 세계  
      - Atmosphere & Art Direction: 초록빛의 숲과 맑은 하늘  
      - Core Mechanic & Unique Features: 
      - 자연의 힘을 이용한 퍼즐  
      - 대지의 생물들과의 전투  
      - 숲 속 숨겨진 비밀 찾기  
      - Fun Elements: 자연과의 상호작용, 숨겨진 길 발견하기  

  * 물의 차원
      - Theme & Background Story: 물의 신비로운 생명체들이 사는 차원, 해류가 강하게 흐른다.  
      - Atmosphere & Art Direction: 푸른 바다와 하늘, 반짝이는 물결  
      - Core Mechanic & Unique Features: 
      - 해류를 이용한 이동 퍼즐  
      - 물속 생물들과의 전투  
      - 물 속 숨겨진 유물 찾기  
      - Fun Elements: 해류 타고 이동하기, 숨겨진 유물 수집 보너스  

  * 어둠의 차원
      - Theme & Background Story: 어둠의 힘이 지배하는 차원, 음울하고 불길한 분위기  
      - Atmosphere & Art Direction: 검은 하늘과 대지, 희미한 빛  
      - Core Mechanic & Unique Features: 
      - 어둠 속에서의 생존 퍼즐  
      - 어둠의 생명체들과의 전투  
      - 어둠 속 숨겨진 비밀 발견하기  
      - Fun Elements: 어둠 속 길 찾기, 랜덤 이벤트

  2. Difficulty Curve & Balancing
  * Difficulty Progression: 
      - 대지의 차원: 초반(친화적 퍼즐, 쉬움) → 중반(정령 전투, 보통) → 후반(보스 전투, 어려움)  
      - 물의 차원: 초반(해류 이용 이동, 보통) → 중반(물속 전투, 어려움) → 후반(숨겨진 유물 찾기, 매우 어려움)
      - 어둠의 차원: 초반(어둠 속 탐험, 보통) → 중반(어둠의 생물 전투, 어려움) → 후반(최종 보스, 매우 어려움)
  * Balancing Considerations: 
      - 스킬과 장비 업그레이드에 따른 적 난이도 조정
      - 주요 구간 전후 회복 아이템 배치
      - 첫 클리어 보상과 추가 도전 보상 차별화

## 10. UI/UX Design
* Control Mapping: 키보드 및 마우스 입력 방식, 직관적인 UI
* Wireframes & Mockups: 화면 레이아웃 스케치
* UX Considerations: 접근성, 인내도 관리

## 11. Art Direction
* Visual Style & References: 판타지 테마의 컨셉 아트, 자연과 마법의 조화
* Character & Environment Art: 부드러운 톤, 따뜻한 색감
* UI Theme: 아이콘, 폰트, 컬러 팔레트

## 12. Audio Design
* Music Themes: 각 차원의 분위기에 맞는 배경음악
* Sound Effects: 전투, 퍼즐, 차원 이동에 맞는 이펙트
* Voice Over: 주요 캐릭터의 대사 가이드

## 13. Monetization & Live Ops
* Business Model: 유료 게임
* Live Service Features: 주기적인 콘텐츠 업데이트, 이벤트
* Retention Mechanisms: 일일 보상, 주간 퀘스트

## 14. Metrics & KPIs
* Success Metrics: MAU, ARPU, 세션 길이
* Analytics Plan: 데이터 수집 툴, 이벤트 트래킹

## 15. Production Plan
1. Roadmap & Milestones: MVP, 알파, 베타, 출시 일정
2. Team & Roles: 기획, 아트, 개발, QA 담당자
3. Budget & Resources: 인건비, 소프트웨어 라이선스
4. Risk Assessment & Mitigation: 주요 리스크, 대응 방안

## 16. Appendices
* Glossary: 용어 정의
* References: 참고 자료, 논문, 레퍼런스 링크
* Diagrams & Charts: 전체 다이어그램 모음
"""

levels = generator.extract_gdd_core(gdd)
print(levels)