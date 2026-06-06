import { useState, useEffect } from 'react';
import { getPlaces, searchPlaces } from '../../api';
import KakaoMap from '../Map/KakaoMap';
import PlaceList from '../Place/PlaceList';
import PlaceDetail from '../Place/PlaceDetail';
import SearchBar from '../Sidebar/SearchBar';
import './MapPage.css';

export default function MapPage({ filters }) {
  const [places, setPlaces] = useState([]);
  const [selected, setSelected] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadPlaces();
  }, [filters, searchQuery]);

  const loadPlaces = () => {
    const params = {};
    if (filters.category !== '전체') params.category = filters.category;

    const request = searchQuery
      ? searchPlaces(searchQuery, params)
      : getPlaces(params);

    request
      .then(setPlaces)
      .catch(() => setPlaces([]));
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
  };

  const handleClearSearch = () => {
    setSearchQuery('');
  };

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
          <>
            <SearchBar onSearch={handleSearch} onClear={handleClearSearch} />
            {searchQuery && (
              <div className="search-info">
                <span>검색 결과: <strong>{searchQuery}</strong> ({places.length}개)</span>
              </div>
            )}
            <PlaceList
              places={places}
              selectedId={selected?.place_id}
              onSelect={setSelected}
            />
          </>
        )}
      </div>
    </div>
  );
}
