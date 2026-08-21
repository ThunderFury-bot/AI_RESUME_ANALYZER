export default function ResultsView({ results }) {
  if (!results) return null;

  return (
    <div className="results">
      <h2>Analysis Results</h2>

      <div className="score-block">
        <span className="score-number">{results.overall_score}</span>
        <span className="score-label">/ 100 Overall Score</span>
      </div>

      <Section title="ATS Compatibility">
        <p>{results.ats_compatibility}</p>
      </Section>

      <Section title="Missing Skills / Keywords">
        <List items={results.missing_skills} empty="None identified." />
      </Section>

      <Section title="Strengths">
        <List items={results.strengths} empty="None identified." />
      </Section>

      <Section title="Weaknesses">
        <List items={results.weaknesses} empty="None identified." />
      </Section>

      <Section title="Suggestions for Improvement">
        <List items={results.suggestions} empty="None provided." />
      </Section>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div className="section">
      <h3>{title}</h3>
      {children}
    </div>
  );
}

function List({ items, empty }) {
  if (!items || items.length === 0) return <p className="muted">{empty}</p>;
  return (
    <ul>
      {items.map((item, i) => (
        <li key={i}>{item}</li>
      ))}
    </ul>
  );
}