/**
 * components/Community/CommunityFeed.jsx
 * 자랑게시판 - 사진이 첨부된 리뷰를 카드 그리드로 보여준다.
 * 보고서의 '반려동물 자랑하기' 커뮤니티 기능.
 */
import { useState, useEffect } from "react";
import { getCommunityFeed, mediaUrl } from "../../api";
import "./CommunityFeed.css";

export default function CommunityFeed() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCommunityFeed(40)
      .then(setPosts)
      .catch(() => setPosts([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="community">
      <div className="community-header">
        <h1>🐶 자랑하기</h1>
        <p>반려인들이 다녀온 곳에서 남긴 우리 아이 자랑 모음</p>
      </div>

      {loading ? (
        <div className="community-loading">불러오는 중...</div>
      ) : posts.length === 0 ? (
        <div className="community-empty">
          <span style={{ fontSize: 40 }}>📷</span>
          <p>아직 사진이 첨부된 리뷰가 없어요.<br />첫 자랑글의 주인공이 되어보세요!</p>
        </div>
      ) : (
        <div className="brag-grid">
          {posts.map((p) => (
            <div className="brag-card fade-up" key={p.review_id}>
              <div className="brag-photo">
                <img src={mediaUrl(p.photo_url)} alt="자랑 사진"
                  onError={(e) => { e.target.parentElement.classList.add("no-img"); e.target.remove(); }} />
                <span className="brag-rating">{"⭐".repeat(p.rating)}</span>
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
