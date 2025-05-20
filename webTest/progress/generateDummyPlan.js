const generateDummyPlan = (prompt) => {
  // 예시로 기획서 데이터를 생성
  if (prompt.includes("다크 판타지")) {
    return [
      { title: "개요", text: "다크 판타지 게임: 왕국 확장과 전투 중심의 RPG" },
      { title: "세계관", text: "마법과 기술이 혼합된 세상에서 왕국 간 전투" },
      { title: "주요 기능", text: "게임 내 전투, 자원 관리, 퀘스트 및 스토리라인" },
      { title: "타임라인", text: "1단계: 기획 / 2단계: 디자인 / 3단계: 구현" },
      { title: "팀 소개", text: "기획: 홍길동 / 개발: 김철수 / 아트: 이영희" },
    ];
  }

  // 기본 기획서 내용
  return [
    { title: "기본 기획서", text: "기본적인 게임 기획서 내용이 들어갑니다." }
  ];
};

export default generateDummyPlan;
