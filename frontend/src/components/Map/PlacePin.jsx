const CAT_COLORS = {
  식당: '#1D9E75',
  카페: '#D85A30',
  숙소: '#7F77DD',
  공원: '#639922',
};

const CAT_EMOJI = { 식당: '🍽️', 카페: '☕', 숙소: '🏨', 공원: '🌿', 관광지: '📸' };

export default function PlacePin({ place, onClick }) {
  const color = CAT_COLORS[place.category] || '#1D9E75';
  const emoji = CAT_EMOJI[place.category] || '📍';

  return (
    <div onClick={() => onClick(place)} style={{ cursor: 'pointer', display: 'inline-flex', flexDirection: 'column', alignItems: 'center' }}>
      <div style={{
        background: color,
        color: '#fff',
        padding: '4px 10px',
        borderRadius: 12,
        fontSize: 12,
        fontWeight: 500,
        whiteSpace: 'nowrap',
        boxShadow: '0 2px 6px rgba(0,0,0,0.15)',
      }}>
        {emoji} {place.place_name}
      </div>
      <div style={{
        width: 0, height: 0,
        borderLeft: '5px solid transparent',
        borderRight: '5px solid transparent',
        borderTop: `7px solid ${color}`,
      }} />
    </div>
  );
}
