import React from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { Home, BellRing, FileText, Network, BarChart3 } from 'lucide-react';
import './App.css';

import Dashboard from './pages/Dashboard';
import Alerts from './pages/Alerts';
import Articles from './pages/Articles';
import Clusters from './pages/Clusters';
import Analytics from './pages/Analytics';

export default function App() {
  // Helper style for active nav item in dark sidebar
  const getNavStyle = ({ isActive }) => ({
    backgroundColor: isActive ? '#1e293b' : 'transparent',
    color: isActive ? '#ffffff' : '#94a3b8',
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '12px 16px',
    textDecoration: 'none',
    borderRadius: '8px',
    fontWeight: '500',
    fontSize: '14px',
    transition: 'all 0.2s ease',
  });

  return (
    <BrowserRouter>
      <div className="app-container">
        
        {/* Dark Sidebar */}
        <aside className="sidebar">
          <div className="sidebar-header">
            <h1><Network size={24} className="text-blue-400" /> EcoTrend</h1>
          </div>
          <nav className="nav-menu">
            <NavLink to="/" style={getNavStyle}>
              <Home size={18} /> Accueil
            </NavLink>
            <NavLink to="/alerts" style={getNavStyle}>
              <BellRing size={18} /> Alertes
            </NavLink>
            <NavLink to="/articles" style={getNavStyle}>
              <FileText size={18} /> Articles
            </NavLink>
            <NavLink to="/clusters" style={getNavStyle}>
              <Network size={18} /> Clusters
            </NavLink>
            <NavLink to="/analytics" style={getNavStyle}>
              <BarChart3 size={18} /> Analytiques
            </NavLink>
          </nav>
        </aside>

        {/* Main Viewport */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/articles" element={<Articles />} />
            <Route path="/clusters" element={<Clusters />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </main>
        
      </div>
    </BrowserRouter>
  );
}