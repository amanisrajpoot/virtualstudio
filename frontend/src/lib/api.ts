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


