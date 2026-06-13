export const API_BASE = "http://127.0.0.1:8000/api";

export async function compileStory(text: string) {
  const res = await fetch(`${API_BASE}/story/compile`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ story_text: text }),
  });
  return res.json();
}

export async function fetchProjects() {
  const res = await fetch(`${API_BASE}/projects`);
  return res.json();
}

export async function fetchRenderJobs() {
  const res = await fetch(`${API_BASE}/render/jobs`);
  return res.json();
}

export async function fetchMetrics() {
  const res = await fetch(`${API_BASE}/observability/metrics`);
  if (!res.ok) throw new Error("Failed to fetch metrics");
  return res.json();
}

export async function fetchFailures() {
  const res = await fetch(`${API_BASE}/observability/failures`);
  if (!res.ok) throw new Error("Failed to fetch failures");
  return res.json();
}

export async function fetchStoryHealth(storyId: string) {
  const res = await fetch(`${API_BASE}/observability/health/${storyId}`);
  if (!res.ok) throw new Error("Failed to fetch health");
  return res.json();
}

export async function fetchCharacters() {
  const res = await fetch(`${API_BASE}/characters`);
  return res.json();
}

export async function saveCharacter(profile: any) {
  const res = await fetch(`${API_BASE}/characters`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(profile),
  });
  return res.json();
}

export async function generateCharacterConcept(description: string) {
  const res = await fetch(`${API_BASE}/characters/generate-concept`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ description }),
  });
  return res.json();
}

export async function fetchWorlds() {
  const res = await fetch(`${API_BASE}/worlds`);
  return res.json();
}

export async function saveWorld(profile: any) {
  const res = await fetch(`${API_BASE}/worlds`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(profile),
  });
  return res.json();
}

export async function generateWorld(description: string) {
  const res = await fetch(`${API_BASE}/worlds/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ description }),
  });
  return res.json();
}

export async function fetchTemplates() {
  const res = await fetch(`${API_BASE}/templates`);
  return res.json();
}

export async function fetchGoals() {
  const res = await fetch(`${API_BASE}/goals`);
  return res.json();
}

export async function fetchArchetypes() {
  const res = await fetch(`${API_BASE}/archetypes`);
  return res.json();
}

// --- Projects ---
export async function fetchProjectsList() {
  const res = await fetch(`${API_BASE}/projects`);
  return res.json();
}

export async function createProject(data: any) {
  const res = await fetch(`${API_BASE}/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function saveProjectSnapshot(projectId: string, data: any) {
  const res = await fetch(`${API_BASE}/projects/${projectId}/snapshot`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

// --- Collaboration ---
export async function fetchMockUsers() {
  const res = await fetch(`${API_BASE}/auth/users`);
  return res.json();
}

export async function fetchComments(projectId: string) {
  const res = await fetch(`${API_BASE}/projects/${projectId}/comments`);
  return res.json();
}

export async function addComment(projectId: string, data: any) {
  const res = await fetch(`${API_BASE}/projects/${projectId}/comments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function resolveComment(projectId: string, commentId: string, userId: string) {
  const res = await fetch(`${API_BASE}/projects/${projectId}/comments/${commentId}/resolve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId }),
  });
  return res.json();
}

export async function approveRevision(projectId: string, revisionId: string, userId: string) {
  const res = await fetch(`${API_BASE}/projects/${projectId}/revisions/${revisionId}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId }),
  });
  return res.json();
}

// --- Render Queue ---
export async function fetchRenderJobs() {
  const res = await fetch(`${API_BASE}/render/jobs`);
  return res.json();
}

export async function fetchRenderMetrics() {
  const res = await fetch(`${API_BASE}/render/metrics`);
  return res.json();
}

export async function submitRenderJob(data: any) {
  const res = await fetch(`${API_BASE}/render/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

// --- Marketplace ---
export async function fetchMarketplaceAssets(query: string = "") {
  const res = await fetch(`${API_BASE}/marketplace/assets${query}`);
  return res.json();
}

export async function publishMarketplaceAsset(data: any) {
  const res = await fetch(`${API_BASE}/marketplace/publish`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function forkMarketplaceAsset(assetId: string, authorId: string) {
  const res = await fetch(`${API_BASE}/marketplace/fork`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ asset_id: assetId, author_id: authorId }),
  });
  return res.json();
}

export async function rateMarketplaceAsset(assetId: string, userId: string, score: number) {
  const res = await fetch(`${API_BASE}/marketplace/assets/${assetId}/rate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, score }),
  });
  return res.json();
}

export async function downloadMarketplaceAsset(assetId: string) {
  const res = await fetch(`${API_BASE}/marketplace/assets/${assetId}/download`, {
    method: "POST",
  });
  return res.json();
}

export async function generateSkeleton(data: any) {
  const res = await fetch(`${API_BASE}/stories/generate-skeleton`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  return res.json();
}

export async function saveStory(data: any) {
  const res = await fetch(`${API_BASE}/stories`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  return res.json();
}

export async function fetchStoryGraph(data: any) {
  const res = await fetch(`${API_BASE}/graph/build`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  return res.json();
}

export async function overrideStoryIntent(data: any) {
  const res = await fetch(`${API_BASE}/graph/override-intent`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  return res.json();
}
