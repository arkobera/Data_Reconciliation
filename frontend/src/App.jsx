import { useState } from "react";
import { fetchResults } from "./api";
import "./App.css";

const formatMoney = (value) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(value ?? 0);

function StatCard({ label, value, accent = false }) {
  return (
    <div className={`stat-card${accent ? " accent" : ""}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ProfileCard({ profile }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <p className="eyebrow">Dataset Profile</p>
        <h3>{profile.label}</h3>
      </div>
      <div className="profile-grid">
        <StatCard label="Rows" value={profile.count} />
        <StatCard label="Total Amount" value={formatMoney(profile.total_amount)} />
        <StatCard label="Duplicate Rows" value={profile.duplicate_rows} />
        <StatCard label="Negative Rows" value={profile.negative_amount_rows} />
      </div>
      <p className="muted">
        Date range: {profile.date_range.start} to {profile.date_range.end}
      </p>
    </section>
  );
}

function RecordTable({ rows }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Status</th>
            <th>Txn</th>
            <th>Settlement</th>
            <th>Txn Amount</th>
            <th>Settlement Amount</th>
            <th>Delta</th>
            <th>Note</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={`${row.status}-${row.txn_id}-${row.settle_id}`}>
              <td>
                <span className={`pill ${row.status}`}>{row.status.replaceAll("_", " ")}</span>
              </td>
              <td>{row.txn_id ?? "N/A"}</td>
              <td>{row.settle_id ?? "N/A"}</td>
              <td>{row.platform_amount == null ? "N/A" : formatMoney(row.platform_amount)}</td>
              <td>{row.settlement_amount == null ? "N/A" : formatMoney(row.settlement_amount)}</td>
              <td>{formatMoney(row.amount_delta)}</td>
              <td>{row.explanation}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleRun = async () => {
    setLoading(true);
    setError("");

    try {
      const res = await fetchResults();
      setData(res);
    } catch (err) {
      setError(err.message || "Unable to fetch reconciliation results.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="dashboard-shell">
      <section className="hero-panel">
        <div className="hero-copy">
          <p className="eyebrow">Payments Reconciliation</p>
          <h1>Why the books do not balance at month end</h1>
          <p className="lead">
            Compare platform transactions against delayed bank settlements, surface the gaps,
            and explain each mismatch in plain language.
          </p>
        </div>
        <button className="run-button" onClick={handleRun} disabled={loading}>
          {loading ? "Running..." : "Generate data and reconcile"}
        </button>
      </section>

      {error ? <p className="error-banner">{error}</p> : null}

      {data ? (
        <>
          <section className="summary-grid">
            <StatCard
              label="Platform Total"
              value={formatMoney(data.reconciliation.totals.platform_total)}
            />
            <StatCard
              label="Bank Total"
              value={formatMoney(data.reconciliation.totals.settlement_total)}
            />
            <StatCard
              label="Net Difference"
              value={formatMoney(data.reconciliation.totals.net_difference)}
              accent
            />
            <StatCard
              label="Unmatched Records"
              value={data.reconciliation.totals.unmatched_count}
            />
          </section>

          <section className="dual-grid">
            <ProfileCard profile={data.transaction_profile} />
            <ProfileCard profile={data.settlement_profile} />
          </section>

          <section className="panel">
            <div className="panel-heading">
              <p className="eyebrow">Assumptions</p>
              <h3>How this assessment dataset is framed</h3>
            </div>
            <ul className="clean-list">
              {data.assumptions.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </section>

          <section className="panel">
            <div className="panel-heading">
              <p className="eyebrow">Key Findings</p>
              <h3>Explained anomaly buckets</h3>
            </div>
            <div className="anomaly-grid">
              {data.anomalies.map((anomaly) => (
                <article className="anomaly-card" key={anomaly.key}>
                  <div className="anomaly-topline">
                    <h4>{anomaly.title}</h4>
                    <span>{anomaly.count} record(s)</span>
                  </div>
                  <p>{anomaly.description}</p>
                  <strong>{formatMoney(anomaly.net_amount)}</strong>
                </article>
              ))}
            </div>
          </section>

          <section className="panel">
            <div className="panel-heading">
              <p className="eyebrow">Record View</p>
              <h3>Transactions that need explanation</h3>
            </div>
            <RecordTable
              rows={data.reconciliation.record_results.filter((row) => row.status !== "matched")}
            />
          </section>
        </>
      ) : (
        <section className="panel empty-state">
          <p className="eyebrow">Ready</p>
          <h3>No report loaded yet</h3>
          <p>Run the workflow to generate sample data and see the planted month-end gaps.</p>
        </section>
      )}
    </main>
  );
}

export default App;
