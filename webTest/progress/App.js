import React, { useState, useRef, useEffect } from 'react';
import HTMLFlipBook from 'react-pageflip';
import './App.css';

function App() {
  const bookRef = useRef();
  const [activeTab, setActiveTab] = useState('list'); // list, view, edit, generate
  const [selectedPlanId, setSelectedPlanId] = useState(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [plans, setPlans] = useState(() => {
    const savedPlans = localStorage.getItem('gamePlans');
    return savedPlans ? JSON.parse(savedPlans) : [];
  });
  const [planData, setPlanData] = useState({
    id: Date.now(),
    title: "게임 기획서",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    genre: "",
    setting: "",
    theme: "",
    worldBuilding: {
      overview: "",
      factions: [],
      locations: [],
      history: ""
    },
    characters: {
      mainCharacters: [],
      npcs: [],
      relationships: []
    },
    story: {
      mainPlot: "",
      subplots: [],
      quests: []
    },
    gameMechanics: {
      coreLoop: "",
      progression: "",
      combat: "",
      exploration: ""
    },
    visualStyle: {
      artDirection: "",
      keyVisuals: []
    },
    additionalNotes: ""
  });

  useEffect(() => {
    localStorage.setItem('gamePlans', JSON.stringify(plans));
  }, [plans]);

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (selectedPlanId) {
      setPlans(plans.map(plan => 
        plan.id === selectedPlanId 
          ? { ...planData, updatedAt: new Date().toISOString() }
          : plan
      ));
    } else {
      setPlans([...plans, { ...planData, id: Date.now(), createdAt: new Date().toISOString() }]);
    }
    setActiveTab('list');
  };

  const handleGenerateContent = async (section) => {
    // TODO: LLM API 호출 구현
    console.log(`Generating content for ${section}`);
  };

  const handleEditPlan = (plan) => {
    setPlanData(plan);
    setSelectedPlanId(plan.id);
    setActiveTab('edit');
  };

  const handleViewPlan = (plan) => {
    setPlanData(plan);
    setSelectedPlanId(plan.id);
    setActiveTab('view');
  };

  const handleNewPlan = () => {
    setPlanData({
      id: Date.now(),
      title: "새 게임 기획서",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      genre: "",
      setting: "",
      theme: "",
      worldBuilding: {
        overview: "",
        factions: [],
        locations: [],
        history: ""
      },
      characters: {
        mainCharacters: [],
        npcs: [],
        relationships: []
      },
      story: {
        mainPlot: "",
        subplots: [],
        quests: []
      },
      gameMechanics: {
        coreLoop: "",
        progression: "",
        combat: "",
        exploration: ""
      },
      visualStyle: {
        artDirection: "",
        keyVisuals: []
      },
      additionalNotes: ""
    });
    setSelectedPlanId(null);
    setActiveTab('edit');
  };

  const handleDeletePlan = (planId) => {
    if (window.confirm('정말로 이 기획서를 삭제하시겠습니까?')) {
      setPlans(plans.filter(plan => plan.id !== planId));
    }
  };

  const handleSectionChange = (section) => {
    const pageMap = {
      'basic': 0,    // 기본 정보는 0-1 페이지
      'world': 2,    // 세계관은 2-3 페이지
      'character': 4, // 캐릭터는 4-5 페이지
      'story': 6,    // 스토리는 6-7 페이지
      'gameplay': 8  // 게임플레이는 8-9 페이지
    };

    // 현재 페이지가 해당 섹션의 페이지 범위에 있는지 확인
    const isInSection = (currentPage >= pageMap[section] && currentPage <= pageMap[section] + 1);
    
    // 현재 섹션에 있다면 다음 페이지로, 아니면 섹션의 첫 페이지로 이동
    const targetPage = isInSection ? pageMap[section] + 1 : pageMap[section];
    
    // 페이지 이동
    setTimeout(() => {
      bookRef.current.pageFlip().flip(targetPage);
      setCurrentPage(targetPage);
    }, 100);
  };

  const handlePageChange = (pageNumber) => {
    bookRef.current.pageFlip().flip(pageNumber);
    setCurrentPage(pageNumber);
  };

  const renderPlanList = () => (
    <div className="plan-list">
      <div className="plan-list-header">
        <h2>게임 기획서 목록</h2>
        <button className="new-plan-btn" onClick={handleNewPlan}>
          새 기획서 작성
        </button>
      </div>
      <div className="plan-grid">
        {plans.map(plan => (
          <div key={plan.id} className="plan-card">
            <h3>{plan.title}</h3>
            <p className="plan-date">
              작성일: {new Date(plan.createdAt).toLocaleDateString()}
              <br />
              수정일: {new Date(plan.updatedAt).toLocaleDateString()}
            </p>
            <div className="plan-actions">
              <button onClick={() => handleViewPlan(plan)}>보기</button>
              <button onClick={() => handleEditPlan(plan)}>편집</button>
              <button onClick={() => handleDeletePlan(plan.id)} className="delete-btn">삭제</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="App">
      <header className="App-header">
        <h1>LLM 기반 게임 기획 자동화</h1>
        <div className="tabs">
          <button 
            className={activeTab === 'list' ? 'active' : ''} 
            onClick={() => setActiveTab('list')}
          >
            기획서 목록
          </button>
          {activeTab === 'view' && (
            <button 
              className={activeTab === 'view' ? 'active' : ''} 
              onClick={() => setActiveTab('view')}
            >
              기획서 보기
            </button>
          )}
          {activeTab === 'edit' && (
            <button 
              className={activeTab === 'edit' ? 'active' : ''} 
              onClick={() => setActiveTab('edit')}
            >
              기획서 편집
            </button>
          )}
        </div>
      </header>
      <main>
        {activeTab === 'list' ? (
          renderPlanList()
        ) : activeTab === 'view' ? (
          <div className="game-plan-book">
            <div className="book-navigation">
              <button 
                className={currentPage <= 1 ? 'active' : ''} 
                onClick={() => handleSectionChange('basic')}
              >
                기본 정보
              </button>
              <button 
                className={currentPage >= 2 && currentPage <= 3 ? 'active' : ''} 
                onClick={() => handleSectionChange('world')}
              >
                세계관
              </button>
              <button 
                className={currentPage >= 4 && currentPage <= 5 ? 'active' : ''} 
                onClick={() => handleSectionChange('character')}
              >
                캐릭터
              </button>
              <button 
                className={currentPage >= 6 && currentPage <= 7 ? 'active' : ''} 
                onClick={() => handleSectionChange('story')}
              >
                스토리
              </button>
              <button 
                className={currentPage >= 8 && currentPage <= 9 ? 'active' : ''} 
                onClick={() => handleSectionChange('gameplay')}
              >
                게임플레이
              </button>
            </div>

            <HTMLFlipBook
              width={800}
              height={600}
              size="stretch"
              minWidth={315}
              maxWidth={1200}
              minHeight={400}
              maxHeight={1536}
              maxShadowOpacity={0}
              showCover={true}
              mobileScrollSupport={true}
              ref={bookRef}
              onFlip={(e) => setCurrentPage(e.data)}
              flippingTime={500}
              usePortrait={false}
              startZIndex={0}
              autoSize={true}
              clickEventForward={false}
              useMouseEvents={true}
              swipeDistance={0}
              showPageCorners={false}
              disableFlipByClick={false}
              onInit={() => {
                // 초기 페이지 설정
                setCurrentPage(0);
              }}
            >
              {/* 표지 */}
              <div className="page cover">
                <h1>{planData.title}</h1>
                <p className="date">{new Date().toLocaleDateString()}</p>
                <div className="genre-tags">
                  <span>{planData.genre}</span>
                  <span>{planData.setting}</span>
                  <span>{planData.theme}</span>
                </div>
              </div>

              {/* 기본 정보 - 1쪽 */}
              <div className="page">
                <h2>01. 기본 정보</h2>
                <div className="content">
                  <h3>장르</h3>
                  <p>{planData.genre}</p>
                  
                  <h3>배경 설정</h3>
                  <p>{planData.setting}</p>
                </div>
              </div>

              {/* 기본 정보 - 2쪽 */}
              <div className="page">
                <h2>01. 기본 정보</h2>
                <div className="content">
                  <h3>주제</h3>
                  <p>{planData.theme}</p>
                </div>
              </div>

              {/* 세계관 - 1쪽 */}
              <div className="page">
                <h2>02. 세계관</h2>
                <div className="content">
                  <h3>개요</h3>
                  <p>{planData.worldBuilding.overview}</p>

                  <h3>세력</h3>
                  <ul>
                    {planData.worldBuilding.factions.map((faction, index) => (
                      <li key={index}>{faction}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* 세계관 - 2쪽 */}
              <div className="page">
                <h2>02. 세계관</h2>
                <div className="content">
                  <h3>주요 장소</h3>
                  <ul>
                    {planData.worldBuilding.locations.map((location, index) => (
                      <li key={index}>{location}</li>
                    ))}
                  </ul>

                  <h3>역사</h3>
                  <p>{planData.worldBuilding.history}</p>
                </div>
              </div>

              {/* 캐릭터 - 1쪽 */}
              <div className="page">
                <h2>03. 캐릭터</h2>
                <div className="content">
                  <h3>주인공</h3>
                  <ul>
                    {planData.characters.mainCharacters.map((character, index) => (
                      <li key={index}>{character}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* 캐릭터 - 2쪽 */}
              <div className="page">
                <h2>03. 캐릭터</h2>
                <div className="content">
                  <h3>NPC</h3>
                  <ul>
                    {planData.characters.npcs.map((npc, index) => (
                      <li key={index}>{npc}</li>
                    ))}
                  </ul>

                  <h3>관계도</h3>
                  <ul>
                    {planData.characters.relationships.map((relationship, index) => (
                      <li key={index}>{relationship}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* 스토리 - 1쪽 */}
              <div className="page">
                <h2>04. 스토리</h2>
                <div className="content">
                  <h3>메인 플롯</h3>
                  <p>{planData.story.mainPlot}</p>

                  <h3>서브 플롯</h3>
                  <ul>
                    {planData.story.subplots.map((subplot, index) => (
                      <li key={index}>{subplot}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* 스토리 - 2쪽 */}
              <div className="page">
                <h2>04. 스토리</h2>
                <div className="content">
                  <h3>퀘스트</h3>
                  <ul>
                    {planData.story.quests.map((quest, index) => (
                      <li key={index}>{quest}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* 게임플레이 - 1쪽 */}
              <div className="page">
                <h2>05. 게임플레이</h2>
                <div className="content">
                  <h3>핵심 루프</h3>
                  <p>{planData.gameMechanics.coreLoop}</p>

                  <h3>진행 시스템</h3>
                  <p>{planData.gameMechanics.progression}</p>
                </div>
              </div>

              {/* 게임플레이 - 2쪽 */}
              <div className="page">
                <h2>05. 게임플레이</h2>
                <div className="content">
                  <h3>전투 시스템</h3>
                  <p>{planData.gameMechanics.combat}</p>

                  <h3>탐험 시스템</h3>
                  <p>{planData.gameMechanics.exploration}</p>

                  <h3>시각적 스타일</h3>
                  <p>{planData.visualStyle.artDirection}</p>
                </div>
              </div>
            </HTMLFlipBook>
          </div>
        ) : (
          <div className="form-container">
            <h2>기획서 {selectedPlanId ? '수정' : '작성'}</h2>
            <form onSubmit={handleFormSubmit}>
              <div className="form-section">
                <h3>기본 정보</h3>
                <div className="form-group">
                  <label htmlFor="title">제목</label>
                  <input
                    type="text"
                    id="title"
                    value={planData.title}
                    onChange={(e) => setPlanData({...planData, title: e.target.value})}
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="genre">장르</label>
                  <input
                    type="text"
                    id="genre"
                    value={planData.genre}
                    onChange={(e) => setPlanData({...planData, genre: e.target.value})}
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="setting">배경 설정</label>
                  <input
                    type="text"
                    id="setting"
                    value={planData.setting}
                    onChange={(e) => setPlanData({...planData, setting: e.target.value})}
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="theme">주제</label>
                  <input
                    type="text"
                    id="theme"
                    value={planData.theme}
                    onChange={(e) => setPlanData({...planData, theme: e.target.value})}
                    required
                  />
                </div>
              </div>

              <div className="form-section">
                <h3>세계관</h3>
                <div className="form-group">
                  <label htmlFor="worldOverview">세계관 개요</label>
                  <textarea
                    id="worldOverview"
                    value={planData.worldBuilding.overview}
                    onChange={(e) => setPlanData({
                      ...planData,
                      worldBuilding: {...planData.worldBuilding, overview: e.target.value}
                    })}
                    required
                  />
                  <button 
                    type="button" 
                    className="generate-btn"
                    onClick={() => handleGenerateContent('worldOverview')}
                  >
                    AI로 생성
                  </button>
                </div>

                <div className="form-group">
                  <label htmlFor="factions">세력 (각 항목을 새 줄로 구분)</label>
                  <textarea
                    id="factions"
                    value={planData.worldBuilding.factions.join('\n')}
                    onChange={(e) => setPlanData({
                      ...planData,
                      worldBuilding: {
                        ...planData.worldBuilding,
                        factions: e.target.value.split('\n').filter(f => f.trim())
                      }
                    })}
                    required
                  />
                  <button 
                    type="button" 
                    className="generate-btn"
                    onClick={() => handleGenerateContent('factions')}
                  >
                    AI로 생성
                  </button>
                </div>

                <div className="form-group">
                  <label htmlFor="locations">주요 장소 (각 항목을 새 줄로 구분)</label>
                  <textarea
                    id="locations"
                    value={planData.worldBuilding.locations.join('\n')}
                    onChange={(e) => setPlanData({
                      ...planData,
                      worldBuilding: {
                        ...planData.worldBuilding,
                        locations: e.target.value.split('\n').filter(l => l.trim())
                      }
                    })}
                    required
                  />
                  <button 
                    type="button" 
                    className="generate-btn"
                    onClick={() => handleGenerateContent('locations')}
                  >
                    AI로 생성
                  </button>
                </div>

                <div className="form-group">
                  <label htmlFor="history">역사</label>
                  <textarea
                    id="history"
                    value={planData.worldBuilding.history}
                    onChange={(e) => setPlanData({
                      ...planData,
                      worldBuilding: {...planData.worldBuilding, history: e.target.value}
                    })}
                    required
                  />
                  <button 
                    type="button" 
                    className="generate-btn"
                    onClick={() => handleGenerateContent('history')}
                  >
                    AI로 생성
                  </button>
                </div>
              </div>

              <div className="form-section">
                <h3>캐릭터</h3>
                <div className="form-group">
                  <label htmlFor="mainCharacters">주인공 (각 항목을 새 줄로 구분)</label>
                  <textarea
                    id="mainCharacters"
                    value={planData.characters.mainCharacters.join('\n')}
                    onChange={(e) => setPlanData({
                      ...planData,
                      characters: {
                        ...planData.characters,
                        mainCharacters: e.target.value.split('\n').filter(c => c.trim())
                      }
                    })}
                    required
                  />
                  <button 
                    type="button" 
                    className="generate-btn"
                    onClick={() => handleGenerateContent('mainCharacters')}
                  >
                    AI로 생성
                  </button>
                </div>

                <div className="form-group">
                  <label htmlFor="npcs">NPC (각 항목을 새 줄로 구분)</label>
                  <textarea
                    id="npcs"
                    value={planData.characters.npcs.join('\n')}
                    onChange={(e) => setPlanData({
                      ...planData,
                      characters: {
                        ...planData.characters,
                        npcs: e.target.value.split('\n').filter(n => n.trim())
                      }
                    })}
                    required
                  />
                  <button 
                    type="button" 
                    className="generate-btn"
                    onClick={() => handleGenerateContent('npcs')}
                  >
                    AI로 생성
                  </button>
                </div>

                <div className="form-group">
                  <label htmlFor="relationships">관계도 (각 항목을 새 줄로 구분)</label>
                  <textarea
                    id="relationships"
                    value={planData.characters.relationships.join('\n')}
                    onChange={(e) => setPlanData({
                      ...planData,
                      characters: {
                        ...planData.characters,
                        relationships: e.target.value.split('\n').filter(r => r.trim())
                      }
                    })}
                    required
                  />
                  <button 
                    type="button" 
                    className="generate-btn"
                    onClick={() => handleGenerateContent('relationships')}
                  >
                    AI로 생성
                  </button>
                </div>
              </div>

              <div className="form-section">
                <h3>스토리</h3>
                <div className="form-group">
                  <label htmlFor="mainPlot">메인 플롯</label>
                  <textarea
                    id="mainPlot"
                    value={planData.story.mainPlot}
                    onChange={(e) => setPlanData({
                      ...planData,
                      story: {...planData.story, mainPlot: e.target.value}
                    })}
                    required
                  />
                  <button 
                    type="button" 
                    className="generate-btn"
                    onClick={() => handleGenerateContent('mainPlot')}
                  >
                    AI로 생성
                  </button>
                </div>

                <div className="form-group">
                  <label htmlFor="subplots">서브 플롯 (각 항목을 새 줄로 구분)</label>
                  <textarea
                    id="subplots"
                    value={planData.story.subplots.join('\n')}
                    onChange={(e) => setPlanData({
                      ...planData,
                      story: {
                        ...planData.story,
                        subplots: e.target.value.split('\n').filter(s => s.trim())
                      }
                    })}
                    required
                  />
                  <button 
                    type="button" 
                    className="generate-btn"
                    onClick={() => handleGenerateContent('subplots')}
                  >
                    AI로 생성
                  </button>
                </div>

                <div className="form-group">
                  <label htmlFor="quests">퀘스트 (각 항목을 새 줄로 구분)</label>
                  <textarea
                    id="quests"
                    value={planData.story.quests.join('\n')}
                    onChange={(e) => setPlanData({
                      ...planData,
                      story: {
                        ...planData.story,
                        quests: e.target.value.split('\n').filter(q => q.trim())
                      }
                    })}
                    required
                  />
                  <button 
                    type="button" 
                    className="generate-btn"
                    onClick={() => handleGenerateContent('quests')}
                  >
                    AI로 생성
                  </button>
                </div>
              </div>

              <div className="form-section">
                <h3>게임플레이</h3>
                <div className="form-group">
                  <label htmlFor="coreLoop">핵심 루프</label>
                  <textarea
                    id="coreLoop"
                    value={planData.gameMechanics.coreLoop}
                    onChange={(e) => setPlanData({
                      ...planData,
                      gameMechanics: {...planData.gameMechanics, coreLoop: e.target.value}
                    })}
                    required
                  />
                  <button 
                    type="button" 
                    className="generate-btn"
                    onClick={() => handleGenerateContent('coreLoop')}
                  >
                    AI로 생성
                  </button>
                </div>

                <div className="form-group">
                  <label htmlFor="progression">진행 시스템</label>
                  <textarea
                    id="progression"
                    value={planData.gameMechanics.progression}
                    onChange={(e) => setPlanData({
                      ...planData,
                      gameMechanics: {...planData.gameMechanics, progression: e.target.value}
                    })}
                    required
                  />
                  <button 
                    type="button" 
                    className="generate-btn"
                    onClick={() => handleGenerateContent('progression')}
                  >
                    AI로 생성
                  </button>
                </div>

                <div className="form-group">
                  <label htmlFor="combat">전투 시스템</label>
                  <textarea
                    id="combat"
                    value={planData.gameMechanics.combat}
                    onChange={(e) => setPlanData({
                      ...planData,
                      gameMechanics: {...planData.gameMechanics, combat: e.target.value}
                    })}
                    required
                  />
                  <button 
                    type="button" 
                    className="generate-btn"
                    onClick={() => handleGenerateContent('combat')}
                  >
                    AI로 생성
                  </button>
                </div>

                <div className="form-group">
                  <label htmlFor="exploration">탐험 시스템</label>
                  <textarea
                    id="exploration"
                    value={planData.gameMechanics.exploration}
                    onChange={(e) => setPlanData({
                      ...planData,
                      gameMechanics: {...planData.gameMechanics, exploration: e.target.value}
                    })}
                    required
                  />
                  <button 
                    type="button" 
                    className="generate-btn"
                    onClick={() => handleGenerateContent('exploration')}
                  >
                    AI로 생성
                  </button>
                </div>

                <div className="form-group">
                  <label htmlFor="artDirection">시각적 스타일</label>
                  <textarea
                    id="artDirection"
                    value={planData.visualStyle.artDirection}
                    onChange={(e) => setPlanData({
                      ...planData,
                      visualStyle: {...planData.visualStyle, artDirection: e.target.value}
                    })}
                    required
                  />
                  <button 
                    type="button" 
                    className="generate-btn"
                    onClick={() => handleGenerateContent('artDirection')}
                  >
                    AI로 생성
                  </button>
                </div>
              </div>

              <div className="form-actions">
                <button type="submit" className="submit-btn">
                  {selectedPlanId ? '수정 완료' : '기획서 생성'}
                </button>
                <button 
                  type="button" 
                  className="cancel-btn"
                  onClick={() => setActiveTab('list')}
                >
                  취소
                </button>
              </div>
            </form>
          </div>
        )}
      </main>
      <footer>
        <p>© 2025 LLM 기반 게임 기획 자동화</p>
      </footer>
    </div>
  );
}

export default App;
