import { useEffect } from "react";
import axios from "axios";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";

mapboxgl.accessToken = "YOUR_MAPBOX_TOKEN";

export default function App() {
  useEffect(() => {
    const map = new mapboxgl.Map({
      container: "map",
      style: "mapbox://styles/mapbox/streets-v11",
      center: [78.0322, 30.3165],
      zoom: 12
    });

    axios.get("http://localhost:8002/facility/public")
      .then(res => {
        res.data.forEach(f => {
          new mapboxgl.Marker()
            .setLngLat([78.0322, 30.3165])
            .setPopup(new mapboxgl.Popup().setText(f.name))
            .addTo(map);
        });
      })
      .catch(err => console.error("API Error:", err));
  }, []);

  return (
    <div
      id="map"
      style={{ width: "100vw", height: "100vh" }}
    ></div>
  );
}
