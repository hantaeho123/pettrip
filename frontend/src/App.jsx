/**
 * App.jsx
 * 최상위 컴포넌트. 상단 네비게이션 + 탭별 페이지 전환 + 로그인 모달.
 *
 * 탭: 지도 탐색 / 멍트립 다이어리 / 자랑하기 / 견종 랭킹
 * 우상단: 로그인 상태에 따라 로그인 버튼 또는 유저 메뉴(로그아웃·탈퇴)
 */
import { useState } from "react";
import { useAuth } from "./context/AuthContext";
import MapPage from "./pages/MapPage";
import CommunityFeed from "./components/Community/CommunityFeed";
import RankingBoard from "./components/Community/RankingBoard";
import DiaryView from "./components/Community/DiaryView";
import AuthModal from "./components/Auth/AuthModal";
import { deleteAccount } from "./api";
import "./App.css";

const TABS = [
  { id: "map",   label: "지도 탐색", icon: "🗺️" },
  { id: "diary", label: "멍트립 다이어리", icon: "🐾" },
  { id: "brag",  label: "자랑하기", icon: "🐶" },
  { id: "rank",  label: "견종 랭킹", icon: "🏆" },
];

export default function App() {
  const { user, logoutUser } = useAuth();
  const [tab, setTab] = useState("map");
  const [showAuth, setShowAuth] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  const handleDeleteAccount = async () => {
    if (!window.confirm("정말 탈퇴하시겠어요? 작성한 리뷰가 모두 삭제됩니다.")) return;
    await deleteAccount(user.user_id);
    logoutUser();
    setShowMenu(false);
    alert("탈퇴가 완료되었습니다.");
  };

  return (
    <div className="app">
      {/* ── 상단 네비게이션 ── */}
      <header className="topbar">
        <div className="brand" onClick={() => setTab("map")}>
          <span className="brand-logo">🐾</span>
          <span className="brand-name">PetTrip</span>
        </div>

        <nav className="nav-tabs">
          {TABS.map((t) => (
            <button key={t.id}
              className={`nav-tab ${tab === t.id ? "active" : ""}`}
              onClick={() => setTab(t.id)}>
              <span className="nav-icon">{t.icon}</span>{t.label}
            </button>
          ))}
        </nav>

        <div className="auth-area">
          {user ? (
            <div className="user-menu-wrap">
              <button className="user-chip" onClick={() => setShowMenu(!showMenu)}>
                <span className="user-ava">🧑</span>
                {user.nickname}
              </button>
              {showMenu && (
                <div className="user-dropdown fade-in">
                  <span className="dropdown-email">{user.email}</span>
                  <button onClick={() => { logoutUser(); setShowMenu(false); }}>로그아웃</button>
                  <button className="danger" onClick={handleDeleteAccount}>회원 탈퇴</button>
                </div>
              )}
            </div>
          ) : (
            <button className="login-btn" onClick={() => setShowAuth(true)}>로그인 / 가입</button>
          )}
        </div>
      </header>

      {/* ── 본문 ── */}
      <main className="content">
        {tab === "map"   && <MapPage />}
        {tab === "diary" && <DiaryView />}
        {tab === "brag"  && <CommunityFeed />}
        {tab === "rank"  && <RankingBoard />}
      </main>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </div>
  );
}
