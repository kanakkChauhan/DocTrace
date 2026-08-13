import { useEffect, useState } from "react";
import {
  createDocument,
  fetchDocuments,
  type DocumentResponse,
} from "./services/api";
import "./App.css";

export default function App() {
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<DocumentResponse | null>(null);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [version, setVersion] = useState("v1.0");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    fetchDocuments()
      .then((docs) => {
        if (isMounted) {
          setDocuments(docs);
          if (docs.length > 0) {
            setSelectedDoc(docs[0]);
          }
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Failed to load documents");
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) return;

    try {
      setLoading(true);
      setError(null);
      const created = await createDocument({ title, content, version });
      setDocuments((prev) => [created, ...prev]);
      setSelectedDoc(created);
      setTitle("");
      setContent("");
      setVersion("v1.0");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save document");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>DocTrace</h1>
        <p className="app-subtitle">Documentation Verification Engine</p>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <main className="dashboard-grid">
        {/* Document Creation Panel */}
        <section className="card">
          <h2>New Document</h2>
          <form onSubmit={handleSubmit} className="doc-form">
            <div className="form-group">
              <label htmlFor="title">Document Title</label>
              <input
                id="title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Authentication Spec"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="version">Version</label>
              <input
                id="version"
                type="text"
                value={version}
                onChange={(e) => setVersion(e.target.value)}
                placeholder="v1.0"
              />
            </div>

            <div className="form-group">
              <label htmlFor="content">Specification Content</label>
              <textarea
                id="content"
                rows={10}
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Enter markdown or raw technical specification here..."
                required
              />
            </div>

            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? "Saving..." : "Save Document"}
            </button>
          </form>
        </section>

        {/* Document Listing & Viewer Panel */}
        <section className="card">
          <h2>Indexed Specifications</h2>
          {documents.length === 0 ? (
            <p className="empty-state">No documents added yet. Create one to begin.</p>
          ) : (
            <div className="doc-layout">
              <ul className="doc-list">
                {documents.map((doc) => (
                  <li
                    key={doc.id}
                    className={`doc-item ${selectedDoc?.id === doc.id ? "active" : ""}`}
                    onClick={() => setSelectedDoc(doc)}
                  >
                    <div className="doc-item-title">{doc.title}</div>
                    <span className="doc-item-version">{doc.version}</span>
                  </li>
                ))}
              </ul>

              {selectedDoc && (
                <div className="doc-viewer">
                  <h3>
                    {selectedDoc.title}{" "}
                    <span className="version-tag">{selectedDoc.version}</span>
                  </h3>
                  <pre className="doc-content-body">{selectedDoc.content}</pre>
                </div>
              )}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}