/**
 * components/Community/RankingBoard.jsx
 * 견종별 인기 스팟 랭킹 (시나리오 5).
 * 견종을 고르면 그 견종 견주들이 높은 평점을 준 장소 TOP 10을 보여준다.
 */
import { useState, useEffect } from "react";
import { getBreedList, getBreedRanking } from "../../api";
import "./RankingBoard.css";

export default function RankingBoard() {
  const [breeds, setBreeds] = useState([]);
  const [breed, setBreed] = useState("");
  const [ranking, setRanking] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getBreedList().then((list) => {
      setBreeds(list);
      if (list.length) setBreed(list.includes("웰시코기") ? "웰시코기" : list[0]);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!breed) return;
    setLoading(true);
    getBreedRanking(breed)
      .then(setRanking)
      .catch(() => setRanking([]))
      .finally(() => setLoading(false));
  }, [breed]);

  const medal = (i) => (i === 0 ? "🥇" : i === 1 ? "🥈" : i === 2 ? "🥉" : `${i + 1}`);

  return (
    <div className="ranking">
      <div className="ranking-header">
        <h1>🏆 견종별 인기 스팟</h1>
        <p>같은 견종 친구들이 별점 4점 이상 준 인기 장소를 모았어요</p>
      </div>

      <div className="breed-selector">
        <label>견종 선택</label>
        <select value={breed} onChange={(e) => setBreed(e.target.value)}>
          {breeds.map((b) => <option key={b} value={b}>{b}</option>)}
        </select>
      </div>

      {loading ? (
        <div className="ranking-loading">집계 중...</div>
      ) : ranking.length === 0 ? (
        <div className="ranking-empty">
          <p>아직 <b>{breed}</b> 견주의 충분한 평가가 없어요.</p>
        </div>
      ) : (
        <div className="ranking-list">
          {ranking.map((r, i) => (
            <div className={`rank-row ${i < 3 ? "top" : ""} fade-up`} key={r.place_id}>
              <span className="rank-medal">{medal(i)}</span>
              <div className="rank-info">
                <span className="rank-name">{r.place_name}</span>
                <span className="rank-cat">{r.category}</span>
              </div>
              <div className="rank-score">
                <span className="rank-rating">⭐ {r.avg_rating}</span>
                <span className="rank-count">리뷰 {r.review_count}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
