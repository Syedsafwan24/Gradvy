/**
 * Real-time validation utilities for user preferences
 */

// Validation rules for basic info preferences
export const basicInfoValidationRules = {
  learning_goals: {
    required: true,
    minLength: 1,
    maxLength: 10,
    message: 'Please select at least 1 learning goal (maximum 10)'
  },
  experience_level: {
    required: true,
    message: 'Please select your experience level'
  },
  preferred_pace: {
    required: true,
    message: 'Please select your preferred learning pace'
  },
  time_availability: {
    required: true,
    message: 'Please indicate your available time'
  },
  learning_style: {
    required: true,
    minLength: 1,
    maxLength: 5,
    message: 'Please select at least 1 learning style (maximum 5)'
  },
  career_stage: {
    required: true,
    message: 'Please select your career stage'
  },
  target_timeline: {
    required: true,
    message: 'Please select your target timeline'
  }
};

// Validation rules for content preferences
export const contentPreferencesValidationRules = {
  preferred_platforms: {
    required: false,
    minLength: 0,
    maxLength: 9,
    message: 'Please select up to 9 preferred platforms'
  },
  content_types: {
    required: false,
    minLength: 0,
    maxLength: 7,
    message: 'Please select up to 7 content types'
  },
  difficulty_preference: {
    required: false,
    message: 'Please select difficulty preference'
  },
  duration_preference: {
    required: false,
    message: 'Please select duration preference'
  },
  language_preference: {
    required: true,
    minLength: 1,
    maxLength: 5,
    message: 'Please select at least 1 language (maximum 5)'
  },
  instructor_ratings_min: {
    required: false,
    min: 0.0,
    max: 5.0,
    message: 'Instructor rating must be between 0 and 5'
  }
};

/**
 * Validate a single field value against its rules
 */
export const validateField = (fieldName, value, rules) => {
  const rule = rules[fieldName];
  if (!rule) return { isValid: true };

  const errors = [];

  // Required field validation
  if (rule.required) {
    if (value === undefined || value === null || 
        (Array.isArray(value) && value.length === 0) ||
        (typeof value === 'string' && value.trim() === '')) {
      errors.push(rule.message || `${fieldName} is required`);
    }
  }

  // Array length validation
  if (Array.isArray(value) && rule.minLength !== undefined) {
    if (value.length < rule.minLength) {
      errors.push(rule.message || `${fieldName} must have at least ${rule.minLength} items`);
    }
  }

  if (Array.isArray(value) && rule.maxLength !== undefined) {
    if (value.length > rule.maxLength) {
      errors.push(rule.message || `${fieldName} cannot have more than ${rule.maxLength} items`);
    }
  }

  // Number range validation
  if (typeof value === 'number' && rule.min !== undefined) {
    if (value < rule.min) {
      errors.push(rule.message || `${fieldName} must be at least ${rule.min}`);
    }
  }

  if (typeof value === 'number' && rule.max !== undefined) {
    if (value > rule.max) {
      errors.push(rule.message || `${fieldName} cannot exceed ${rule.max}`);
    }
  }

  // String length validation
  if (typeof value === 'string' && rule.minLength !== undefined) {
    if (value.length < rule.minLength) {
      errors.push(rule.message || `${fieldName} must be at least ${rule.minLength} characters`);
    }
  }

  if (typeof value === 'string' && rule.maxLength !== undefined) {
    if (value.length > rule.maxLength) {
      errors.push(rule.message || `${fieldName} cannot exceed ${rule.maxLength} characters`);
    }
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Validate basic info preferences section
 */
export const validateBasicInfo = (basicInfo) => {
  const errors = {};
  let isValid = true;

  Object.keys(basicInfoValidationRules).forEach(field => {
    const validation = validateField(field, basicInfo?.[field], basicInfoValidationRules);
    if (!validation.isValid) {
      errors[field] = validation.errors;
      isValid = false;
    }
  });

  return { isValid, errors };
};

/**
 * Validate content preferences section
 */
export const validateContentPreferences = (contentPreferences) => {
  const errors = {};
  let isValid = true;

  Object.keys(contentPreferencesValidationRules).forEach(field => {
    const validation = validateField(field, contentPreferences?.[field], contentPreferencesValidationRules);
    if (!validation.isValid) {
      errors[field] = validation.errors;
      isValid = false;
    }
  });

  return { isValid, errors };
};

/**
 * Validate entire user preferences object
 */
export const validateUserPreferences = (preferences) => {
  const basicInfoValidation = validateBasicInfo(preferences?.basic_info);
  const contentPrefsValidation = validateContentPreferences(preferences?.content_preferences);

  const errors = {};
  if (!basicInfoValidation.isValid) {
    errors.basic_info = basicInfoValidation.errors;
  }
  if (!contentPrefsValidation.isValid) {
    errors.content_preferences = contentPrefsValidation.errors;
  }

  return {
    isValid: basicInfoValidation.isValid && contentPrefsValidation.isValid,
    errors,
    sections: {
      basic_info: basicInfoValidation,
      content_preferences: contentPrefsValidation
    }
  };
};

/**
 * Get validation summary for UI display
 */
export const getValidationSummary = (preferences) => {
  const validation = validateUserPreferences(preferences);
  
  const totalFields = Object.keys(basicInfoValidationRules).length + 
                     Object.keys(contentPreferencesValidationRules).filter(
                       key => contentPreferencesValidationRules[key].required
                     ).length;
  
  let validFields = 0;
  
  // Count valid basic info fields
  if (preferences?.basic_info) {
    Object.keys(basicInfoValidationRules).forEach(field => {
      const validation = validateField(field, preferences.basic_info[field], basicInfoValidationRules);
      if (validation.isValid) validFields++;
    });
  }
  
  // Count valid content preferences fields
  if (preferences?.content_preferences) {
    Object.keys(contentPreferencesValidationRules).forEach(field => {
      const rule = contentPreferencesValidationRules[field];
      if (rule.required) {
        const validation = validateField(field, preferences.content_preferences[field], contentPreferencesValidationRules);
        if (validation.isValid) validFields++;
      }
    });
  }

  return {
    ...validation,
    completionPercentage: Math.round((validFields / totalFields) * 100),
    validFields,
    totalFields
  };
};

/**
 * Real-time field validation with debouncing
 */
export class FieldValidator {
  constructor(debounceMs = 300) {
    this.debounceMs = debounceMs;
    this.timeouts = {};
  }

  validateWithDebounce(fieldName, value, rules, callback) {
    // Clear existing timeout for this field
    if (this.timeouts[fieldName]) {
      clearTimeout(this.timeouts[fieldName]);
    }

    // Set new timeout
    this.timeouts[fieldName] = setTimeout(() => {
      const validation = validateField(fieldName, value, rules);
      callback(fieldName, validation);
    }, this.debounceMs);
  }

  clearTimeout(fieldName) {
    if (this.timeouts[fieldName]) {
      clearTimeout(this.timeouts[fieldName]);
      delete this.timeouts[fieldName];
    }
  }

  clearAllTimeouts() {
    Object.keys(this.timeouts).forEach(fieldName => {
      clearTimeout(this.timeouts[fieldName]);
    });
    this.timeouts = {};
  }
}

/**
 * Smart validation suggestions based on user input
 */
export const getValidationSuggestions = (preferences) => {
  const suggestions = [];
  
  // Check for common validation issues and provide suggestions
  if (!preferences?.basic_info?.learning_goals || preferences.basic_info.learning_goals.length === 0) {
    suggestions.push({
      type: 'error',
      field: 'learning_goals',
      message: 'Add learning goals to get personalized recommendations',
      action: 'Select at least one area you want to learn about'
    });
  }

  if (!preferences?.basic_info?.experience_level) {
    suggestions.push({
      type: 'warning',
      field: 'experience_level',
      message: 'Set your experience level for better content matching',
      action: 'Choose your current skill level'
    });
  }

  if (preferences?.basic_info?.learning_goals?.length > 5) {
    suggestions.push({
      type: 'info',
      field: 'learning_goals',
      message: 'Consider focusing on fewer goals for better results',
      action: 'Try selecting 3-5 main learning areas'
    });
  }

  if (!preferences?.content_preferences?.preferred_platforms || 
      preferences.content_preferences.preferred_platforms.length === 0) {
    suggestions.push({
      type: 'info',
      field: 'preferred_platforms',
      message: 'Select preferred platforms to filter recommendations',
      action: 'Choose platforms you like to learn from'
    });
  }

  return suggestions;
};

/**
 * Export utility for form validation states
 */
export const VALIDATION_STATES = {
  IDLE: 'idle',
  VALIDATING: 'validating',
  VALID: 'valid',
  INVALID: 'invalid'
};