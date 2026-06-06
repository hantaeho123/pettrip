import { useEffect, useState } from 'react';
import { getReviews } from '../../api';
import './PlaceDetail.css';

export default function PlaceDetail({ place, onBack }) {
  const [reviews, setReviews] = useState([]);

  useEffect(() => {
    if (!place) return;
    getReviews(place.place_id).then(setReviews).catch(() => setReviews([]));
  }, [place]);

  if (!place) return null;

  const policies = place.pet_policy?.split(',').map(s => s.trim()) || [];

  return (
    <div className="place-detail">
      <button className="back-btn" onClick={onBack}>← 목록으로</button>

      <div className="detail-header">
        <div className="detail-name">{place.place_name}</div>
        <span className="detail-cat">{place.category}</span>
      </div>

      <div className="detail-section">
        <div className="sec-title">동반 정책</div>
        {policies.map((p, i) => (
          <div key={i} className="policy-row">✅ {p}</div>
        ))}
      </div>

      <div className="detail-section">
        <div className="sec-title">리뷰 ({reviews.length})</div>
        {reviews.length === 0 && <p className="no-review">아직 리뷰가 없습니다.</p>}
        {reviews.map(r => (
          <div key={r.review_id} className="review-card">
            <div className="review-top">
              <span className="reviewer">{r.nickname || '익명'}</span>
              <span className="review-stars">{'⭐'.repeat(r.rating)}</span>
            </div>
            <p className="review-text">{r.comment}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
