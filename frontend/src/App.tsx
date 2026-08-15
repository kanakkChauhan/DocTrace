import { useCallback, useEffect, useState } from "react";
import {
  createDocument, deleteDocument, extractClaims, fetchComplianceMetrics, fetchDocuments,
  fetchTraceState, runTraceability, updateLinkStatus, type ClaimResponse, type ComplianceMetrics,
  type DocumentResponse, type TraceLinkResponse,
} from "./services/api";

import { LandingView } from "./components/LandingView";
import { OnboardingFlow } from "./components/OnboardingFlow";
import { PipelineLoader, type PipelineStage } from "./components/PipelineLoader";

import type { AppMode } from "./types/product";
import "./App.css";

const VALID_MODES: AppMode[] = ["landing", "spec-flow", "github-flow", "demo", "workspace"];

function isValidMode(value: string | null): value is AppMode {
  return value !== null && VALID_MODES.includes(value as AppMode);
}

function getRouteFromUrl(): { mode: AppMode; documentId: string | null } {
  const params = new URLSearchParams(window.location.search);
  const mode = isValidMode(params.get("view")) ? params.get("view") as AppMode : "landing";
  return { mode, documentId: params.get("document") };
}

function buildUrl(mode: AppMode, documentId?: string | null): string {
  const params = new URLSearchParams();
  params.set("view", mode);
  if (documentId) params.set("document", documentId);
  return `${window.location.pathname}?${params.toString()}${window.location.hash}`;
}

export default function App() {
  const initialRoute = getRouteFromUrl();

  const [appMode, setAppMode] = useState<AppMode>(initialRoute.mode);
  const [pipelineStage, setPipelineStage] = useState<PipelineStage>("idle");
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<DocumentResponse | null>(null);
  const [claims, setClaims] = useState<ClaimResponse[]>([]);
  const [traceLinks, setTraceLinks] = useState<TraceLinkResponse[]>([]);
  const [compliance, setCompliance] = useState<ComplianceMetrics | null>(null);
  const [specSearch, setSpecSearch] = useState("");

  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const navigate = useCallback((newMode: AppMode, documentId: string | null = null) => {
    const currentRoute = getRouteFromUrl();
    if (currentRoute.mode === newMode && currentRoute.documentId === documentId) {
      setAppMode(newMode);
      if (documentId) {
        const doc = documents.find((item) => item.id === documentId);
        if (doc) setSelectedDoc(doc);
      }
      return;
    }
    window.history.pushState({ mode: newMode, documentId }, "", buildUrl(newMode, documentId));
    setAppMode(newMode);
    if (documentId) {
      const doc = documents.find((item) => item.id === documentId);
      if (doc) setSelectedDoc(doc);
    }
  }, [documents]);

  useEffect(() => {
    const handlePopState = () => {
      const route = getRouteFromUrl();
      setAppMode(route.mode);
      if (route.documentId) setSelectedDoc((curr) => documents.find((d) => d.id === route.documentId) ?? curr);
      if (route.mode === "landing") setError(null);
    };
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, [documents]);

  useEffect(() => {
    fetchDocuments().then((docs) => {
      setDocuments(docs);
      const route = getRouteFromUrl();
      if (route.documentId) {
        const doc = docs.find((item) => item.id === route.documentId);
        if (doc) {
          setSelectedDoc(doc);
          loadCompliance(doc.id);
          fetchTraceData(doc.id);
        }
      }
    }).catch((err) => setError(err instanceof Error ? err.message : "Failed to load documents"));
  }, []);

  const loadCompliance = async (docId: string) => {
    try {
      const metrics = await fetchComplianceMetrics(docId);
      setCompliance(metrics);
    } catch { setCompliance(null); }
  };

  const fetchTraceData = async (docId: string) => {
    try {
      // Reads back whatever was already persisted (claims + trace links).
      // Does NOT re-extract, so claim ids stay stable across reloads and
      // verify/reject state survives navigating away and back.
      const state = await fetchTraceState(docId);
      setClaims(state.claims);
      setTraceLinks(state.links);
    } catch {
      setClaims([]);
      setTraceLinks([]);
    }
  };

  const handleLaunchDemo = async () => {
    try {
      setError(null);
      navigate("demo");

      setPipelineStage("spec_loaded");
      const created = await createDocument({
        title: "Demo Authentication Spec",
        content: "1. The system must hash passwords securely using bcrypt.\n2. JWT tokens must expire after 24 hours.",
        version: "v1.0",
      });
      setDocuments((prev) => [created, ...prev]);
      setSelectedDoc(created);

      setPipelineStage("extracting_requirements");
      const extractedClaims = await extractClaims(created.id);
      setClaims(extractedClaims);

      setPipelineStage("analyzing_and_tracing");
      const traceResp = await runTraceability(created.id, {
        files: [{ filepath: "src/auth.py", source_code: "def hash_password(password: str):\n    '''Hash user password securely.'''\n    pass\n" }],
      });
      // traceResp.claims is the authoritative persisted set whose ids match
      // traceResp.links, so it replaces the earlier extract-only snapshot.
      setClaims(traceResp.claims);
      setTraceLinks(traceResp.links);

      setPipelineStage("calculating_compliance");
      await loadCompliance(created.id);

      setPipelineStage("completed");
      await new Promise(r => setTimeout(r, 600));
      navigate("workspace", created.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Demo initialization failed");
    }
  };

  const handleOnboardingComplete = async (data: { title: string; content: string; source: string }) => {
    try {
      setError(null);
      navigate("demo");

      setPipelineStage("spec_loaded");
      const created = await createDocument({ title: data.title, content: data.content, version: "v1.0" });
      setDocuments((prev) => [created, ...prev]);
      setSelectedDoc(created);

      setPipelineStage("extracting_requirements");
      const extractedClaims = await extractClaims(created.id);
      setClaims(extractedClaims);

      setPipelineStage("analyzing_and_tracing");
      const tracePayload = appMode === "github-flow"
        ? { github_url: data.source }
        : { files: [{ filepath: "src/main.py", source_code: data.source || data.content }] };

      const traceResp = await runTraceability(created.id, tracePayload);
      setClaims(traceResp.claims);
      setTraceLinks(traceResp.links);

      setPipelineStage("calculating_compliance");
      await loadCompliance(created.id);

      setPipelineStage("completed");
      await new Promise(r => setTimeout(r, 600));
      navigate("workspace", created.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Pipeline execution failed");
    }
  };

  const handleStatusChange = async (linkId: string, newStatus: "verified" | "rejected") => {
    try {
      await updateLinkStatus(linkId, newStatus);
      setTraceLinks((prev) => prev.map((link) => (link.id === linkId ? { ...link, status: newStatus } : link)));
      if (selectedDoc) loadCompliance(selectedDoc.id);
    } catch (err) { setError(err instanceof Error ? err.message : "Failed to update link status"); }
  };

  const toggleSelectDoc = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedDocIds((prev) => prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]);
  };

  const confirmDeleteSelected = async () => {
    try {
      for (const id of selectedDocIds) await deleteDocument(id);
      const remainingDocs = documents.filter((doc) => !selectedDocIds.includes(doc.id));
      setDocuments(remainingDocs);
      setSelectedDocIds([]);
      setShowDeleteConfirm(false);

      if (selectedDoc && selectedDocIds.includes(selectedDoc.id)) {
        if (remainingDocs.length > 0) {
          const nextDoc = remainingDocs[0];
          setSelectedDoc(nextDoc);
          loadCompliance(nextDoc.id);
          fetchTraceData(nextDoc.id);
          navigate("workspace", nextDoc.id);
        } else {
          setSelectedDoc(null);
          setClaims([]);
          setTraceLinks([]);
          setCompliance(null);
          navigate("landing");
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete selected documents");
      setShowDeleteConfirm(false);
    }
  };

  const filteredDocuments = documents.filter((doc) => doc.title.toLowerCase().includes(specSearch.toLowerCase()));

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="brand-logo-container" onClick={() => navigate("landing")} style={{ cursor: "pointer" }}>
          <h1 className="brand-name">DocTrace</h1>
        </div>
        <div className="brand-tagline">Semantic Specification & Codebase Verification</div>
      </header>

      {error && appMode !== 'demo' && (
        <div className="error-banner" style={{ color: "#EF4444", background: "rgba(239, 68, 68, 0.1)", padding: "10px 14px", borderRadius: "8px", marginBottom: "1.5rem" }}>
          {error}
        </div>
      )}

      {appMode === "landing" && <LandingView onSelectMode={(mode) => navigate(mode)} onLaunchDemo={handleLaunchDemo} />}

      {(appMode === "spec-flow" || appMode === "github-flow") && (
        <OnboardingFlow mode={appMode} onComplete={handleOnboardingComplete} onBack={() => navigate("landing")} />
      )}

      {appMode === "demo" && <PipelineLoader currentStage={pipelineStage} error={error} />}

      {appMode === "workspace" && selectedDoc && (
        <main className="dashboard-grid">
          <section className="card" style={{ display: 'flex', flexDirection: 'column', height: 'fit-content', maxHeight: '85vh' }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <h2 style={{ margin: 0, fontSize: '1.1rem' }}>Specifications</h2>
                <span style={{ fontSize: '0.7rem', fontWeight: 700, padding: '2px 6px', borderRadius: '10px', background: '#FAF7F5', border: '1px solid #D4C4BC', color: '#6B574F' }}>
                  {documents.length}
                </span>
              </div>
              <button onClick={() => navigate("landing")} style={{ background: "none", border: "1px solid #D4C4BC", color: "#6B574F", padding: "4px 8px", borderRadius: "6px", fontSize: '0.75rem', cursor: "pointer", fontWeight: 700 }}>
                + New Trace
              </button>
            </div>

            <div style={{ marginBottom: '0.75rem' }}>
              <input type="text" placeholder="Filter specifications..." value={specSearch} onChange={(e) => setSpecSearch(e.target.value)} style={{ width: '100%', padding: '8px 12px', background: '#FAF7F5', border: '1px solid #D4C4BC', borderRadius: '8px', fontSize: '0.85rem', color: '#2C221E', outline: 'none', boxSizing: 'border-box' }} />
            </div>

            <div style={{ overflowY: 'auto', maxHeight: '300px', paddingRight: '4px', display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '1rem' }}>
              {filteredDocuments.length === 0 ? (
                <div style={{ fontSize: '0.85rem', color: '#9E857B', textAlign: 'center', padding: '1.5rem 0' }}>No matching specifications.</div>
              ) : (
                filteredDocuments.map((doc) => {
                  const isChecked = selectedDocIds.includes(doc.id);
                  return (
                    <div key={doc.id} className={`doc-item ${selectedDoc?.id === doc.id ? "active" : ""}`} onClick={() => { setSelectedDoc(doc); loadCompliance(doc.id); fetchTraceData(doc.id); navigate("workspace", doc.id); }} style={{ padding: '10px 12px', borderRadius: '10px', cursor: 'pointer', border: selectedDoc?.id === doc.id ? '1.5px solid #5A3D31' : '1px solid #D4C4BC', background: selectedDoc?.id === doc.id ? '#FAF7F5' : '#FFFFFF', display: 'flex', alignItems: 'center', justifyContent: 'space-between', transition: 'all 0.2s ease' }}>
                      <div style={{ overflow: 'hidden', marginRight: '8px' }}>
                        <div className="doc-item-title" style={{ fontSize: '0.9rem', fontWeight: 700, color: '#2C221E', marginBottom: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{doc.title}</div>
                        <span className="doc-item-version" style={{ fontSize: '0.75rem', color: '#9E857B' }}>{doc.version}</span>
                      </div>
                      <input type="checkbox" checked={isChecked} onClick={(e) => toggleSelectDoc(doc.id, e)} onChange={() => {}} style={{ cursor: 'pointer', accentColor: '#5A3D31', width: '16px', height: '16px' }} />
                    </div>
                  );
                })
              )}
            </div>

            {showDeleteConfirm ? (
              <div style={{ background: '#FAF7F5', border: '1.5px solid #D4C4BC', borderRadius: '12px', padding: '1rem', textAlign: 'center' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#2C221E', marginBottom: '0.75rem' }}>Delete {selectedDocIds.length} selected specification{selectedDocIds.length > 1 ? 's' : ''}?</div>
                <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center' }}>
                  <button onClick={confirmDeleteSelected} style={{ background: '#DC2626', color: '#fff', border: 'none', padding: '6px 14px', borderRadius: '6px', fontSize: '0.8rem', fontWeight: 700, cursor: 'pointer' }}>Yes, Delete</button>
                  <button onClick={() => setShowDeleteConfirm(false)} style={{ background: '#FFFFFF', color: '#6B574F', border: '1px solid #D4C4BC', padding: '6px 14px', borderRadius: '6px', fontSize: '0.8rem', fontWeight: 700, cursor: 'pointer' }}>No</button>
                </div>
              </div>
            ) : (
              <button onClick={() => { if (selectedDocIds.length > 0) setShowDeleteConfirm(true); }} disabled={selectedDocIds.length === 0} className="btn-danger" style={{ width: "100%", fontSize: "0.85rem", padding: "10px", opacity: selectedDocIds.length === 0 ? 0.5 : 1, cursor: selectedDocIds.length === 0 ? 'not-allowed' : 'pointer' }}>
                Delete Selected ({selectedDocIds.length})
              </button>
            )}
          </section>

          <section className="card">
            <div className="doc-viewer-header">
              <h3>{selectedDoc.title} <span className="version-tag">{selectedDoc.version}</span></h3>
            </div>
            <pre className="doc-content-body" style={{ maxHeight: "100px", overflowY: "auto" }}>{selectedDoc.content}</pre>

            {compliance && (
              <div style={{ background: "#FAF7F5", border: "1px solid #D4C4BC", borderRadius: "12px", padding: "1.25rem", marginTop: "1.5rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                  <h4 style={{ margin: 0, color: "#2C221E", fontSize: "0.95rem" }}>Compliance Health Matrix</h4>
                  <span style={{ fontSize: "0.85rem", fontWeight: 700, padding: "4px 10px", borderRadius: "12px", backgroundColor: compliance.compliance_percentage >= 70 ? "rgba(16, 185, 129, 0.15)" : "rgba(245, 158, 11, 0.15)", color: compliance.compliance_percentage >= 70 ? "#059669" : "#D97706" }}>
                    {compliance.compliance_percentage}% Compliant
                  </span>
                </div>
                <div style={{ fontSize: "0.75rem", color: "#9E857B", marginBottom: "1rem" }}>
                  {compliance.coverage_percentage}% of requirements have at least one trace link ({compliance.traced_claims}/{compliance.total_claims} traced)
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "0.75rem", textAlign: "center" }}>
                  <div style={{ background: "#FFFFFF", padding: "10px", borderRadius: "8px", border: "1px solid #D4C4BC" }}>
                    <div style={{ fontSize: "0.7rem", color: "#9E857B", textTransform: "uppercase" }}>Requirements</div>
                    <div style={{ fontSize: "1.1rem", fontWeight: 700, color: "#2C221E" }}>{compliance.total_claims}</div>
                  </div>
                  <div style={{ background: "#FFFFFF", padding: "10px", borderRadius: "8px", border: "1px solid #D4C4BC" }}>
                    <div style={{ fontSize: "0.7rem", color: "#059669", textTransform: "uppercase" }}>Verified</div>
                    <div style={{ fontSize: "1.1rem", fontWeight: 700, color: "#059669" }}>{compliance.verified_claims}</div>
                  </div>
                  <div style={{ background: "#FFFFFF", padding: "10px", borderRadius: "8px", border: "1px solid #D4C4BC" }}>
                    <div style={{ fontSize: "0.7rem", color: "#D97706", textTransform: "uppercase" }}>Pending</div>
                    <div style={{ fontSize: "1.1rem", fontWeight: 700, color: "#D97706" }}>{compliance.pending_claims}</div>
                  </div>
                  <div style={{ background: "#FFFFFF", padding: "10px", borderRadius: "8px", border: "1px solid #D4C4BC" }}>
                    <div style={{ fontSize: "0.7rem", color: "#DC2626", textTransform: "uppercase" }}>Untraced</div>
                    <div style={{ fontSize: "1.1rem", fontWeight: 700, color: "#DC2626" }}>{compliance.untraced_claims}</div>
                  </div>
                </div>
              </div>
            )}

            {claims.length > 0 && (
              <div style={{ marginTop: "1.5rem" }}>
                <h4 style={{ color: "#2C221E", fontSize: "1rem", marginBottom: "1rem" }}>Requirements & Evidence Links</h4>
                <ul className="claims-list" style={{ listStyle: "none", padding: 0, display: "flex", flexDirection: "column", gap: "1rem" }}>
                  {claims.map((claim) => {
                    const links = traceLinks.filter((link) => link.claim_id === claim.id);
                    return (
                      <li key={claim.id} className="claim-card">
                        <span className="claim-section">{claim.section || "General"}</span>
                        <p className="claim-statement">{claim.statement}</p>

                        {/* FORCE RENDER EVIDENCE LINKS AND ACTION BUTTONS */}
                        {links.length > 0 ? (
                          <div style={{ marginTop: "1rem", paddingTop: "1rem", borderTop: "1px dashed #D4C4BC" }}>
                            {links.map((link) => (
                              <div key={link.id || Math.random()} style={{ marginBottom: "0.75rem", fontSize: "0.85rem", background: "#FAF7F5", padding: "10px", borderRadius: "8px", border: "1px solid #D4C4BC" }}>
                                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.4rem" }}>
                                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                                    <span style={{ padding: "2px 6px", borderRadius: "4px", fontWeight: 700, fontSize: "0.7rem", backgroundColor: link.match_type === "strong" ? "rgba(16, 185, 129, 0.15)" : "rgba(245, 158, 11, 0.15)", color: link.match_type === "strong" ? "#059669" : "#D97706" }}>
                                      {link.match_type.toUpperCase()} ({(link.match_score * 100).toFixed(0)}%)
                                    </span>
                                    <code style={{ background: "#FFFFFF", padding: "2px 6px", borderRadius: "4px", color: "#2C221E", fontSize: "0.8rem", border: "1px solid #D4C4BC" }}>
                                      {link.filepath} : {link.code_element_name}
                                    </code>
                                  </div>
                                  <div style={{ display: "flex", gap: "6px" }}>
                                    <button onClick={() => handleStatusChange(link.id as string, "verified")} style={{ fontSize: "0.75rem", padding: "3px 8px", borderRadius: "6px", cursor: "pointer", backgroundColor: link.status === "verified" ? "#059669" : "#FFFFFF", color: link.status === "verified" ? "#fff" : "#6B574F", border: "1px solid #D4C4BC", fontWeight: 600 }}>
                                      {link.status === "verified" ? "✓ Verified" : "Verify"}
                                    </button>
                                    <button onClick={() => handleStatusChange(link.id as string, "rejected")} style={{ fontSize: "0.75rem", padding: "3px 8px", borderRadius: "6px", cursor: "pointer", backgroundColor: link.status === "rejected" ? "#DC2626" : "#FFFFFF", color: link.status === "rejected" ? "#fff" : "#6B574F", border: "1px solid #D4C4BC", fontWeight: 600 }}>
                                      {link.status === "rejected" ? "✕ Rejected" : "Reject"}
                                    </button>
                                  </div>
                                </div>
                                <div style={{ color: "#6B574F", fontSize: "0.8rem", paddingLeft: "0.5rem", borderLeft: "2px solid #D4C4BC" }}>
                                  {link.evidence.map((evidence, index) => (
                                    <div key={index}>{evidence}</div>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div style={{ marginTop: "0.75rem", fontSize: "0.8rem", color: "#9E857B", fontStyle: "italic" }}>
                            No code trace links found for this requirement.
                          </div>
                        )}
                      </li>
                    );
                  })}
                </ul>
              </div>
            )}
          </section>
        </main>
      )}
    </div>
  );
}