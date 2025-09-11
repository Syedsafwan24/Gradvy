// Lightweight local storage for onboarding progress

const VERSION = 'v1';

const keyFor = (userId, type) => `gradvy:onboarding:${VERSION}:${userId}:${type}`;

export function loadOnboardingProgress(userId, type = 'full') {
  try {
    const raw = localStorage.getItem(keyFor(userId, type));
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function saveOnboardingStep(userId, type = 'full', stepIndex, partialData = {}) {
  if (!userId) return;
  try {
    const key = keyFor(userId, type);
    const now = new Date().toISOString();
    const existing = loadOnboardingProgress(userId, type) || { version: VERSION, data: {} };
    const data = { ...existing.data, ...partialData };
    const payload = {
      version: VERSION,
      data,
      last_step: stepIndex,
      updated_at: now,
    };
    localStorage.setItem(key, JSON.stringify(payload));
    return payload;
  } catch {
    // ignore
  }
}

export function saveOnboardingAll(userId, type = 'full', allData) {
  if (!userId) return;
  try {
    const key = keyFor(userId, type);
    const now = new Date().toISOString();
    const payload = {
      version: VERSION,
      data: allData || {},
      last_step: null,
      updated_at: now,
    };
    localStorage.setItem(key, JSON.stringify(payload));
    return payload;
  } catch {
    // ignore
  }
}

// Remove the markOnboardingSubmitted function as we no longer track completion in local storage
// Completion status is now managed exclusively by the backend via onboarding_status field

export function clearOnboardingProgress(userId, type = 'full') {
  if (!userId) return;
  try {
    localStorage.removeItem(keyFor(userId, type));
  } catch {
    // ignore
  }
}

