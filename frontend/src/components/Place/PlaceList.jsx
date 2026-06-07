/**
 * components/Place/PlaceList.jsx
 * 검색 결과 장소 목록 (지도 우측 패널).
 * 각 항목 클릭 시 상세 보기로 전환된다.
 */
import "./PlaceList.css";

const CAT_CLASS = { 카페: "c-cafe", 식당: "c-food", 숙소: "c-hotel", 공원: "c-park", 관광지: "c-tour" };
const CAT_EMOJI = { 카페: "☕", 식당: "🍽️", 숙소: "🏨", 공원: "🌿", 관광지: "📸", 문화시설: "🏛️", 쇼핑: "🛍️", 기타: "📍" };

export default function PlaceList({ places, selectedId, onSelect, title = "검색 결과" }) {
  return (
    <div className="place-list">
      <div className="list-header">
        <span className="list-title">{title}</span>
        <span className="list-count">{places.length.toLocaleString()}곳</span>
      </div>

      {places.length === 0 && (
        <div className="list-empty">
          <span style={{ fontSize: 32 }}>🔍</span>
          <p>이 지역에는 등록된 장소가 없어요.<br />지도를 옮기거나 필터를 바꿔보세요.</p>
        </div>
      )}

      {places.map((p) => (
        <button
          key={p.place_id}
          className={`place-item ${selectedId === p.place_id ? "sel" : ""}`}
          onClick={() => onSelect(p)}
        >
          <div className="place-top">
            <span className="place-name">
              {CAT_EMOJI[p.category] || "📍"} {p.place_name}
            </span>
            <span className={`place-badge ${CAT_CLASS[p.category] || ""}`}>{p.category}</span>
          </div>
          {p.address && <div className="place-addr">{p.address}</div>}
          <div className="place-meta">
            {p.average_rating > 0 && (
              <span className="place-rating">⭐ {p.average_rating}</span>
            )}
            <span className="place-reviews">리뷰 {p.total_reviews || 0}</span>
            {p.pet_size_limit && <span className="place-policy">{p.pet_size_limit}</span>}
          </div>
        </button>
      ))}
    </div>
  );
}
