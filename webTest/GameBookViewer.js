import React, { useRef, useEffect } from "react";
import HTMLFlipBook from "react-pageflip";

const GameBookViewer = ({ pages }) => {
  const bookRef = useRef();

  useEffect(() => {
    if (bookRef.current) {
      bookRef.current.pageFlip().flip(0); // 처음 페이지부터 시작
    }
  }, []);

  return (
    <div>
      <HTMLFlipBook ref={bookRef} width={600} height={400}>
        {pages.map((page, index) => (
          <div key={index} className="page">
            <h2>{page.title}</h2>
            <p>{page.text}</p>
          </div>
        ))}
      </HTMLFlipBook>
    </div>
  );
};

export default GameBookViewer;
