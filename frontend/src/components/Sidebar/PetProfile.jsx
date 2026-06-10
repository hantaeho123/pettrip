/**
 * components/Sidebar/PetProfile.jsx
 * 반려동물 프로필 패널.
 * - 펫 등록 (사진 + 이름/견종/몸무게)
 * - 초대코드 표시 → 가족에게 공유
 * - 초대코드 입력 → 공동 소유 등록
 * - 펫 선택 시 맞춤 추천 필터 적용
 */
import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { getUserPets, createPet, joinByInviteCode, mediaUrl } from "../../api";
import "./PetProfile.css";

export default function PetProfile({ selectedPet, onSelectPet }) {
  const { user } = useAuth();
  const [pets, setPets] = useState([]);
  const [mode, setMode] = useState(null); // null | 'add' | 'join'
  const [form, setForm] = useState({ pet_name: "", pet_breed: "", pet_weight: "" });
  const [photo, setPhoto] = useState(null);
  const [joinCode, setJoinCode] = useState("");
  const [msg, setMsg] = useState("");

  const loadPets = () => {
    if (!user) { setPets([]); return; }
    getUserPets(user.user_id).then(setPets).catch(() => setPets([]));
  };
  useEffect(loadPets, [user]);

  const handleAdd = async () => {
    if (!form.pet_name) return;
    const fd = new FormData();
    fd.append("pet_name", form.pet_name);
    fd.append("pet_breed", form.pet_breed || "");
    fd.append("pet_weight", form.pet_weight || "");
    fd.append("user_id", user.user_id);
    if (photo) fd.append("photo", photo);
    await createPet(fd);
    setForm({ pet_name: "", pet_breed: "", pet_weight: "" });
    setPhoto(null);
    setMode(null);
    loadPets();
  };

  const handleJoin = async () => {
    if (!joinCode.trim()) return;
    try {
      const res = await joinByInviteCode(joinCode.trim(), user.user_id);
      setMsg(res.message);
      setJoinCode("");
      setMode(null);
      loadPets();
    } catch (e) {
      setMsg(e.response?.data?.detail || "등록 실패");
    }
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
        <span className="pet-actions">
          <button className="pet-action-btn" onClick={() => setMode(mode === "add" ? null : "add")}>
            {mode === "add" ? "닫기" : "+ 등록"}
          </button>
          <button className="pet-action-btn join" onClick={() => setMode(mode === "join" ? null : "join")}>
            {mode === "join" ? "닫기" : "🔗 공동등록"}
          </button>
        </span>
      </div>

      {msg && <p className="pet-msg fade-in">{msg}</p>}

      {/* 새 반려견 등록 폼 */}
      {mode === "add" && (
        <div className="pet-add-form fade-in">
          <label className="pet-photo-upload">
            {photo ? `📷 ${photo.name}` : "📷 강아지 사진 첨부"}
            <input type="file" accept="image/*" hidden onChange={(e) => setPhoto(e.target.files[0])} />
          </label>
          <input placeholder="이름 *" value={form.pet_name}
            onChange={(e) => setForm({ ...form, pet_name: e.target.value })} />
          <input placeholder="견종 (예: 웰시코기)" value={form.pet_breed}
            onChange={(e) => setForm({ ...form, pet_breed: e.target.value })} />
          <input placeholder="몸무게(kg)" type="number" value={form.pet_weight}
            onChange={(e) => setForm({ ...form, pet_weight: e.target.value })} />
          <button className="pet-save-btn" onClick={handleAdd}>등록하기</button>
        </div>
      )}

      {/* 초대코드로 공동 등록 */}
      {mode === "join" && (
        <div className="pet-join-form fade-in">
          <p className="pet-join-desc">가족이 공유한 초대코드를 입력하세요</p>
          <div className="pet-join-row">
            <input placeholder="초대코드 6자리" value={joinCode} maxLength={6}
              onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
              onKeyDown={(e) => e.key === "Enter" && handleJoin()} />
            <button onClick={handleJoin}>등록</button>
          </div>
        </div>
      )}

      {/* 펫 목록 */}
      <div className="pet-list">
        {pets.length === 0 && !mode && (
          <p className="pet-empty">아직 등록된 반려견이 없어요.</p>
        )}
        {pets.map((p) => (
          <button
            key={p.pet_id}
            className={`pet-card ${selectedPet?.pet_id === p.pet_id ? "sel" : ""}`}
            onClick={() => onSelectPet(selectedPet?.pet_id === p.pet_id ? null : p)}
          >
            <div className="pet-avatar">
              {p.photo_url ? (
                <img src={mediaUrl(p.photo_url)} alt={p.pet_name}
                  onError={(e) => { e.target.style.display = "none"; e.target.nextSibling.style.display = "flex"; }} />
              ) : null}
              <span className="pet-avatar-fallback" style={p.photo_url ? { display: "none" } : {}}>🐕</span>
            </div>
            <span className="pet-info">
              <span className="pet-name">{p.pet_name}</span>
              <span className="pet-breed">{p.pet_breed || "견종 미상"} · {p.pet_weight || "?"}kg</span>
              {p.invite_code && (
                <span className="pet-code" title="이 코드를 가족에게 공유하세요"
                  onClick={(e) => { e.stopPropagation(); navigator.clipboard.writeText(p.invite_code); setMsg("초대코드가 복사되었습니다!"); }}>
                  초대코드: {p.invite_code} 📋
                </span>
              )}
            </span>
            {selectedPet?.pet_id === p.pet_id && <span className="pet-check">✓</span>}
          </button>
        ))}
      </div>
    </div>
  );
}
