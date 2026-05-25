import { useState } from "react";

function SearchBar({ onSearchResult }) {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (event) => {
    event.preventDefault();

    if (!query.trim()) {
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`,
        {
          headers: {
            Accept: "application/json",
          },
        },
      );

      if (!response.ok) {
        throw new Error("Search request failed.");
      }

      const result = await response.json();

      if (!result.length) {
        setError("No matching location found.");
        return;
      }

      const location = result[0];
      onSearchResult({
        name: location.display_name,
        lat: Number(location.lat),
        lon: Number(location.lon),
      });
    } catch {
      setError("Unable to search location right now.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="section-block">
      <h2>🔍 Search Location</h2>
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={query}
          placeholder="Search for a location..."
          onChange={(event) => setQuery(event.target.value)}
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Searching..." : "Search"}
        </button>
      </form>
      {error ? <p className="error-text">{error}</p> : null}
    </section>
  );
}

export default SearchBar;
