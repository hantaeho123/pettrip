import { useState } from 'react';
import './SearchBar.css';

export default function SearchBar({ onSearch, onClear }) {
  const [query, setQuery] = useState('');

  const handleInputChange = (e) => {
    const value = e.target.value;
    setQuery(value);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query);
    }
  };

  const handleClear = () => {
    setQuery('');
    onClear();
  };

  return (
    <div className="search-bar">
      <form onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="🔍 가게명 또는 지역명 검색..."
          value={query}
          onChange={handleInputChange}
          className="search-input"
        />
        {query && (
          <button type="button" className="clear-btn" onClick={handleClear}>
            ✕
          </button>
        )}
      </form>
    </div>
  );
}
