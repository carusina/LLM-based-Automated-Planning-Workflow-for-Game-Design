import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const GameDesignForm = () => {
  const [formData, setFormData] = useState({
    idea: '',
    genre: '',
    target: '',
    concept: ''
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState('');
  const [downloadLinks, setDownloadLinks] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setResult('');
    setDownloadLinks(null);
    
    try {
      const response = await axios.post('/api/generate_gdd', formData);
      setResult(response.data.gdd);
      setDownloadLinks(response.data.downloads || {});
    } catch (err) {
      setError(err.response?.data?.error || 'GDD 생성 중 오류가 발생했습니다.');
      console.error('Error generating GDD:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const isFormValid = () => {
    return formData.idea && formData.genre && formData.target && formData.concept;
  };

  return (
    <div className="form-container">
      <h2>게임 디자인 문서(GDD) 생성</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="idea">게임 아이디어</label>
          <textarea
            id="idea"
            name="idea"
            value={formData.idea}
            onChange={handleChange}
            placeholder="게임의 핵심 아이디어를 설명해주세요"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="genre">장르</label>
          <input
            type="text"
            id="genre"
            name="genre"
            value={formData.genre}
            onChange={handleChange}
            placeholder="RPG, 액션, 퍼즐 등"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="target">타겟 오디언스</label>
          <input
            type="text"
            id="target"
            name="target"
            value={formData.target}
            onChange={handleChange}
            placeholder="10대, 캐주얼 게이머, 하드코어 게이머 등"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="concept">컨셉</label>
          <textarea
            id="concept"
            name="concept"
            value={formData.concept}
            onChange={handleChange}
            placeholder="게임의 주요 컨셉과 특징을 설명해주세요"
            required
          />
        </div>

        <button
          type="submit"
          className="submit-btn"
          disabled={!isFormValid() || isLoading}
        >
          {isLoading ? '생성 중...' : 'GDD 생성하기'}
        </button>
      </form>

      {isLoading && (
        <div className="loading">
          <div className="spinner"></div>
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="result-container">
          <h3>생성된 GDD</h3>
          <ReactMarkdown>{result}</ReactMarkdown>
          
          {downloadLinks && (
            <div className="download-options">
              <h4>다운로드:</h4>
              {downloadLinks.md && (
                <a
                  href={downloadLinks.md}
                  download
                  className="download-btn"
                >
                  Markdown
                </a>
              )}
              {downloadLinks.pdf && (
                <a
                  href={downloadLinks.pdf}
                  download
                  className="download-btn"
                >
                  PDF
                </a>
              )}
              {downloadLinks.txt && (
                <a
                  href={downloadLinks.txt}
                  download
                  className="download-btn"
                >
                  Text
                </a>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default GameDesignForm;