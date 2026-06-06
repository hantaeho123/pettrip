import './FilterPanel.css';

const CATEGORIES = ['전체', '카페', '식당', '숙소', '공원', '관광지'];
const SIZES      = [
  { label: '전체',              value: '전체' },
  { label: '소형견 (10kg 미만)', value: '소형' },
  { label: '중형견 (10–20kg)',   value: '중형' },
  { label: '대형견 (20kg 이상)', value: '대형' },
];

export default function FilterPanel({ filters, onChange }) {
  const set = (key, val) => onChange(prev => ({ ...prev, [key]: val }));

  return (
    <div className="filter-panel">
      <div className="filter-label">카테고리</div>
      <div className="cat-grid">
        {CATEGORIES.map(c => (
          <button
            key={c}
            className={`cat-btn ${filters.category === c ? 'sel' : ''}`}
            onClick={() => set('category', c)}
          >
            {c}
          </button>
        ))}
      </div>

      <div className="filter-label">반려견 크기</div>
      {SIZES.map(s => (
        <div
          key={s.value}
          className={`size-row ${filters.size === s.value ? 'sel' : ''}`}
          onClick={() => set('size', s.value)}
        >
          <div className="size-dot" />
          <span>{s.label}</span>
        </div>
      ))}
    </div>
  );
}
