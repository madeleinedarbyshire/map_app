export type SearchResult = {
  name: string;
  lat: number;
  lon: number;
  score: number;
  polygon: number[][]
};

export type SearchResults = {
  tiles: SearchResult[];
  bounds: [[number, number], [number, number]] | null;
}

export interface SearchDrawerProps {
  onSearch: (query: string) => void;
  onTileSelect: (polygon: number[][]) => void;
  searchResults: SearchResults;
};

export interface DrawerItemProps {
  searchResult: SearchResult;
  onTileSelect: (polygon: number[][]) => void;
};
