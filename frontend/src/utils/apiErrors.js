// DRF/RTK-aware API error normalization utilities

export function normalizeApiError(err) {
  try {
    // RTK Query style
    const status = err?.status ?? err?.originalStatus ?? 0;
    const data = err?.data ?? err?.error ?? err;
    let message = '';
    const fieldErrors = {};
    let code = data?.code ?? undefined;

    if (typeof data === 'string') {
      message = data;
    } else if (data) {
      // Common DRF keys
      if (typeof data.detail === 'string') message = data.detail;
      else if (typeof data.message === 'string') message = data.message;
      else if (typeof data.error === 'string') message = data.error;
      else if (Array.isArray(data.non_field_errors) && data.non_field_errors.length) {
        message = data.non_field_errors.join(' ');
      }

      // Helper to collect flat field errors
      const collectFieldErrors = (obj) => {
        if (!obj || typeof obj !== 'object') return;
        Object.keys(obj).forEach((k) => {
          const v = obj[k];
          if (Array.isArray(v) && v.length && typeof v[0] === 'string') {
            fieldErrors[k] = v.join(' ');
          } else if (v && typeof v === 'object') {
            // Nesting (rare) -> flatten depth-1
            Object.keys(v).forEach((innerK) => {
              const innerV = v[innerK];
              if (Array.isArray(innerV) && innerV.length && typeof innerV[0] === 'string') {
                fieldErrors[innerK] = innerV.join(' ');
              }
            });
          }
        });
      };

      // Collect field errors from top-level and from `.errors` envelope
      collectFieldErrors(data);
      if (data.errors) collectFieldErrors(data.errors);

      // If still no message, use the first field error or fallback
      if (!message) {
        const firstField = Object.keys(fieldErrors)[0];
        if (firstField) message = fieldErrors[firstField];
      }
      // If message looks generic ("failed"), prefer first field error
      if (message && /failed|error/i.test(message) && Object.keys(fieldErrors).length) {
        const firstField = Object.keys(fieldErrors)[0];
        if (firstField) message = fieldErrors[firstField];
      }
    }

    if (!message) {
      // Last resort fallback, but still include status
      message = status ? `Request failed (HTTP ${status})` : 'Request failed';
    }

    return { status, code, message, fieldErrors };
  } catch (e) {
    return { status: 0, message: 'Unexpected error', fieldErrors: {} };
  }
}

// Apply field errors to react-hook-form's setError
export function applyFieldErrorsToForm(normalized, setError) {
  if (!normalized?.fieldErrors) return;
  Object.entries(normalized.fieldErrors).forEach(([field, msg]) => {
    // Map DRF non_field_errors to root
    const name = field === 'non_field_errors' ? 'root' : field;
    try {
      setError(name, { type: 'server', message: msg });
    } catch {}
  });
}

// Small helper to extract a nice title message
export function getTopLevelMessage(normalized) {
  return normalized?.message || 'An error occurred';
}
