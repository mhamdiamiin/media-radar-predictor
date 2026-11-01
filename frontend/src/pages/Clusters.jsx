import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js';

export default function Clusters() {
  const [clustersData, setClustersData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/clusters')
      .then(res => {
        setClustersData(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching clusters:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="loading-state">⏳ Chargement des clusters...</div>;
  
  if (clustersData.length === 0) return <div className="empty-state">Aucun cluster trouvé.</div>;

  // Transform data for the scatter plot
  const xValues = clustersData.map(a => a.published_at);
  const yValues = clustersData.map(a => a.tendance?.score || 0);
  const textValues = clustersData.map(a => a.title ? a.title.substring(0, 40) + '...' : '');

  return (
    <div>
      <div className="page-header">
        <h2>Clusters thématiques</h2>
      </div>
      
      <div className="metric-card" style={{ marginBottom: '24px' }}>
         <h3 style={{ marginBottom: '16px' }}>Évolution des scores (Tous les clusters)</h3>
         <Plot
            data={[
              {
                x: xValues,
                y: yValues,
                text: textValues,
                mode: 'markers',
                type: 'scatter',
                marker: { 
                  color: yValues, 
                  colorscale: 'RdYlGn', 
                  size: 10 
                }
              }
            ]}
            layout={{ 
              autosize: true, 
              height: 400,
              paper_bgcolor: 'rgba(0,0,0,0)',
              plot_bgcolor: 'rgba(0,0,0,0)',
              margin: { t: 10, r: 10, l: 40, b: 40 }
            }}
            useResizeHandler={true}
            style={{ width: "100%", height: "100%" }}
          />
      </div>
    </div>
  );
}