/**
 * components/Sidebar/PetProfile.jsx
 * 로그인한 유저의 반려동물 프로필 목록.
 * 펫을 선택하면 그 펫 기준으로 맞춤 추천 필터가 적용된다 (시나리오 4).
 * 비로그인 시에는 로그인 유도 메시지를 보여준다.
 */
import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { getUserPets, createPet } from "../../api";
import "./PetProfile.css";

export default function PetProfile({ selectedPet, onSelectPet }) {
  const { user } = useAuth();
  const [pets, setPets] = useState([]);
  const [adding, setAdding] = useState(false);
  const [form, setForm] = useState({ pet_name: "", pet_breed: "", pet_weight: "" });

  const loadPets = () => {
    if (!user) { setPets([]); return; }
    getUserPets(user.user_id).then(setPets).catch(() => setPets([]));
  };

  useEffect(loadPets, [user]);

  const handleAdd = async () => {
    if (!form.pet_name) return;
    await createPet(
      { ...form, pet_weight: parseFloat(form.pet_weight) || null },
      user.user_id
    );
    setForm({ pet_name: "", pet_breed: "", pet_weight: "" });
    setAdding(false);
    loadPets();
  };

  if (!user) {
    return (
      <div className="pet-profile">
        <div className="pet-label">내 반려견</div>
        <p className="pet-login-hint">로그인하면 반려견을 등록하고<br />맞춤 추천을 받을 수 있어요 🐾</p>
      </div>
    );
  }

  return (
    <div className="pet-profile">
      <div className="pet-label">
        내 반려견
        <button className="pet-add-btn" onClick={() => setAdding(!adding)}>
          {adding ? "닫기" : "+ 등록"}
        </button>
      </div>

      {adding && (
        <div className="pet-add-form fade-in">
          <input placeholder="이름" value={form.pet_name}
            onChange={(e) => setForm({ ...form, pet_name: e.target.value })} />
          <input placeholder="견종 (예: 웰시코기)" value={form.pet_breed}
            onChange={(e) => setForm({ ...form, pet_breed: e.target.value })} />
          <input placeholder="몸무게(kg)" type="number" value={form.pet_weight}
            onChange={(e) => setForm({ ...form, pet_weight: e.target.value })} />
          <button className="pet-save-btn" onClick={handleAdd}>등록하기</button>
        </div>
      )}

      <div className="pet-list">
        {pets.length === 0 && !adding && (
          <p className="pet-empty">아직 등록된 반려견이 없어요.</p>
        )}
        {pets.map((p) => (
          <button
            key={p.pet_id}
            className={`pet-card ${selectedPet?.pet_id === p.pet_id ? "sel" : ""}`}
            onClick={() => onSelectPet(selectedPet?.pet_id === p.pet_id ? null : p)}
          >
            <span className="pet-avatar">🐕</span>
            <span className="pet-info">
              <span className="pet-name">{p.pet_name}</span>
              <span className="pet-breed">{p.pet_breed || "견종 미상"} · {p.pet_weight || "?"}kg</span>
            </span>
            {selectedPet?.pet_id === p.pet_id && <span className="pet-check">✓</span>}
          </button>
        ))}
      </div>
    </div>
  );
}
