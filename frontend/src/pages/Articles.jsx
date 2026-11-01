import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ExternalLink, Search } from 'lucide-react';

export default function Articles() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Filters
  const [search, setSearch] = useState('');
  const [catFilter, setCatFilter] = useState('Toutes');
  const [labelFilter, setLabelFilter] = useState('Tous');

  useEffect(() => {
    // Fetching up to 200 articles for the explorer
    axios.get('http://127.0.0.1:8000/api/articles?limit=200')
      .then(res => {
        setArticles(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching articles:", err);
        setLoading(false);
      });
  }, []);

  // Apply filters client-side
  const filtered = articles.filter(a => {
    const matchSearch = search ? (a.title || '').toLowerCase().includes(search.toLowerCase()) : true;
    const matchCat = catFilter === 'Toutes' ? true : a.category_normalized === catFilter;
    const matchLabel = labelFilter === 'Tous' ? true : (a.tendance?.label === labelFilter);
    return matchSearch && matchCat && matchLabel;
  });

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    try {
      return new Date(dateStr).toLocaleDateString('fr-FR');
    } catch {
      return dateStr;
    }
  };

  const getLabelColor = (label) => {
    if (label === 'trend') return '#16a34a'; // green
    if (label === 'fiddling') return '#d97706'; // orange
    return '#6b7280'; // gray
  };

  if (loading) return <div className="loading-state">⏳ Chargement des articles...</div>;

  return (
    <div>
      <div className="page-header">
        <h2>Explorateur d'articles</h2>
      </div>

      {/* Filter Controls */}
      <div className="filters-container">
        <div className="search-box">
          <Search size={18} className="search-icon" />
          <input 
            type="text" 
            placeholder="🔍 Rechercher par titre..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <select value={catFilter} onChange={(e) => setCatFilter(e.target.value)} className="filter-select">
          <option value="Toutes">Toutes catégories</option>
          <option value="sport">Sport</option>
          <option value="politique">Politique</option>
          <option value="international">International</option>
          <option value="economie">Économie</option>
          <option value="culture">Culture</option>
          <option value="tech">Tech</option>
        </select>

        <select value={labelFilter} onChange={(e) => setLabelFilter(e.target.value)} className="filter-select">
          <option value="Tous">Tous labels</option>
          <option value="trend">Trend</option>
          <option value="fiddling">Fiddling</option>
          <option value="mimic">Mimic</option>
        </select>
      </div>

      {/* Articles Table/List */}
      <div className="articles-table">
        <div className="table-header">
          <div className="col-main">Article</div>
          <div className="col-badge">Label</div>
          <div className="col-badge">Score</div>
          <div className="col-badge">Sentiment</div>
        </div>
        
        <div className="table-body">
          {filtered.slice(0, 50).map(a => (
            <div key={a._id} className="table-row">
              <div className="col-main">
                <a href={a.url || '#'} target="_blank" rel="noopener noreferrer" className="article-link">
                  {a.title} <ExternalLink size={12} />
                </a>
                <div className="article-meta">
                  📂 {a.category_normalized || 'N/A'} • 📅 {formatDate(a.published_at)}
                </div>
              </div>
              
              <div className="col-badge">
                {a.tendance?.label && (
                  <span className="badge" style={{ backgroundColor: getLabelColor(a.tendance.label), color: 'white' }}>
                    {a.tendance.label}
                  </span>
                )}
              </div>
              
              <div className="col-badge">
                <span className="badge score-badge">
                  {a.tendance?.score ? a.tendance.score.toFixed(2) : '0.00'}
                </span>
              </div>
              
              <div className="col-badge">
                {a.nlp?.sentiment?.label && (
                  <span className={`badge sentiment-${a.nlp.sentiment.label}`}>
                    {a.nlp.sentiment.label}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}