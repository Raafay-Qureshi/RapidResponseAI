import React from 'react';
import './PopulationImpact.css';

function PopulationImpact({ populationImpact, affectedAreas }) {
  if (!populationImpact) {
    return (
      <section className="plan-section">
        <h3>👥 Population Impact</h3>
        <p className="no-data">Population impact data not available</p>
      </section>
    );
  }

  const {
    total_affected = 0,
    vulnerable_population = {},
    languages = {},
    critical_facilities = [],
    affected_neighborhoods = [],
  } = populationImpact;

  const {
    elderly = 0,
    children = 0,
    disabled = 0,
  } = vulnerable_population;

  const totalLangSpeakers = Object.values(languages).reduce((sum, count) => sum + count, 0);
  const languageData = Object.entries(languages)
    .map(([lang, count]) => ({
      language: lang,
      count,
      percentage: totalLangSpeakers > 0 ? ((count / totalLangSpeakers) * 100).toFixed(1) : 0,
    }))
    .sort((a, b) => b.count - a.count);

  const totalVulnerable = elderly + children + disabled;
  const vulnerablePercentage =
    total_affected > 0 ? ((totalVulnerable / total_affected) * 100).toFixed(1) : 0;

  const formattedArea =
    typeof affectedAreas?.affected_area_km2 === 'number'
      ? `${affectedAreas.affected_area_km2.toFixed(2)} km²`
      : 'N/A';

  const facilityIcons = {
    elementary_school: '🏫',
    high_school: '🎓',
    hospital: '🏥',
    senior_center: '👴',
    daycare: '👶',
    care_home: '🏥',
  };

  return (
    <section className="plan-section population-section">
      <h3>👥 Population Impact & Affected Areas</h3>

      <div className="impact-summary">
        <div className="total-affected-card">
          <div className="total-icon">🏘️</div>
          <div className="total-content">
            <span className="total-value">{total_affected.toLocaleString()}</span>
            <span className="total-label">Total People Affected</span>
          </div>
        </div>

        <div className="affected-area-card">
          <div className="area-icon">📍</div>
          <div className="area-content">
            <span className="area-value">{formattedArea}</span>
            <span className="area-label">Affected Area</span>
          </div>
        </div>

        <div className="vulnerable-card">
          <div className="vulnerable-icon">⚠️</div>
          <div className="vulnerable-content">
            <span className="vulnerable-value">{totalVulnerable.toLocaleString()}</span>
            <span className="vulnerable-label">Vulnerable Residents</span>
            <span className="vulnerable-percentage">{vulnerablePercentage}% of total</span>
          </div>
        </div>
      </div>

      <div className="vulnerable-breakdown">
        <h4 className="subsection-title">🆘 Priority Populations</h4>
        <p className="subsection-description">
          These groups require priority evacuation assistance and specialized care
        </p>

        <div className="vulnerable-grid">
          <div className="vulnerable-item elderly">
            <div className="vulnerable-item-header">
              <span className="vulnerable-item-icon">👴</span>
              <span className="vulnerable-item-count">{elderly.toLocaleString()}</span>
            </div>
            <div className="vulnerable-item-content">
              <h5 className="vulnerable-item-title">Elderly (65+)</h5>
              <p className="vulnerable-item-note">
                May require mobility assistance and medical support
              </p>
            </div>
          </div>

          <div className="vulnerable-item children">
            <div className="vulnerable-item-header">
              <span className="vulnerable-item-icon">👶</span>
              <span className="vulnerable-item-count">{children.toLocaleString()}</span>
            </div>
            <div className="vulnerable-item-content">
              <h5 className="vulnerable-item-title">Children (Under 18)</h5>
              <p className="vulnerable-item-note">
                Priority for family reunification and shelter
              </p>
            </div>
          </div>

          <div className="vulnerable-item disabled">
            <div className="vulnerable-item-header">
              <span className="vulnerable-item-icon">♿</span>
              <span className="vulnerable-item-count">{disabled.toLocaleString()}</span>
            </div>
            <div className="vulnerable-item-content">
              <h5 className="vulnerable-item-title">People with Disabilities</h5>
              <p className="vulnerable-item-note">
                Require accessible transportation and accommodations
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="language-demographics">
        <h4 className="subsection-title">🌐 Language Demographics</h4>
        <p className="subsection-description">
          Communication strategy must address multiple language groups
        </p>

        {languageData.length > 0 ? (
          <div className="language-bars">
            {languageData.map((lang) => (
              <div key={lang.language} className="language-bar-item">
                <div className="language-bar-header">
                  <span className="language-bar-name">{lang.language}</span>
                  <span className="language-bar-stats">
                    {lang.count.toLocaleString()} ({lang.percentage}%)
                  </span>
                </div>
                <div className="language-bar-track">
                  <div className="language-bar-fill" style={{ width: `${lang.percentage}%` }} />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="no-data">Language demographics not available</p>
        )}
      </div>

      {critical_facilities.length > 0 && (
        <div className="critical-facilities">
          <h4 className="subsection-title">🏫 Critical Facilities at Risk</h4>
          <p className="subsection-description">
            Priority protection and evacuation coordination required
          </p>

          <div className="facilities-grid">
            {critical_facilities.map((facility, idx) => {
              const icon = facilityIcons[facility.type] || '🏢';
              const lat = facility.location?.lat;
              const lon = facility.location?.lon;
              const coords =
                typeof lat === 'number' && typeof lon === 'number'
                  ? `${lat.toFixed(4)}, ${lon.toFixed(4)}`
                  : 'N/A';
              const hasPopulation = typeof facility.population === 'number';

              return (
                <div key={`${facility.name}-${idx}`} className="facility-card">
                  <div className="facility-icon">{icon}</div>
                  <div className="facility-content">
                    <h5 className="facility-name">{facility.name}</h5>
                    {facility.type && (
                      <p className="facility-type">{facility.type.replace(/_/g, ' ').toUpperCase()}</p>
                    )}
                    {hasPopulation && (
                      <p className="facility-population">
                        <strong>{facility.population.toLocaleString()}</strong> people
                      </p>
                    )}
                    <p className="facility-coords">📍 {coords}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {affected_neighborhoods.length > 0 && (
        <div className="affected-neighborhoods">
          <h4 className="subsection-title">🏘️ Affected Neighborhoods</h4>
          <div className="neighborhoods-list">
            {affected_neighborhoods.map((neighborhood, idx) => (
              <span key={`${neighborhood}-${idx}`} className="neighborhood-badge">
                {neighborhood}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="response-priorities">
        <h4 className="priorities-title">🎯 Response Priorities</h4>
        <ul className="priorities-list">
          <li className="priority-item">
            <span className="priority-number">1</span>
            <span className="priority-text">
              Immediate evacuation assistance for {totalVulnerable.toLocaleString()} vulnerable residents
            </span>
          </li>
          <li className="priority-item">
            <span className="priority-number">2</span>
            <span className="priority-text">
              Coordinate evacuation of {critical_facilities.length} critical facilities
            </span>
          </li>
          <li className="priority-item">
            <span className="priority-number">3</span>
            <span className="priority-text">
              Multi-language emergency alerts to {total_affected.toLocaleString()} residents
            </span>
          </li>
          <li className="priority-item">
            <span className="priority-number">4</span>
            <span className="priority-text">Establish accessible shelters with medical support</span>
          </li>
        </ul>
      </div>
    </section>
  );
}

export default PopulationImpact;
