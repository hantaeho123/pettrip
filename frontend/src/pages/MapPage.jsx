/**
 * pages/MapPage.jsx
 * 지도 탐색 메인 페이지.
 * 좌측 사이드바(필터+펫프로필) / 가운데 지도 / 우측 목록·상세 패널을 조합한다.
 *
 * 핵심 흐름:
 *  - 지도 bounds나 필터가 바뀌면 장소를 다시 조회
 *  - 펫을 선택하면 그 펫 기준 맞춤 추천으로 전환 (시나리오 4)
 *  - 마커/목록 클릭 시 상세 패널 표시
 */
import { useState, useEffect, useCallback, useRef } from "react";
import KakaoMap from "../components/Map/KakaoMap";
import SearchBar from "../components/Map/SearchBar";
import FilterPanel from "../components/Sidebar/FilterPanel";
import PetProfile from "../components/Sidebar/PetProfile";
import PlaceList from "../components/Place/PlaceList";
import PlaceDetail from "../components/Place/PlaceDetail";
import { getPlaces, recommendForPet } from "../api";

export default function MapPage() {
  const [places, setPlaces] = useState([]);
  const [filters, setFilters] = useState({ category: "전체", maxWeight: null, indoorOnly: false });
  const [bounds, setBounds] = useState(null);
  const [moveTarget, setMoveTarget] = useState(null);
  const [selectedPlace, setSelectedPlace] = useState(null);
  const [selectedPet, setSelectedPet] = useState(null);
  const [keyword, setKeyword] = useState(null);
  const debounceRef = useRef(null);

  // 장소 조회 (필터/바운드 조합)
  const fetchPlaces = useCallback(() => {
    // 펫이 선택되면 맞춤 추천 모드
    if (selectedPet) {
      const cat = filters.category !== "전체" ? filters.category : undefined;
      recommendForPet(selectedPet.pet_id, cat).then(setPlaces).catch(() => setPlaces([]));
      return;
    }

    const params = { limit: 500 };
    if (filters.category && filters.category !== "전체") params.category = filters.category;
    if (filters.maxWeight) params.max_weight = filters.maxWeight;
    if (filters.indoorOnly) params.indoor_only = true;
    if (keyword) params.keyword = keyword;
    if (bounds) Object.assign(params, bounds);

    getPlaces(params).then(setPlaces).catch(() => setPlaces([]));
  }, [filters, bounds, keyword, selectedPet]);

  // 디바운스: 지도 이동/필터 변경이 잦으므로 약간 지연 후 조회
  useEffect(() => {
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(fetchPlaces, 250);
    return () => clearTimeout(debounceRef.current);
  }, [fetchPlaces]);

  return (
    <div style={{ display: "flex", height: "100%" }}>
      {/* 좌측 사이드바 */}
      <aside style={{
        width: "var(--sidebar-w)", flexShrink: 0,
        background: "var(--paper)", borderRight: "1px solid var(--line)",
        overflowY: "auto",
      }}>
        <FilterPanel filters={filters} onChange={setFilters} />
        <PetProfile selectedPet={selectedPet} onSelectPet={setSelectedPet} />
        {selectedPet && (
          <div style={{ padding: "12px 16px", fontSize: 12, color: "var(--green-700)", lineHeight: 1.5 }}>
            🎯 <b>{selectedPet.pet_name}</b>({selectedPet.pet_weight}kg) 맞춤 추천 중 ·
            평점 높은 곳 위주로 표시돼요.
          </div>
        )}
      </aside>

      {/* 가운데 지도 */}
      <div style={{ flex: 1, position: "relative" }}>
        <div style={{ position: "absolute", top: 16, left: 16, right: 16, zIndex: 10 }}>
          <SearchBar onMove={setMoveTarget} onKeywordSearch={setKeyword} />
        </div>
        <KakaoMap
          places={places}
          moveTarget={moveTarget}
          onBoundsChange={setBounds}
          onPinClick={(p) => setSelectedPlace(p)}
        />
      </div>

      {/* 우측 목록/상세 */}
      <aside style={{
        width: 340, flexShrink: 0,
        background: "var(--paper)", borderLeft: "1px solid var(--line)",
        overflow: "hidden",
      }}>
        {selectedPlace ? (
          <PlaceDetail placeId={selectedPlace.place_id} onBack={() => setSelectedPlace(null)} />
        ) : (
          <PlaceList
            places={places}
            selectedId={selectedPlace?.place_id}
            onSelect={(p) => setSelectedPlace(p)}
            title={selectedPet ? `${selectedPet.pet_name} 추천 장소` : "검색 결과"}
          />
        )}
      </aside>
    </div>
  );
}
