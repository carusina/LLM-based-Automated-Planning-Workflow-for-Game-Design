import React, { useRef, useState, useEffect } from 'react';
import HTMLFlipBook from 'react-pageflip';
import './App.css';

function App() {
  const bookRef = useRef();
  const [targetPage, setTargetPage] = useState(null);

  useEffect(() => {
    if (targetPage !== null && bookRef.current) {
      bookRef.current.pageFlip().flip(targetPage);
      setTargetPage(null); // 다시 초기화
    }
  }, [targetPage]);

  return (
    <div className="App">
      <div className="nav">
        <button onClick={() => setTargetPage(0)}>개요</button>
        <button onClick={() => setTargetPage(2)}>기능</button>
        <button onClick={() => setTargetPage(4)}>타임라인</button>
        <button onClick={() => setTargetPage(6)}>팀소개</button>
      </div>

      <HTMLFlipBook
        width={600}
        height={500}
        size="stretch"
        minWidth={315}
        maxWidth={1000}
        minHeight={400}
        maxHeight={1536}
        maxShadowOpacity={0.5}
        showCover={false}
        mobileScrollSupport={true}
        ref={bookRef}
      >
        <div className="page">
          <h2>01. 개요</h2>
          <p>이 프로젝트는 시각장애인을 위한 주식 자동매매 시스템을 목표로 합니다. 음성 명령, 보조기능, 접근성 향상에 집중합니다.</p>
        </div>

        <div className="page">
          <h2>02. 문제 배경</h2>
          <p>시각장애인에게 제공되는 금융 서비스는 매우 제한적이며, 실시간 피드백과 접근성 높은 UI/UX가 필요합니다.</p>
        </div>

        <div className="page">
          <h2>03. 주요 기능</h2>
          <p>음성 기반 매매, 실시간 시세 조회, 차트 음성 해설, WCAG 2.1 AA 대응 UI 등이 포함됩니다.</p>
        </div>

        <div className="page">
          <h2>04. 시스템 구조</h2>
          <p>React + Flask API + 증권사 API 연동, 음성 인식 모듈과 챗봇 처리 구조로 구성됩니다.</p>
        </div>

        <div className="page">
          <h2>05. 개발 일정</h2>
          <p>1월~2월: 기획 / 3월~5월: 기능 구현 / 6월~7월: 테스트 및 발표</p>
        </div>

        <div className="page">
          <h2>06. 기대 효과</h2>
          <p>접근성 향상을 통한 금융소외 해소, 사용자 편의성 강화 및 기술적 가치 창출</p>
        </div>

        <div className="page">
          <h2>07. 팀소개</h2>
          <p>기획: 김OO / 프론트엔드: 이OO / 백엔드: 박OO / 음성처리: 정OO</p>
        </div>

        <div className="page">
          <h2>08. 기타</h2>
          <p>기타 기술 스택, 향후 확장 계획, API 제한 대응 방안 등</p>
        </div>
      </HTMLFlipBook>
    </div>
  );
}

export default App;
