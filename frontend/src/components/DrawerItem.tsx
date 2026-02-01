import React from "react";
import styled from "styled-components";
import { FiFlag } from "react-icons/fi";
import type { DrawerItemProps } from "../types/Search";

const DrawerItem: React.FC<DrawerItemProps> = ({ searchResult, onTileSelect }) => {
  return (
    <Container onClick={() => onTileSelect(searchResult.polygon)}>
      <FlagCircle style={{ backgroundColor: "#f01d98" }}>
        <FiFlag size={24} color="#fff" />
      </FlagCircle>
      <TextGroup>
        <Title>{searchResult.name}</Title>
        <Subtitle>{searchResult.lat.toString() + ', ' + searchResult.lon.toString()}</Subtitle>
      </TextGroup>
    </Container>
  );
};

export default DrawerItem;

const Container = styled.div`
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  &:active {
    background-color: rgba(0, 0, 0, 0.05); // subtle “pressed” effect
  }
`;

const FlagCircle = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-shrink: 0;
  margin-right: 0.75rem;
`;

const TextGroup = styled.div`
  display: flex;
  flex-direction: column;
`;

const Title = styled.span`
  font-size: 1rem;
  font-weight: bold;
  color: #000;
`;

const Subtitle = styled.span`
  font-size: 0.85rem;
  color: #666;
`;

