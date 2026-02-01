import  { useState } from "react";
import Map from "./components/Map";
import "leaflet/dist/leaflet.css";
import styled from "styled-components";
import SearchDrawer from "./components/SearchDrawer";
import type { SearchResults } from "./types/Search";

function App() {
  const [searchResults, setSearchResults] = useState<SearchResults>({tiles: [], bounds: null});

  const handleSearch = async (query: string) => {
    const baseUrl = "http://localhost:8080/search";
    const url = new URL(baseUrl);

    if (query.trim() !== "") {
      url.searchParams.append("q", query);
    }

    const response = await fetch(url.toString());
    const result = await response.json();
    console.log(result)
    setSearchResults(result);
  };

  const handleTileSelect = (polygon: number[][]) => {
    const latitudes = polygon.map(item => item[0]);
    const longitudes = polygon.map(item => item[1]);

    const minLat = Math.min(...latitudes);
    const maxLat = Math.max(...latitudes);
    const minLon = Math.min(...longitudes);
    const maxLon = Math.max(...longitudes);

    setSearchResults({tiles: searchResults.tiles, bounds: [[minLat, minLon], [maxLat, maxLon]]})
  }

  return (
    <AppContainer>
      <SearchDrawer
        onSearch={handleSearch}
        onTileSelect={handleTileSelect}
        searchResults={searchResults}
      />  
      <Map
        onTileSelect={handleTileSelect}
        searchResults={searchResults} />
    </AppContainer>
  );
}

export default App;

// Styled Components for layout
const AppContainer = styled.div`
  display: flex;
  flex-direction: row;
  height: 100vh;
  width: 100vw;
`;