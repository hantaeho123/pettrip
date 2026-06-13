/**
 * components/Place/PlaceDetail.jsx
 * 장소 상세 정보 + 리뷰 목록 + 리뷰 작성(사진 업로드).
 *
 * - 상세 정보: 동반 정책, 시설, 운영시간 등 API 가공 데이터 표시
 * - 리뷰: 별점/사진과 함께 표시, 로그인 시 작성·삭제 가능
 */
import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { getPlaceDetail, getPlaceReviews, createReview, deleteReview, mediaUrl } from "../../api";
import "./PlaceDetail.css";

export default function PlaceDetail({ placeId, onBack }) {
  const { user } = useAuth();
  const [place, setPlace] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [writing, setWriting] = useState(false);
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [photo, setPhoto] = useState(null);

  const load = () => {
    getPlaceDetail(placeId).then(setPlace).catch(() => {});
    getPlaceReviews(placeId).then(setReviews).catch(() => setReviews([]));
  };
  useEffect(load, [placeId]);

  const handleSubmit = async () => {
    if (!user) return alert("로그인이 필요합니다.");
    const fd = new FormData();
    fd.append("place_id", placeId);
    fd.append("user_id", user.user_id);
    fd.append("rating", rating);
    fd.append("comment", comment);
    if (photo) fd.append("photo", photo);
    await createReview(fd);
    setComment(""); setPhoto(null); setRating(5); setWriting(false);
    load();
  };

  const handleDelete = async (reviewId) => {
    if (!window.confirm("리뷰를 삭제할까요?")) return;
    await deleteReview(reviewId, user.user_id);
    load();
  };

  if (!place) return <div className="detail-loading">불러오는 중...</div>;

  const infoRows = [
    ["🐕 동반 가능", place.pet_size_limit],
    ["📋 필요사항", place.pet_policy],
    ["🏠 실내 동반", place.is_indoor_allowed === true ? "가능" : place.is_indoor_allowed === false ? "불가" : null],
    ["🌳 야외 공간", place.has_outdoor_yard === true ? "있음" : place.has_outdoor_yard === false ? "없음" : null],
    ["🛎️ 비치 품목", place.amenities],
    ["🕐 운영시간", place.operating_hours],
    ["🚫 휴무일", place.closed_days],
    ["🅿️ 주차", place.parking_info],
  ].filter(([, v]) => v);

  return (
    <div className="place-detail">
      <button className="detail-back" onClick={onBack}>← 목록으로</button>

      <div className="detail-hero">
        {place.main_image_url ? (
          <img src={place.main_image_url} alt={place.place_name} />
        ) : (
          <div className="detail-hero-placeholder">🐾</div>
        )}
      </div>

      <div className="detail-body">
        <div className="detail-titlebar">
          <h2 className="detail-name">{place.place_name}</h2>
          <span className="detail-cat">{place.category}</span>
        </div>
        {place.address && <p className="detail-addr">📍 {place.address}</p>}

        <div className="detail-stats">
          <div className="stat">
            <span className="stat-num">⭐ {place.average_rating || 0}</span>
            <span className="stat-label">평균 평점</span>
          </div>
          <div className="stat">
            <span className="stat-num">{place.total_reviews || 0}</span>
            <span className="stat-label">리뷰 수</span>
          </div>
        </div>

        <div className="detail-section">
          <div className="section-title">동반 정보</div>
          <div className="info-table">
            {infoRows.map(([k, v]) => (
              <div className="info-row" key={k}>
                <span className="info-key">{k}</span>
                <span className="info-val" dangerouslySetInnerHTML={{ __html: v }} />
              </div>
            ))}
          </div>
        </div>

        <div className="detail-section">
          <div className="section-title">
            리뷰 {reviews.length}
            {user && (
              <button className="write-toggle" onClick={() => setWriting(!writing)}>
                {writing ? "취소" : "✏️ 리뷰 쓰기"}
              </button>
            )}
          </div>

          {writing && (
            <div className="review-form fade-in">
              <div className="star-picker">
                {[1, 2, 3, 4, 5].map((s) => (
                  <button key={s} className={s <= rating ? "star on" : "star"} onClick={() => setRating(s)}>★</button>
                ))}
              </div>
              <textarea placeholder="방문 경험을 들려주세요!" value={comment}
                onChange={(e) => setComment(e.target.value)} />
              <label className="photo-input">
                📷 {photo ? photo.name : "반려동물 사진 첨부 (선택)"}
                <input type="file" accept="image/*" hidden
                  onChange={(e) => setPhoto(e.target.files[0])} />
              </label>
              <button className="review-submit" onClick={handleSubmit}>등록하기</button>
            </div>
          )}

          {!user && <p className="login-hint">리뷰를 작성하려면 로그인하세요.</p>}

          <div className="review-list">
            {reviews.map((r) => (
              <div className="review-card" key={r.review_id}>
                <div className="review-head">
                  <span className="review-user">{r.nickname || "익명"}</span>
                  <span className="review-stars">{"⭐".repeat(r.rating)}</span>
                </div>
                {r.created_at && (
                  <span className="review-date">{new Date(r.created_at).toLocaleDateString("ko-KR")}</span>
                )}
                {r.photo_url && (
                  <img className="review-photo" src={mediaUrl(r.photo_url)} alt="리뷰 사진"
                    onError={(e) => (e.target.style.display = "none")} />
                )}
                <p className="review-text">{r.comment}</p>
                {user && user.user_id === r.user_id && (
                  <button className="review-del-btn" onClick={() => handleDelete(r.review_id)}>🗑️ 삭제</button>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
