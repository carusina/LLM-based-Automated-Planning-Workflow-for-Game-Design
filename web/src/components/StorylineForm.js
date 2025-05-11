import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const StorylineForm = () => {
  const [formData, setFormData] = useState({
    gddId: '',
    chapters: 5
  });
  
  const [availableGdds, setAvailableGdds] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingGdds, setIsLoadingGdds] = useState(true);
  const [error, setError] = useState('');
  const [result, setResult] = useState('');
  const [downloadLinks, setDownloadLinks] = useState(null);

  // GDD 목록 로드
  useEffect(() => {
    const fetchGdds = async () => {
      try {
        const response = await axios.get('/api/available_gdds');
        setAvailableGdds(response.data.gdds || []);
      } catch (err) {
        console.error('Error fetching GDDs:', err);
        setError('GDD 목록을 불러오는 중 오류가 발생했습니다.');
      } finally {
        setIsLoadingGdds(false);
      }
    };

    fetchGdds();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: name === 'chapters' ? parseInt(value, 10) : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setResult('');
    setDownloadLinks(null);
    
    try {
      const response = await axios.post('/api/generate_storyline', formData);
      setResult(response.data.storyline);
      setDownloadLinks(response.data.downloads || {});
    } catch (err) {
      setError(err.response?.data?.error || '스토리라인 생성 중 오류가 발생했습니다.');
      console.error('Error generating storyline:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const isFormValid = () => {
    return formData.gddId && formData.chapters > 0;
  };

  return (
    <div className="form-container">
      <h2>스토리라인 생성</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="gddId">게임 디자인 문서 선택</label>
          {isLoadingGdds ? (
            <div className="loading">
              <div className="spinner"></div>
            </div>
          ) : (
            <select
              id="gddId"
              name="gddId"
              value={formData.gddId}
              onChange={handleChange}
              required
            >
              <option value="">-- GDD 선택 --</option>
              {availableGdds.map((gdd) => (
                <option key={gdd.id} value={gdd.id}>
                  {gdd.title || gdd.id}
                </option>
              ))}
            </select>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="chapters">챕터 수</label>
          <input
            type="number"
            id="chapters"
            name="chapters"
            min="1"
            max="20"
            value={formData.chapters}
            onChange={handleChange}
            required
          />
        </div>

        <button
          type="submit"
          className="submit-btn"
          disabled={!isFormValid() || isLoading}
        >
          {isLoading ? '생성 중...' : '스토리라인 생성하기'}
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
          <h3>생성된 스토리라인</h3>
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

export default StorylineForm;