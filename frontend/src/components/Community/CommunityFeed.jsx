/**
 * components/Community/CommunityFeed.jsx
 * 자랑하기 게시판 — 반려동물 사진과 방문 후기를 공유하는 커뮤니티.
 *
 * 사용법:
 *  1. 상단 "자랑글 쓰기" 클릭
 *  2. 다녀온 장소를 검색해서 선택
 *  3. 반려동물 사진 첨부 + 한줄평 작성
 *  4. 등록하면 피드에 카드로 표시됨
 *
 * 내부적으로는 place_reviews에 photo_url이 있는 리뷰를 보여주는 구조.
 */
import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { getCommunityFeed, getPlaces, createReview, mediaUrl } from "../../api";
import "./CommunityFeed.css";

export default function CommunityFeed() {
  const { user } = useAuth();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [writing, setWriting] = useState(false);

  // 글쓰기 폼 상태
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [selectedPlace, setSelectedPlace] = useState(null);
  const [comment, setComment] = useState("");
  const [rating, setRating] = useState(5);
  const [photo, setPhoto] = useState(null);

  const loadFeed = () => {
    setLoading(true);
    getCommunityFeed(50)
      .then(setPosts)
      .catch(() => setPosts([]))
      .finally(() => setLoading(false));
  };
  useEffect(loadFeed, []);

  // 장소 검색
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    try {
      const results = await getPlaces({ keyword: searchQuery, limit: 10 });
      setSearchResults(results);
    } catch { setSearchResults([]); }
  };

  // 자랑글 등록
  const handlePost = async () => {
    if (!selectedPlace || !photo) return alert("장소와 사진을 모두 선택해주세요!");
    const fd = new FormData();
    fd.append("place_id", selectedPlace.place_id);
    fd.append("user_id", user.user_id);
    fd.append("rating", rating);
    fd.append("comment", comment);
    fd.append("photo", photo);
    await createReview(fd);
    // 초기화
    setWriting(false);
    setSelectedPlace(null);
    setComment("");
    setRating(5);
    setPhoto(null);
    setSearchQuery("");
    setSearchResults([]);
    loadFeed();
  };

  return (
    <div className="community">
      <div className="community-header">
        <div>
          <h1>🐶 자랑하기</h1>
          <p>반려동물과 다녀온 곳에서 찍은 사진을 공유해보세요!</p>
        </div>
        {user && (
          <button className="brag-write-btn" onClick={() => setWriting(!writing)}>
            {writing ? "닫기" : "📷 자랑글 쓰기"}
          </button>
        )}
      </div>

      {/* ── 자랑글 작성 폼 ── */}
      {writing && (
        <div className="brag-form fade-in">
          <div className="brag-form-title">우리 아이 자랑하기 ✨</div>

          {/* 장소 검색 */}
          <div className="brag-place-search">
            <div className="brag-search-row">
              <input placeholder="다녀온 장소를 검색하세요 (예: 한강공원)" value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()} />
              <button onClick={handleSearch}>검색</button>
            </div>
            {searchResults.length > 0 && !selectedPlace && (
              <div className="brag-search-results">
                {searchResults.map((p) => (
                  <button key={p.place_id} className="brag-search-item"
                    onClick={() => { setSelectedPlace(p); setSearchResults([]); }}>
                    📍 {p.place_name} <span>{p.category}</span>
                  </button>
                ))}
              </div>
            )}
            {selectedPlace && (
              <div className="brag-selected-place">
                📍 {selectedPlace.place_name}
                <button onClick={() => setSelectedPlace(null)}>✕</button>
              </div>
            )}
          </div>

          {/* 사진 + 평점 + 코멘트 */}
          <label className="brag-photo-input">
            {photo ? `📷 ${photo.name}` : "📷 반려동물 사진을 올려주세요 *"}
            <input type="file" accept="image/*" hidden onChange={(e) => setPhoto(e.target.files[0])} />
          </label>

          <div className="brag-rating-row">
            <span>평점</span>
            <div className="star-picker">
              {[1, 2, 3, 4, 5].map((s) => (
                <button key={s} className={s <= rating ? "star on" : "star"} onClick={() => setRating(s)}>★</button>
              ))}
            </div>
          </div>

          <textarea placeholder="어떤 곳이었나요? 우리 아이는 좋아했나요?" value={comment}
            onChange={(e) => setComment(e.target.value)} />

          <button className="brag-submit" onClick={handlePost}
            disabled={!selectedPlace || !photo}>
            자랑하기 🐾
          </button>
        </div>
      )}

      {!user && !loading && (
        <div className="brag-login-cta">
          로그인하면 우리 아이 자랑글을 쓸 수 있어요! 🐾
        </div>
      )}

      {/* ── 피드 ── */}
      {loading ? (
        <div className="community-loading">불러오는 중...</div>
      ) : posts.length === 0 ? (
        <div className="community-empty">
          <span style={{ fontSize: 40 }}>📷</span>
          <p>아직 자랑글이 없어요.<br />첫 자랑글의 주인공이 되어보세요!</p>
        </div>
      ) : (
        <div className="brag-grid">
          {posts.map((p) => (
            <div className="brag-card fade-up" key={p.review_id}>
              <div className="brag-photo">
                <img src={mediaUrl(p.photo_url)} alt="자랑 사진"
                  onError={(e) => { e.target.parentElement.classList.add("no-img"); e.target.remove(); }} />
                <span className="brag-rating-badge">{"⭐".repeat(p.rating)}</span>
              </div>
              <div className="brag-body">
                {p.place_name && <span className="brag-place">📍 {p.place_name}</span>}
                <p className="brag-comment">{p.comment}</p>
                <span className="brag-user">— {p.nickname}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
