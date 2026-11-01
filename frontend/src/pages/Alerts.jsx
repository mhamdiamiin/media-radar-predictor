import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { CheckCircle2, Bell, ExternalLink, Calendar, Folder } from 'lucide-react';

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [filter, setFilter] = useState('all'); // 'all' | 'unseen' | 'seen'
  const [loading, setLoading] = useState(true);

  // 1. Fetch alerts from FastAPI
  const loadAlerts = () => {
    axios.get('http://127.0.0.1:8000/api/alerts')
      .then(res => {
        setAlerts(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching alerts:", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  // 2. Mark alert as seen instantaneously (Optimistic UI update)
  const handleMarkAsSeen = async (id) => {
    try {
      // Update UI immediately
      setAlerts(prev => prev.map(a => a._id === id ? { ...a, seen: true } : a));
      // Notify backend quietly
      await axios.post(`http://127.0.0.1:8000/api/alerts/${id}/seen`);
    } catch (err) {
      console.error("Failed to mark alert as seen:", err);
      loadAlerts(); // Rollback if error
    }
  };

  // 3. Filter computation
  const unseenCount = alerts.filter(a => !a.seen).length;
  const filteredAlerts = alerts.filter(a => {
    if (filter === 'unseen') return !a.seen;
    if (filter === 'seen') return a.seen;
    return true;
  });

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    try {
      const d = new Date(dateStr);
      return isNaN(d) ? String(dateStr) : d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch {
      return String(dateStr);
    }
  };

  if (loading) return <div className="loading-state">⏳ Chargement des alertes...</div>;

  return (
    <div>
      <div className="page-header">
        <h2>Alertes en cours</h2>
      </div>

      {/* Metrics Row */}
      <div className="metrics-row top-row" style={{ maxWidth: '600px' }}>
        
        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-title">Total alertes</span>
            <div className="icon-wrapper bg-blue"><Bell size={20} className="icon-blue" /></div>
          </div>
          <div className="metric-value">{alerts.length}</div>
        </div>

        <div className="metric-card highlight-card">
          <div className="metric-header">
            <span className="metric-title">Non vues</span>
            <div className="icon-wrapper bg-red"><Bell size={20} className="icon-red" /></div>
          </div>
          <div className="metric-value">{unseenCount}</div>
        </div>

      </div>

      {/* Filter Tabs */}
      <div className="filter-bar">
        <button 
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          Toutes ({alerts.length})
        </button>
        <button 
          className={`filter-btn ${filter === 'unseen' ? 'active' : ''}`}
          onClick={() => setFilter('unseen')}
        >
          Non vues ({unseenCount})
        </button>
        <button 
          className={`filter-btn ${filter === 'seen' ? 'active' : ''}`}
          onClick={() => setFilter('seen')}
        >
          Vues ({alerts.length - unseenCount})
        </button>
      </div>

      {/* Alerts List */}
      {filteredAlerts.length === 0 ? (
        <div className="empty-state">Aucune alerte à afficher.</div>
      ) : (
        <div className="alerts-list">
          {filteredAlerts.map(alert => (
            <div key={alert._id} className={`alert-card ${alert.seen ? 'is-seen' : 'is-unseen'}`}>
              
              {/* Image / Thumbnail */}
              <div className="alert-image-wrapper">
                {alert.image_url ? (
                  <img src={alert.image_url} alt="" className="alert-image" />
                ) : (
                  <div className="alert-image-placeholder">Pas d'image</div>
                )}
              </div>

              {/* Main Content */}
              <div className="alert-body">
                <a href={alert.url || '#'} target="_blank" rel="noopener noreferrer" className="alert-title">
                  {alert.title} <ExternalLink size={14} />
                </a>

                <div className="alert-meta">
                  <span><Folder size={14} /> {alert.category || 'Général'}</span>
                  <span><Calendar size={14} /> Publié: {formatDate(alert.published_at)}</span>
                  <span><Bell size={14} /> Alerté: {formatDate(alert.alerted_at)}</span>
                </div>

                <div className="badge-wrapper">
                  <span className="score-badge">Score: {alert.score ?? 0}</span>
                </div>
              </div>

              {/* Action Button */}
              <div className="alert-action">
                {alert.seen ? (
                  <span className="seen-badge">
                    <CheckCircle2 size={16} /> Vue
                  </span>
                ) : (
                  <button 
                    onClick={() => handleMarkAsSeen(alert._id)} 
                    className="btn-mark-seen"
                  >
                    Marquer vue
                  </button>
                )}
              </div>

            </div>
          ))}
        </div>
      )}
    </div>
  );
}