import { useEffect, useRef } from 'react';

// window.kakao.maps 가 로드된 뒤 호출됩니다 (index.html SDK 삽입 필요)
export default function KakaoMap({ places, onPinClick }) {
  const containerRef = useRef(null);
  const mapRef       = useRef(null);
  const markersRef   = useRef([]);

  // 지도 초기화
  useEffect(() => {
    const { kakao } = window;
    if (!kakao || !containerRef.current) return;

    kakao.maps.load(() => {
      const options = {
        center: new kakao.maps.LatLng(37.2858, 127.0110), // 수원 행궁동
        level: 5,
      };
      mapRef.current = new kakao.maps.Map(containerRef.current, options);
    });
  }, []);

  // 장소 목록이 바뀌면 마커 재렌더
  useEffect(() => {
    const { kakao } = window;
    if (!kakao || !mapRef.current) return;

    // 기존 마커 제거
    markersRef.current.forEach(m => m.setMap(null));
    markersRef.current = [];

    places.forEach(place => {
      const position = new kakao.maps.LatLng(place.latitude, place.longitude);
      const marker   = new kakao.maps.Marker({ position, map: mapRef.current });

      // 인포윈도우
      const infowindow = new kakao.maps.InfoWindow({
        content: `<div style="padding:5px 8px;font-size:13px;font-weight:500">${place.place_name}</div>`,
      });

      kakao.maps.event.addListener(marker, 'click', () => {
        infowindow.open(mapRef.current, marker);
        onPinClick && onPinClick(place);
      });

      markersRef.current.push(marker);
    });
  }, [places, onPinClick]);

  return (
    <div
      ref={containerRef}
      style={{ width: '100%', height: '100%', background: '#e8e8e8' }}
    />
  );
}
