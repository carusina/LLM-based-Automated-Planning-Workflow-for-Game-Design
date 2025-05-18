import React, { useState } from 'react';
import GameDesignForm from './components/GameDesignForm';
import StorylineForm from './components/StorylineForm';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('gdd');

  return (
    <div className="App">
      <header className="App-header">
        <h1>게임 디자인 & 스토리라인 생성기</h1>
        <div className="tabs">
          <button 
            className={activeTab === 'gdd' ? 'active' : ''} 
            onClick={() => setActiveTab('gdd')}
          >
            게임 디자인 문서(GDD)
          </button>
          <button 
            className={activeTab === 'storyline' ? 'active' : ''} 
            onClick={() => setActiveTab('storyline')}
          >
            스토리라인
          </button>
        </div>
      </header>
      <main>
        {activeTab === 'gdd' ? (
          <GameDesignForm />
        ) : (
          <StorylineForm />
        )}
      </main>
      <footer>
        <p>© 2025 게임 디자인 & 스토리라인 생성기</p>
      </footer>
    </div>
  );
}

export default App;