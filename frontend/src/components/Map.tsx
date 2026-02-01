import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer, Polygon, useMap, Tooltip } from "react-leaflet";
import L from "leaflet";
import type { MapProps } from "../types/Map";

const FitBounds: React.FC<{ bounds: L.LatLngBoundsExpression, setMax: boolean }> = ({ bounds, setMax }) => {
  const map = useMap();
  useEffect(() => {
    if (bounds) {
      map.fitBounds(bounds);
      if (setMax) {
        map.setMaxBounds(bounds);
      }
    }
  }, [map, bounds]);
  return null;
};

const Map: React.FC<MapProps> = ({ onTileSelect, searchResults}) => {
  const [bounds, setBounds] = useState<L.LatLngBoundsExpression | null>(null);

  useEffect(() => {
    const fetchBounds = async () => {
      const response = await fetch("http://localhost:8080/bounds");
      const result = await response.json();
      setBounds([result.min, result.max]);
    };
    if (!bounds) {
      fetchBounds();
    }
  }, []);

  const searchBounds: [[number, number], [number, number]] | null = searchResults?.bounds && searchResults.bounds.length && searchResults.tiles.length
    ? searchResults.bounds
    : null;

  if (!bounds) return <div>Loading map...</div>;

  return (
    <MapContainer
      style={{ height: "100%", flex: 1 }}
      crs={L.CRS.EPSG3857}
      scrollWheelZoom
    >
      <FitBounds bounds={bounds} setMax={true} />
      {searchBounds && <FitBounds bounds={searchBounds} setMax={false} />}

      <TileLayer
        url="http://localhost:8080/tiles?z={z}&x={x}&y={y}"
        tileSize={256}
        crossOrigin={true}
        maxZoom={30}
      />

      {(searchResults?.tiles ?? []).map((result, idx) => (
        <Polygon 
          key={idx}
          positions={result.polygon as [number, number][]}
          color="#f01d98"
          eventHandlers={{click: () => onTileSelect(result.polygon)}}>
            <Tooltip>{result.name}</Tooltip>
        </ Polygon>
      ))}
    </MapContainer>
  );
};

export default Map;