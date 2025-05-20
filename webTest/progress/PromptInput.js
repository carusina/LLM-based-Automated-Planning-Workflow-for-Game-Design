import React, { useState } from "react";

const PromptInput = ({ onSubmit }) => {
  const [input, setInput] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(input);  // 입력받은 값 전달
    setInput(""); // 입력창 초기화
  };

  return (
    <div>
      <h2>게임 기획서를 작성하세요</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="예: 다크 판타지 게임"
        />
        <button type="submit">생성</button>
      </form>
    </div>
  );
};

export default PromptInput;
