import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js';

export default function Analytics() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // We need all articles for analytics
    axios.get('http://127.0.0.1:8000/api/articles?limit=0')
      .then(res => {
        setArticles(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching for analytics:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="loading-state">⏳ Calcul des analytiques...</div>;

  // 1. Calculate Score by Category
  const catScores = {};
  const catCounts = {};
  articles.forEach(a => {
      const cat = a.category_normalized || 'autre';
      const score = a.tendance?.score || 0;
      if (score > 0) {
          catScores[cat] = (catScores[cat] || 0) + score;
          catCounts[cat] = (catCounts[cat] || 0) + 1;
      }
  });
  
  const avgScores = Object.keys(catScores).map(cat => ({
      cat, 
      avg: catScores[cat] / catCounts[cat]
  })).sort((a, b) => a.avg - b.avg);

  return (
    <div>
      <div className="page-header">
        <h2>Analytiques</h2>
      </div>

      <div className="metrics-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
        
        {/* Chart 1: Average Score */}
        <div className="metric-card">
          <h3 style={{ fontSize: '16px', marginBottom: '16px' }}>Score moyen par catégorie</h3>
          <Plot
            data={[{
              x: avgScores.map(d => d.avg),
              y: avgScores.map(d => d.cat),
              type: 'bar',
              orientation: 'h',
              marker: {
                color: avgScores.map(d => d.avg),
                colorscale: 'RdYlGn'
              }
            }]}
            layout={{ 
              autosize: true, 
              height: 350,
              margin: { t: 10, r: 10, l: 80, b: 40 }
            }}
            useResizeHandler={true}
            style={{ width: "100%", height: "100%" }}
          />
        </div>

      </div>
    </div>
  );
}