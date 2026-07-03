import { useEffect, useState } from "react";
import { listMonitors, addMonitor, deleteMonitor } from "./api";

const POLL_INTERVAL_MS = 10000;

function timeAgo(iso) {
  if (!iso) return "-";
  const seconds = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (seconds < 5) return "just now";
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

function StatusBadge({ check }) {
  if (!check) return <span className="badge pending">Pending</span>;
  return check.is_up ? (
    <span className="badge up">Up</span>
  ) : (
    <span className="badge down">Down</span>
  );
}

export default function App() {
  const [monitors, setMonitors] = useState([]);
  const [url, setUrl] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  async function load() {
    try {
      setMonitors(await listMonitors());
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    load();
    const timer = setInterval(load, POLL_INTERVAL_MS);
    return () => clearInterval(timer);
  }, []);

  async function handleAdd(event) {
    event.preventDefault();
    setError("");
    try {
      await addMonitor(url.trim(), name.trim());
      setUrl("");
      setName("");
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(id) {
    try {
      await deleteMonitor(id);
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="container">
      <h1>Uptime Monitor</h1>

      <form className="add-form" onSubmit={handleAdd}>
        <input
          type="url"
          required
          placeholder="https://example.com"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <input
          type="text"
          placeholder="Name (optional)"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <button type="submit">Add URL</button>
      </form>

      {error && <p className="error">{error}</p>}

      <table>
        <thead>
          <tr>
            <th>Status</th>
            <th>Name / URL</th>
            <th>Code</th>
            <th>Response</th>
            <th>Last checked</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {monitors.length === 0 && (
            <tr>
              <td colSpan={6} className="empty">
                No monitors yet. Add a URL above.
              </td>
            </tr>
          )}
          {monitors.map((m) => {
            const check = m.latest_check;
            return (
              <tr key={m.id}>
                <td>
                  <StatusBadge check={check} />
                </td>
                <td>
                  <div className="name">{m.name || m.url}</div>
                  {m.name && <div className="url">{m.url}</div>}
                  {check && !check.is_up && check.error && (
                    <div className="reason">{check.error}</div>
                  )}
                </td>
                <td>{check?.status_code ?? "-"}</td>
                <td>
                  {check?.response_time_ms != null
                    ? `${check.response_time_ms} ms`
                    : "-"}
                </td>
                <td title={check ? check.checked_at : ""}>
                  {check ? timeAgo(check.checked_at) : "-"}
                </td>
                <td>
                  <button className="delete" onClick={() => handleDelete(m.id)}>
                    Delete
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </main>
  );
}
