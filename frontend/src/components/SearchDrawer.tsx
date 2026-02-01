import  React, { useState } from "react";
import styled from "styled-components";
import { FaSearch } from "react-icons/fa";
import type { SearchDrawerProps, SearchResult } from "../types/Search";
import DrawerItem from "./DrawerItem";

const SearchDrawer: React.FC<SearchDrawerProps> = ({ onSearch, onTileSelect, searchResults }) => {
  const [query, setQuery] = useState("");
    
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") onSearch(query);
  };

  return (
    <DrawerWrapper>
      <Drawer>
        <SearchWrapper>
            <SearchInput 
                placeholder="Search..."
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}/>
            <SearchButton onClick={() => onSearch(query)}>
                <FaSearch />
            </SearchButton>
        </SearchWrapper>
        <DrawerContent>
          <p>Results</p>
          <div>
            {(searchResults?.tiles ?? []).map((item: SearchResult, index: number) => (
              <DrawerItem
                key={index}
                searchResult={item}
                onTileSelect={onTileSelect}
              />
            ))}
          </div>
        </DrawerContent>
      </Drawer>
    </DrawerWrapper>
  );
};

export default SearchDrawer;

const DrawerWrapper = styled.div`
  width: 500px; // always open
  height: 100%;
  background: white;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
`;

const Drawer = styled.div`
  width: 500px;
  height: 100%;
  transition: transform 0.3s ease;
  display: flex;
  flex-direction: column;
`;

const SearchWrapper = styled.div`
  display: flex;
  align-items: center;
  border: 2px solid black;
  border-radius: 999px;
  margin: 20px;
  padding: 6px 10px;
  width: 430px;
`;

const SearchButton = styled.button`
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  font-size: 20px;
  justify-content: center;
  cursor: pointer;
  color: black;
  font-size: 10px;
  &:hover {
    opacity: 0.85;
  }
`;

const SearchInput = styled.input`
  border: none;
  outline: none;
  flex: 1;
  font-size: 16px;
  padding: 8px;
  background: transparent;
`;

const DrawerContent = styled.div`
  padding: 1rem;
  flex: 80;
  overflow-y: auto;
`;

