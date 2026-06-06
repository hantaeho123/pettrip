import './PlaceList.css';

const CAT_CLASS = { 식당: 'cat-restaurant', 카페: 'cat-cafe', 숙소: 'cat-hotel', 공원: 'cat-park' };
const CAT_EMOJI = { 식당: '🍽️', 카페: '☕', 숙소: '🏨', 공원: '🌿', 관광지: '📸' };

export default function PlaceList({ places, onSelect, selectedId }) {
  return (
    <div className="place-list">
      <div className="list-header">
        <span className="list-title">검색 결과</span>
        <span className="list-count">{places.length}개 장소</span>
      </div>
      {places.map(p => (
        <div
          key={p.place_id}
          className={`place-item ${selectedId === p.place_id ? 'sel' : ''}`}
          onClick={() => onSelect(p)}
        >
          <div className="place-top">
            <span className="place-name">{CAT_EMOJI[p.category]} {p.place_name}</span>
            <span className={`place-badge ${CAT_CLASS[p.category] || ''}`}>{p.category}</span>
          </div>
          <div className="place-addr">{p.latitude?.toFixed(4)}, {p.longitude?.toFixed(4)}</div>
          <div className="place-policy">{p.pet_policy?.split(',')[0]}</div>
        </div>
      ))}
    </div>
  );
}
