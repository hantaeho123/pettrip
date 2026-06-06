import { useState } from 'react';
import MapPage       from './pages/MapPage';
import CommunityPage from './pages/CommunityPage';
import RankingPage   from './pages/RankingPage';
import FilterPanel   from './components/Sidebar/FilterPanel';
import PetProfile    from './components/Sidebar/PetProfile';
import './App.css';

export default function App() {
  const [tab,      setTab]      = useState('map');   // 'map' | 'community' | 'ranking'
  const [filters,  setFilters]  = useState({ category: '전체', size: '전체' });

  const navItems = [
    { id: 'map',       label: '지도 탐색',      icon: '🗺️' },
    { id: 'community', label: '자랑 게시판',    icon: '🐾' },
    { id: 'ranking',   label: '견종별 랭킹',    icon: '🏆' },
  ];

  return (
    <div className="app-layout">
      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="logo">
          <span className="logo-icon">📍</span>
          <div>
            <div className="logo-text">PetTrip</div>
            <div className="logo-sub">반려동물 여행 플랫폼</div>
          </div>
        </div>

        <nav className="nav">
          {navItems.map(n => (
            <div
              key={n.id}
              className={`nav-item ${tab === n.id ? 'active' : ''}`}
              onClick={() => setTab(n.id)}
            >
              <span>{n.icon}</span> {n.label}
            </div>
          ))}
        </nav>

        <PetProfile />

        {tab === 'map' && (
          <FilterPanel filters={filters} onChange={setFilters} />
        )}
      </aside>

      {/* ── Main content ── */}
      <main className="main-content">
        {tab === 'map'       && <MapPage filters={filters} />}
        {tab === 'community' && <CommunityPage />}
        {tab === 'ranking'   && <RankingPage />}
      </main>
    </div>
  );
}
