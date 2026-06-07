/**
 * components/Map/SearchBar.jsx
 * 지역/장소명 검색창.
 * 카카오 services 라이브러리로 주소·키워드를 좌표로 변환하여
 * 지도를 해당 위치로 이동시킨다 (시나리오 1의 검색 이동/확대).
 */
import { useState } from "react";
import "./SearchBar.css";

export default function SearchBar({ onMove, onKeywordSearch }) {
  const [query, setQuery] = useState("");

  const handleSearch = () => {
    if (!query.trim()) return;
    const { kakao } = window;
    if (!kakao || !kakao.maps.services) {
      // 서비스 라이브러리가 없으면 키워드 필터링으로 대체
      onKeywordSearch && onKeywordSearch(query);
      return;
    }

    // 1) 장소(키워드) 검색 우선
    const ps = new kakao.maps.services.Places();
    ps.keywordSearch(query, (data, status) => {
      if (status === kakao.maps.services.Status.OK && data.length) {
        onMove({ lat: parseFloat(data[0].y), lng: parseFloat(data[0].x), level: 4 });
      } else {
        // 2) 실패하면 주소 검색
        const geocoder = new kakao.maps.services.Geocoder();
        geocoder.addressSearch(query, (res, st) => {
          if (st === kakao.maps.services.Status.OK && res.length) {
            onMove({ lat: parseFloat(res[0].y), lng: parseFloat(res[0].x), level: 4 });
          } else {
            // 3) 둘 다 실패 → DB 키워드 필터링
            onKeywordSearch && onKeywordSearch(query);
          }
        });
      }
    });
  };

  return (
    <div className="searchbar">
      <span className="searchbar-icon" aria-hidden>🔍</span>
      <input
        type="text"
        value={query}
        placeholder="지역이나 장소를 검색하세요 (예: 수원 행궁동)"
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSearch()}
      />
      <button className="searchbar-btn" onClick={handleSearch}>검색</button>
    </div>
  );
}
