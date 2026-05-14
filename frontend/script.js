const API_PREFIX = "/api/v1";

let currentDocumentId = null;

function $(id) {
  return document.getElementById(id);
}

function setBadge(state) {
  const badge = $("statusBadge");
  const mapping = {
    idle: ["secondary", "idle"],
    uploaded: ["info", "uploaded"],
    processing: ["warning", "processing"],
    completed: ["success", "completed"],
    failed: ["danger", "failed"],
  };
  const [klass, text] = mapping[state] || ["secondary", state];
  badge.className = `badge text-bg-${klass}`;
  badge.textContent = text;
}

function setMessage(kind, text) {
  const box = $("messageBox");
  if (!text) {
    box.classList.add("d-none");
    return;
  }
  box.className = `alert alert-${kind} mt-3`;
  box.textContent = text;
  box.classList.remove("d-none");
}

function setLoading(buttonEl, isLoading) {
  const spinner = buttonEl.querySelector(".spinner-border");
  const label = buttonEl.querySelector(".btn-text");
  buttonEl.disabled = isLoading;
  if (isLoading) {
    spinner.classList.remove("d-none");
    label.classList.add("opacity-75");
  } else {
    spinner.classList.add("d-none");
    label.classList.remove("opacity-75");
  }
}

function validateFile(file) {
  if (!file) return "Please choose a file.";
  const name = (file.name || "").toLowerCase();
  if (!(name.endsWith(".pdf") || name.endsWith(".txt"))) {
    return "Only PDF and TXT files are supported.";
  }
  if (file.size === 0) return "Empty files are not allowed.";
  return null;
}

async function uploadDocument(file) {
  const form = new FormData();
  form.append("file", file);

  const resp = await fetch(`${API_PREFIX}/documents/upload`, {
    method: "POST",
    body: form,
  });
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    const detail = data.detail || "Upload failed.";
    throw new Error(detail);
  }
  return data;
}

async function extractDocument(id) {
  const resp = await fetch(`${API_PREFIX}/documents/${encodeURIComponent(id)}/extract`, {
    method: "POST",
  });
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    const detail = data.detail || "Extraction failed.";
    throw new Error(detail);
  }
  return data;
}

async function analyzeDocument(id) {
  const resp = await fetch(`${API_PREFIX}/documents/${encodeURIComponent(id)}/analyze`, {
    method: "POST",
  });
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    const detail = data.detail || "Analysis failed.";
    throw new Error(detail);
  }
  return data;
}

function renderExtraction(payload) {
  $("extractMeta").textContent = `${payload.file_type.toUpperCase()} • ${payload.character_count} chars`;
  $("previewBox").textContent = payload.preview || "";
}

function renderAnalytics(payload) {
  $("analyticsMeta").textContent = "Ready";
  $("wordCount").textContent = payload.word_count;
  $("sentenceCount").textContent = payload.sentence_count;
  $("readingTime").textContent = payload.estimated_reading_time_minutes;

  const top = $("topWords");
  top.innerHTML = "";
  (payload.top_frequent_words || []).forEach((item) => {
    const badge = document.createElement("span");
    badge.className = "badge text-bg-light border";
    badge.textContent = `${item.word} (${item.count})`;
    top.appendChild(badge);
  });
}

function setActionsEnabled(enabled) {
  $("extractBtn").disabled = !enabled;
  $("analyzeBtn").disabled = !enabled;
}

function init() {
  setBadge("idle");
  setMessage(null, null);
  setActionsEnabled(false);

  $("uploadForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    setMessage(null, null);

    const file = $("fileInput").files[0];
    const error = validateFile(file);
    if (error) {
      setBadge("failed");
      setMessage("danger", error);
      return;
    }

    const uploadBtn = $("uploadBtn");
    setLoading(uploadBtn, true);
    setBadge("processing");

    try {
      const uploaded = await uploadDocument(file);
      currentDocumentId = uploaded.document_id;
      $("documentId").textContent = uploaded.document_id;
      $("originalFilename").textContent = uploaded.original_filename;

      setBadge("uploaded");
      setMessage("success", "Upload successful.");
      setActionsEnabled(true);
      $("extractMeta").textContent = "—";
      $("analyticsMeta").textContent = "—";
      $("previewBox").textContent = "Click Extract to view a preview.";
      $("wordCount").textContent = "—";
      $("sentenceCount").textContent = "—";
      $("readingTime").textContent = "—";
      $("topWords").innerHTML = "";
    } catch (err) {
      setBadge("failed");
      setMessage("danger", err.message || "Upload failed.");
      setActionsEnabled(false);
    } finally {
      setLoading(uploadBtn, false);
    }
  });

  $("extractBtn").addEventListener("click", async () => {
    if (!currentDocumentId) return;
    setMessage(null, null);
    const btn = $("extractBtn");
    setLoading(btn, true);
    setBadge("processing");

    try {
      const extracted = await extractDocument(currentDocumentId);
      renderExtraction(extracted);
      setBadge("completed");
      setMessage("success", "Extraction completed.");
    } catch (err) {
      setBadge("failed");
      setMessage("danger", err.message || "Extraction failed.");
    } finally {
      setLoading(btn, false);
    }
  });

  $("analyzeBtn").addEventListener("click", async () => {
    if (!currentDocumentId) return;
    setMessage(null, null);
    const btn = $("analyzeBtn");
    setLoading(btn, true);
    setBadge("processing");

    try {
      const analytics = await analyzeDocument(currentDocumentId);
      renderAnalytics(analytics);
      setBadge("completed");
      setMessage("success", "Analysis completed.");
    } catch (err) {
      setBadge("failed");
      setMessage("danger", err.message || "Analysis failed.");
    } finally {
      setLoading(btn, false);
    }
  });
}

document.addEventListener("DOMContentLoaded", init);

