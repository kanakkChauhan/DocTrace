import React, { useState, useEffect } from "react";
import type { AppMode } from "../types/product";

interface LandingViewProps {
  onSelectMode: (mode: AppMode) => void;
  onLaunchDemo: () => void;
}

export const TypewriterBadge: React.FC = () => {
  const text =
    "DETERMINISTIC TRACEABILITY ARCHITECTURE";

  const [displayText, setDisplayText] =
    useState("");

  useEffect(() => {
    let index = 0;

    const timer = setInterval(() => {
      if (index <= text.length) {
        setDisplayText(
          text.slice(0, index),
        );

        index++;
      } else {
        clearInterval(timer);
      }
    }, 45);

    return () => clearInterval(timer);
  }, []);

  return (
    <div
      style={{
        fontSize: "0.75rem",
        fontWeight: 800,
        color: "#5A3D31",
        letterSpacing: "0.2em",
        textTransform: "uppercase",
        display: "inline-block",
        fontFamily: "monospace",
        marginBottom: "2rem",
      }}
    >
      {displayText}

      <span
        style={{
          display: "inline-block",
          width: "2px",
          height: "0.75rem",
          backgroundColor: "#5A3D31",
          verticalAlign: "middle",
          marginLeft: "6px",
          animation: "blink 0.8s infinite",
        }}
      />
    </div>
  );
};

export const LandingView: React.FC<
  LandingViewProps
> = ({
  onSelectMode,
  onLaunchDemo,
}) => {
  const [activeTab, setActiveTab] =
    useState<"spec" | "github">("spec");

  /*
   * IMPORTANT:
   *
   * Do NOT call window.history.pushState here.
   *
   * App.tsx owns navigation.
   */
  const handleCardClick = (
    mode: AppMode,
  ) => {
    onSelectMode(mode);
  };

  return (
    <div
      style={{
        minHeight: "85vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        padding: "4rem 1rem 6rem 1.5rem",
        textAlign: "center",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute",
          top: "15%",
          left: "50%",
          transform: "translateX(-50%)",
          width: "600px",
          height: "300px",
          background:
            "radial-gradient(circle, rgba(90, 61, 49, 0.12) 0%, transparent 70%)",
          filter: "blur(60px)",
          zIndex: 0,
          pointerEvents: "none",
        }}
      />

      <div
        style={{
          position: "relative",
          zIndex: 1,
        }}
      >
        <TypewriterBadge />
      </div>

      <h1
        style={{
          position: "relative",
          zIndex: 1,
          fontSize: "3.75rem",
          fontWeight: 850,
          letterSpacing: "-0.04em",
          color: "#2C221E",
          margin: "0 0 1.25rem 0",
          maxWidth: "820px",
          lineHeight: 1.1,
        }}
      >
        The Missing Link Between{" "}
        <span
          style={{
            color: "#5A3D31",
            borderBottom:
              "3px solid #D4C4BC",
          }}
        >
          Specs
        </span>{" "}
        &{" "}
        <span
          style={{
            color: "#5A3D31",
            borderBottom:
              "3px solid #D4C4BC",
          }}
        >
          Code
        </span>
        .
      </h1>

      <p
        style={{
          position: "relative",
          zIndex: 1,
          fontSize: "1.15rem",
          color: "#6B574F",
          maxWidth: "580px",
          margin: "0 auto 3.5rem auto",
          lineHeight: 1.65,
          fontWeight: 500,
        }}
      >
        DocTrace parses ASTs and extracts
        semantic requirements to guarantee
        absolute continuous compliance across
        your engineering lifecycle.
      </p>

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(340px, 1fr))",
          gap: "1.75rem",
          width: "100%",
          maxWidth: "960px",
          marginBottom: "3rem",
          textAlign: "left",
        }}
      >
        <div
          onClick={() =>
            handleCardClick("spec-flow")
          }
          onMouseEnter={() =>
            setActiveTab("spec")
          }
          style={{
            background:
              activeTab === "spec"
                ? "#FFFFFF"
                : "rgba(255, 255, 255, 0.7)",
            border:
              activeTab === "spec"
                ? "2px solid #5A3D31"
                : "1.5px solid #D4C4BC",
            borderRadius: "20px",
            padding: "2.25rem",
            cursor: "pointer",
            transition:
              "all 0.3s cubic-bezier(0.16, 1, 0.3, 1)",
            boxShadow:
              activeTab === "spec"
                ? "0 20px 40px -10px rgba(90, 61, 49, 0.15)"
                : "0 8px 20px rgba(90, 61, 49, 0.04)",
            transform:
              activeTab === "spec"
                ? "translateY(-4px)"
                : "translateY(0)",
            position: "relative",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "4px",
              height: "100%",
              backgroundColor:
                activeTab === "spec"
                  ? "#5A3D31"
                  : "transparent",
            }}
          />

          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent:
                "space-between",
              marginBottom: "1rem",
            }}
          >
            <span
              style={{
                fontSize: "0.75rem",
                fontWeight: 800,
                color: "#9E857B",
                letterSpacing: "0.08em",
                textTransform: "uppercase",
              }}
            >
              Workflow 01
            </span>

            <span
              style={{
                fontSize: "1.25rem",
              }}
            >
              📄
            </span>
          </div>

          <div
            style={{
              fontSize: "1.25rem",
              fontWeight: 800,
              color: "#2C221E",
              marginBottom: "0.75rem",
            }}
          >
            Start with Specification →
          </div>

          <div
            style={{
              fontSize: "0.925rem",
              color: "#6B574F",
              lineHeight: 1.6,
            }}
          >
            Paste technical specs or markdown
            briefs. Our AI engine extracts
            atomic requirements and maps them
            straight to code methods.
          </div>
        </div>

        <div
          onClick={() =>
            handleCardClick("github-flow")
          }
          onMouseEnter={() =>
            setActiveTab("github")
          }
          style={{
            background:
              activeTab === "github"
                ? "#FFFFFF"
                : "rgba(255, 255, 255, 0.7)",
            border:
              activeTab === "github"
                ? "2px solid #5A3D31"
                : "1.5px solid #D4C4BC",
            borderRadius: "20px",
            padding: "2.25rem",
            cursor: "pointer",
            transition:
              "all 0.3s cubic-bezier(0.16, 1, 0.3, 1)",
            boxShadow:
              activeTab === "github"
                ? "0 20px 40px -10px rgba(90, 61, 49, 0.15)"
                : "0 8px 20px rgba(90, 61, 49, 0.04)",
            transform:
              activeTab === "github"
                ? "translateY(-4px)"
                : "translateY(0)",
            position: "relative",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "4px",
              height: "100%",
              backgroundColor:
                activeTab === "github"
                  ? "#5A3D31"
                  : "transparent",
            }}
          />

          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent:
                "space-between",
              marginBottom: "1rem",
            }}
          >
            <span
              style={{
                fontSize: "0.75rem",
                fontWeight: 800,
                color: "#9E857B",
                letterSpacing: "0.08em",
                textTransform: "uppercase",
              }}
            >
              Workflow 02
            </span>

            <span
              style={{
                fontSize: "1.25rem",
              }}
            >
              ⚡️
            </span>
          </div>

          <div
            style={{
              fontSize: "1.25rem",
              fontWeight: 800,
              color: "#2C221E",
              marginBottom: "0.75rem",
            }}
          >
            Connect GitHub Repository →
          </div>

          <div
            style={{
              fontSize: "0.925rem",
              color: "#6B574F",
              lineHeight: 1.6,
            }}
          >
            Ingest remote repositories via archive
            dispatch, execute deep AST parsing,
            and inspect automated compliance
            metrics.
          </div>
        </div>
      </div>

      <div
        style={{
          position: "relative",
          zIndex: 1,
        }}
      >
        <button
          onClick={onLaunchDemo}
          style={{
            background:
              "linear-gradient(135deg, #5A3D31 0%, #3E2920 100%)",
            color: "#FFFFFF",
            border: "none",
            borderRadius: "14px",
            padding: "1.1rem 3rem",
            fontSize: "1.05rem",
            fontWeight: 800,
            cursor: "pointer",
            boxShadow:
              "0 10px 25px rgba(90, 61, 49, 0.35)",
            transition:
              "all 0.3s cubic-bezier(0.16, 1, 0.3, 1)",
            letterSpacing: "-0.01em",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform =
              "translateY(-3px) scale(1.02)";

            e.currentTarget.style.boxShadow =
              "0 15px 35px rgba(90, 61, 49, 0.5)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform =
              "translateY(0) scale(1)";

            e.currentTarget.style.boxShadow =
              "0 10px 25px rgba(90, 61, 49, 0.35)";
          }}
        >
          Explore Live Demo Workspace ✨
        </button>

        <div
          style={{
            fontSize: "0.8rem",
            color: "#9E857B",
            marginTop: "0.75rem",
            fontWeight: 600,
          }}
        >
          No installation or GitHub credentials
          required.
        </div>
      </div>
    </div>
  );
};