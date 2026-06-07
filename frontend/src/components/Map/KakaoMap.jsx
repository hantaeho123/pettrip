/**
 * components/Map/KakaoMap.jsx
 * 카카오맵 렌더링 + 마커 표시 핵심 컴포넌트
 *
 * 보고서 시나리오 1 반영:
 *  - 처음엔 남한 전체가 보이도록 초기 중심/레벨 설정
 *  - 지도 이동/줌 시 현재 화면 좌표 범위(bounds)를 부모로 전달 → 해당 영역 장소만 로드
 *  - 마커 클릭 시 장소명 라벨(오버레이)이 토글됨 (다시 누르면 사라짐, 여러 개 고정 가능)
 *  - 검색 시 해당 위치로 부드럽게 이동 + 확대 (부모에서 moveTo로 제어)
 */
import { useEffect, useRef, useCallback } from "react";

// 카테고리별 마커 색상
const CAT_COLOR = {
  카페: "#d9663f", 식당: "#1d7a5f", 숙소: "#7b6cd0",
  공원: "#5a9e2f", 관광지: "#e8a33d", 문화시설: "#e8a33d",
  쇼핑: "#6e6f66", 기타: "#6e6f66",
};

export default function KakaoMap({ places, onPinClick, onBoundsChange, moveTarget }) {
  const containerRef = useRef(null);
  const mapRef       = useRef(null);
  const markersRef   = useRef([]);
  const overlaysRef  = useRef({});   // place_id → 라벨 오버레이 (토글 상태 보관)

  // ── 지도 초기화 ──────────────────────────────────────
  useEffect(() => {
    const { kakao } = window;
    if (!kakao || !containerRef.current) return;

    kakao.maps.load(() => {
      const map = new kakao.maps.Map(containerRef.current, {
        center: new kakao.maps.LatLng(36.5, 127.8), // 남한 중앙
        level: 13,                                   // 전국이 보이는 줌 레벨
      });
      mapRef.current = map;

      // 지도 이동/줌이 멈추면 현재 화면 범위를 부모에게 전달
      const emitBounds = () => {
        const b = map.getBounds();
        const sw = b.getSouthWest();
        const ne = b.getNorthEast();
        onBoundsChange &&
          onBoundsChange({
            min_lat: sw.getLat(), max_lat: ne.getLat(),
            min_lng: sw.getLng(), max_lng: ne.getLng(),
          });
      };
      kakao.maps.event.addListener(map, "idle", emitBounds);
      emitBounds();
    });
  }, [onBoundsChange]);

  // ── 검색 등으로 특정 위치로 이동 ─────────────────────
  useEffect(() => {
    const { kakao } = window;
    if (!kakao || !mapRef.current || !moveTarget) return;
    const pos = new kakao.maps.LatLng(moveTarget.lat, moveTarget.lng);
    mapRef.current.setLevel(moveTarget.level || 5);
    mapRef.current.panTo(pos);
  }, [moveTarget]);

  // ── 마커 라벨 토글 ───────────────────────────────────
  const toggleLabel = useCallback((place, position) => {
    const { kakao } = window;
    const id = place.place_id;

    if (overlaysRef.current[id]) {
      // 이미 떠 있으면 제거 (토글 OFF)
      overlaysRef.current[id].setMap(null);
      delete overlaysRef.current[id];
      return;
    }
    // 라벨 생성 (토글 ON)
    const color = CAT_COLOR[place.category] || CAT_COLOR.기타;
    const content = document.createElement("div");
    content.innerHTML = `
      <div style="
        background:${color}; color:#fff; padding:5px 10px;
        border-radius:14px; font-size:12px; font-weight:600;
        white-space:nowrap; box-shadow:0 2px 8px rgba(0,0,0,0.22);
        transform:translateY(-46px); cursor:pointer;
      ">${place.place_name}</div>`;
    const overlay = new kakao.maps.CustomOverlay({
      position, content, yAnchor: 0, zIndex: 5,
    });
    overlay.setMap(mapRef.current);
    overlaysRef.current[id] = overlay;
  }, []);

  // ── 장소 목록이 바뀌면 마커 다시 그리기 ──────────────
  useEffect(() => {
    const { kakao } = window;
    if (!kakao || !mapRef.current) return;

    // 기존 마커 제거
    markersRef.current.forEach((m) => m.setMap(null));
    markersRef.current = [];

    places.forEach((place) => {
      if (!place.latitude || !place.longitude) return;
      const position = new kakao.maps.LatLng(place.latitude, place.longitude);
      const color = CAT_COLOR[place.category] || CAT_COLOR.기타;

      // 색상 있는 원형 마커 (CustomOverlay로 구현)
      const pinEl = document.createElement("div");
      pinEl.innerHTML = `
        <div style="
          width:18px;height:18px;border-radius:50% 50% 50% 0;
          background:${color};transform:rotate(-45deg);
          border:2.5px solid #fff;box-shadow:0 2px 5px rgba(0,0,0,0.25);
          cursor:pointer;
        "></div>`;
      pinEl.onclick = () => {
        toggleLabel(place, position);
        onPinClick && onPinClick(place);
      };

      const marker = new kakao.maps.CustomOverlay({
        position, content: pinEl, yAnchor: 1, zIndex: 3,
      });
      marker.setMap(mapRef.current);
      markersRef.current.push(marker);
    });
  }, [places, onPinClick, toggleLabel]);

  return <div ref={containerRef} style={{ width: "100%", height: "100%" }} />;
}
