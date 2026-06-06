import { useState, useEffect } from 'react';
import { getPlaces } from '../api';
import KakaoMap from '../components/Map/KakaoMap';
import PlaceList from '../components/Place/PlaceList';
import PlaceDetail from '../components/Place/PlaceDetail';
import './MapPage.css';

export default function MapPage({ filters }) {
  const [places, setPlaces] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    const params = {};
    if (filters.category !== '전체') params.category = filters.category;
    getPlaces(params)
      .then(setPlaces)
      .catch(() => setPlaces([]));
  }, [filters]);

  return (
    <div className="map-page">
      {/* 지도 영역 */}
      <div className="map-area">
        <KakaoMap places={places} onPinClick={setSelected} />
      </div>

      {/* 우측 패널 */}
      <div className="place-panel">
        {selected ? (
          <PlaceDetail place={selected} onBack={() => setSelected(null)} />
        ) : (
          <PlaceList
            places={places}
            selectedId={selected?.place_id}
            onSelect={setSelected}
          />
        )}
      </div>
    </div>
  );
}
