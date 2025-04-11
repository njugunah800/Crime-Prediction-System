import React, { useState } from "react";
import axios from "axios";

function App() {
  const [location, setLocation] = useState("");
  const [crimeType, setCrimeType] = useState("All");
  const [prediction, setPrediction] = useState("");

  const handlePredict = async () => {
    try {
      const response = await axios.post("http://127.0.0.1:5000/predict", {
        location,
        crime_type: crimeType,
      });

      setPrediction(`Predicted Crime Risk: ${response.data.risk_level}`);
    } catch (error) {
      setPrediction("Error: " + error.response.data.error);
    }
  };

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <h2>Crime Rate Prediction</h2>
      <input
        type="text"
        placeholder="Enter Location"
        value={location}
        onChange={(e) => setLocation(e.target.value)}
      />
      <select value={crimeType} onChange={(e) => setCrimeType(e.target.value)}>
        <option value="All">All Crimes</option>
        <option value="Murder">Murder</option>
        <option value="Kidnapping">Kidnapping</option>
        <option value="Sexual_Crimes">Sexual Crimes</option>
        <option value="Assault">Assault</option>
        <option value="Theft">Theft</option>
        <option value="Cyber_Crimes">Cyber Crimes</option>
      </select>
      <button onClick={handlePredict}>Predict</button>
      <h3>{prediction}</h3>
    </div>
  );
}

export default App;
