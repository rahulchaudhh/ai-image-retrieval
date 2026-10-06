import { useState } from "react";
import axios from "axios";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [prompt, setPrompt] = useState("");
  const [results, setResults] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedImage, setSelectedImage] = useState(null);

  const handleSearch = async (event) => {
    event.preventDefault();

    if (!prompt.trim()) {
      setError("Please describe the image you are looking for.");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");
    setResults([]);

    try {
      const response = await axios.post(`${API_URL}/search`, {
        prompt: prompt.trim(),
      });

      setResults(response.data.results || []);
      setSearchQuery(response.data.search_query || "");
      setMessage(response.data.message || "");
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Could not connect to the search service. Please make sure the backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="hero">
        <p className="eyebrow"></p>

        <h1 className="title">
          Find the right image<br />
          from a simple prompt.
        </h1>

        <p className="subtitle">
          Type what you picture. We’ll find the shots that match.
        </p>

        <form className="search-form" onSubmit={handleSearch}>
          <input
            className="search-input"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g. coffee shop village natural aesthetic ambiance"
            autoComplete="off"
          />

          <button type="submit" className="search-btn" disabled={loading}>
            {loading ? "Searching..." : "Search"}
          </button>
        </form>

        {error && <p className="error-message">{error}</p>}

        {searchQuery && !error && (
          <p className="query-info">
            Search query: <strong>{searchQuery}</strong>
          </p>
        )}
      </header>

      <main className="results-container">
        {loading && (
          <div className="status-state">
            <div className="minimal-spinner" />
            <p>Finding relevant images...</p>
          </div>
        )}

        {!loading && message && results.length === 0 && (
          <div className="status-state">
            <h3>No images found</h3>
            <p>{message}</p>
          </div>
        )}

        {!loading && results.length > 0 && (
          <>
            <div className="results-header">
              <h2>Top results</h2>
              <span className="results-count">{results.length} images</span>
            </div>

            <div className="image-grid">
              {results.map((image) => (
                <article
                  className="image-card"
                  key={image.id}
                  onClick={() => setSelectedImage(image)}
                >
                  <div className="image-wrapper">
                    <img
                      src={image.image_url}
                      alt={image.title || "Image"}
                      loading="lazy"
                      referrerPolicy="no-referrer"
                      onError={(e) => {
                        if (image.thumbnail_url && e.currentTarget.src !== image.thumbnail_url) {
                          e.currentTarget.src = image.thumbnail_url;
                        }
                      }}
                    />
                  </div>

                  <div className="card-info">
                    <h3 className="card-title">{image.title || "Untitled"}</h3>

                    <div className="card-meta">
                      <span className="photographer">
                        Photo by{" "}
                        <a
                          href={image.photographer_url}
                          target="_blank"
                          rel="noreferrer"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {image.photographer}
                        </a>
                      </span>

                      <a
                        className="source-link"
                        href={image.source_url}
                        target="_blank"
                        rel="noreferrer"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {image.source || "Source"} →
                      </a>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </>
        )}
      </main>

      {/* Minimal Lightbox */}
      {selectedImage && (
        <div className="lightbox-backdrop" onClick={() => setSelectedImage(null)}>
          <div className="lightbox-content" onClick={(e) => e.stopPropagation()}>
            <button
              className="lightbox-close"
              onClick={() => setSelectedImage(null)}
              aria-label="Close"
            >
              ✕
            </button>
            <div className="lightbox-img-wrap">
              <img
                src={selectedImage.image_url}
                alt={selectedImage.title}
                referrerPolicy="no-referrer"
                onError={(e) => {
                  if (selectedImage.thumbnail_url && e.currentTarget.src !== selectedImage.thumbnail_url) {
                    e.currentTarget.src = selectedImage.thumbnail_url;
                  }
                }}
              />
            </div>
            <div className="lightbox-info">
              <div>
                <h4>{selectedImage.title || "Untitled"}</h4>
                <p>Photo by {selectedImage.photographer}</p>
              </div>
              <a
                href={selectedImage.source_url}
                target="_blank"
                rel="noreferrer"
                className="lightbox-action"
              >
                View on {selectedImage.source || "Source"} →
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
