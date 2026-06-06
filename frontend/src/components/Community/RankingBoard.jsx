import { useState, useEffect } from 'react';
import { getRankingByBreed } from '../../api';
import './RankingBoard.css';

const BREEDS = ['웰시코기', '골든리트리버', '말티즈', '비숑프리제', '시바이누'];
const CAT_EMOJI = { 식당: '🍽️', 카페: '☕', 숙소: '🏨', 공원: '🌿', 관광지: '📸' };
const MEDAL = ['🥇', '🥈', '🥉'];

export default function RankingBoard() {
  const [breed,   setBreed]   = useState('웰시코기');
  const [ranking, setRanking] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    getRankingByBreed(breed)
      .then(setRanking)
      .catch(() => setRanking([]))
      .finally(() => setLoading(false));
  }, [breed]);

  return (
    <div className="ranking-board">
      <div className="rank-header">
        <span className="rank-title">🏆 견종별 인기 스팟</span>
        <select value={breed} onChange={e => setBreed(e.target.value)} className="breed-select">
          {BREEDS.map(b => <option key={b}>{b}</option>)}
        </select>
      </div>

      {loading && <p className="rank-loading">불러오는 중...</p>}

      <div className="rank-list">
        {ranking.map((item, i) => (
          <div key={item.place_id} className="rank-item">
            <div className="rank-num">{MEDAL[i] || i + 1}</div>
            <div className="rank-emoji">{CAT_EMOJI[item.category] || '📍'}</div>
            <div className="rank-info">
              <div className="rank-name">{item.place_name}</div>
              <div className="rank-cat">{item.category}</div>
            </div>
            <div className="rank-score">
              <div className="rank-rating">⭐ {item.avg_rating}</div>
              <div className="rank-count">리뷰 {item.review_count}개</div>
            </div>
          </div>
        ))}
        {!loading && ranking.length === 0 && (
          <p className="rank-empty">아직 데이터가 없습니다.</p>
        )}
      </div>
    </div>
  );
}
