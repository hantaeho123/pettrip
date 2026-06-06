import './PetProfile.css';

// 실제 구현 시 props나 전역 상태(Context, Zustand 등)에서 유저 정보 주입
const MOCK_PET = { name: '초코', breed: '골든리트리버', weight: 25 };

export default function PetProfile() {
  return (
    <div className="pet-profile">
      <div className="pet-label">내 반려견 프로필</div>
      <div className="pet-card">
        <div className="pet-avatar">🐕</div>
        <div>
          <div className="pet-name">{MOCK_PET.name}</div>
          <div className="pet-breed">{MOCK_PET.breed} · {MOCK_PET.weight}kg</div>
        </div>
      </div>
    </div>
  );
}
