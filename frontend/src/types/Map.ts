import type { SearchResults } from "./Search";

export interface MapProps {
  searchResults: SearchResults;
  onTileSelect: (polygon: number[][]) => void;
};