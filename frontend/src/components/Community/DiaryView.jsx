/**
 * components/Community/DiaryView.jsx
 * 멍트립 다이어리 (시나리오 2).
 * 내 반려견을 고르면, 공동 소유자(가족)가 그 아이와 다녀온 곳까지
 * 통합해서 방문 이력을 보여준다. (N:M user_pet_map JOIN)
 */
import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { getUserPets, getPetDiary } from "../../api";
import "./DiaryView.css";

export default function DiaryView() {
  const { user } = useAuth();
  const [pets, setPets] = useState([]);
  const [petId, setPetId] = useState(null);
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    if (!user) return;
    getUserPets(user.user_id).then((list) => {
      setPets(list);
      if (list.length) setPetId(list[0].pet_id);
    }).catch(() => {});
  }, [user]);

  useEffect(() => {
    if (!petId) return;
    getPetDiary(petId).then(setEntries).catch(() => setEntries([]));
  }, [petId]);

  if (!user) {
    return <div className="diary-guard">로그인하면 우리 강아지의 발자국을 모아볼 수 있어요 🐾</div>;
  }

  const currentPet = pets.find((p) => p.pet_id === petId);

  return (
    <div className="diary">
      <div className="diary-header">
        <h1>🐾 멍트립 다이어리</h1>
        <p>가족이 함께 등록한 우리 아이의 통합 방문 이력</p>
      </div>

      {pets.length === 0 ? (
        <div className="diary-empty">먼저 반려견을 등록해주세요 (지도 화면 왼쪽 패널).</div>
      ) : (
        <>
          <div className="diary-pet-tabs">
            {pets.map((p) => (
              <button key={p.pet_id}
                className={`diary-pet ${petId === p.pet_id ? "sel" : ""}`}
                onClick={() => setPetId(p.pet_id)}>
                🐕 {p.pet_name}
              </button>
            ))}
          </div>

          {entries.length === 0 ? (
            <div className="diary-empty">
              <b>{currentPet?.pet_name}</b>의 방문 이력이 아직 없어요.
            </div>
          ) : (
            <div className="diary-timeline">
              {entries.map((e, i) => (
                <div className="diary-entry fade-up" key={i}>
                  <div className="diary-dot" />
                  <div className="diary-content">
                    <div className="diary-top">
                      <span className="diary-place">{e.place_name}</span>
                      <span className="diary-stars">{"⭐".repeat(e.rating)}</span>
                    </div>
                    {e.comment && <p className="diary-comment">{e.comment}</p>}
                    <span className="diary-by">
                      {e.nickname}님이 기록 · {e.pet_name}와 함께
                      {e.created_at && ` · ${new Date(e.created_at).toLocaleDateString("ko-KR")}`}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
