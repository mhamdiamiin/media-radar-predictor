import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, Flame, Clock, Copy, BellRing } from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/stats')
      .then(response => {
        setStats(response.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching stats:", err);
        setError("Erreur de connexion à l'API.");
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="loading-state">⏳ Chargement des données...</div>;
  if (error) return <div className="error-state">❌ {error}</div>;

  return (
    <div>
      <div className="page-header">
        <h2>Tableau de bord</h2>
      </div>

      {/* Top Row: Primary Metrics */}
      <div className="metrics-row top-row">
        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-title">Total articles</span>
            <div className="icon-wrapper bg-blue"><Activity size={20} className="icon-blue" /></div>
          </div>
          <div className="metric-value">{stats.total}</div>
        </div>

        <div className="metric-card highlight-card">
          <div className="metric-header">
            <span className="metric-title">Alertes d'action</span>
            <div className="icon-wrapper bg-red"><BellRing size={20} className="icon-red" /></div>
          </div>
          <div className="metric-value">{stats.alerts}</div>
          <div className="metric-subtext">{stats.unseen} non vues nécessitent votre attention</div>
        </div>
      </div>

      {/* Bottom Row: Category Breakdown */}
      <h3 className="section-title">Répartition des détections</h3>
      <div className="metrics-row bottom-row">
        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-title">Tendances</span>
            <div className="icon-wrapper bg-green"><Flame size={20} className="icon-green" /></div>
          </div>
          <div className="metric-value">{stats.trend}</div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-title">Éphémères</span>
            <div className="icon-wrapper bg-orange"><Clock size={20} className="icon-orange" /></div>
          </div>
          <div className="metric-value">{stats.fiddling}</div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-title">Mimiques</span>
            <div className="icon-wrapper bg-gray"><Copy size={20} className="icon-gray" /></div>
          </div>
          <div className="metric-value">{stats.mimic}</div>
        </div>
      </div>
    </div>
  );
}