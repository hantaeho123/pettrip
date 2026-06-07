/**
 * components/Sidebar/FilterPanel.jsx
 * 카테고리 + 반려견 크기 필터 패널.
 * 시나리오 3(개인화 필터)과 연계되며, 선택 시 부모의 filters 상태를 갱신한다.
 */
import "./FilterPanel.css";

const CATEGORIES = [
  { label: "전체", icon: "🐾" },
  { label: "카페", icon: "☕" },
  { label: "식당", icon: "🍽️" },
  { label: "숙소", icon: "🏨" },
  { label: "공원", icon: "🌿" },
  { label: "관광지", icon: "📸" },
];

const SIZES = [
  { label: "전체", value: null },
  { label: "소형견 (10kg 미만)", value: 10 },
  { label: "중형견 (~20kg)", value: 20 },
  { label: "대형견 (20kg 이상)", value: 25 },
];

export default function FilterPanel({ filters, onChange }) {
  const set = (patch) => onChange((prev) => ({ ...prev, ...patch }));

  return (
    <div className="filter-panel">
      <div className="filter-label">카테고리</div>
      <div className="cat-grid">
        {CATEGORIES.map((c) => (
          <button
            key={c.label}
            className={`cat-btn ${filters.category === c.label ? "sel" : ""}`}
            onClick={() => set({ category: c.label })}
          >
            <span className="cat-emoji">{c.icon}</span>
            {c.label}
          </button>
        ))}
      </div>

      <div className="filter-label">반려견 크기</div>
      <div className="size-list">
        {SIZES.map((s) => (
          <button
            key={s.label}
            className={`size-row ${filters.maxWeight === s.value ? "sel" : ""}`}
            onClick={() => set({ maxWeight: s.value })}
          >
            <span className="size-dot" />
            {s.label}
          </button>
        ))}
      </div>

      <label className="indoor-toggle">
        <input
          type="checkbox"
          checked={filters.indoorOnly || false}
          onChange={(e) => set({ indoorOnly: e.target.checked })}
        />
        <span>실내 동반 가능한 곳만</span>
      </label>
    </div>
  );
}
