/**
 * Custom hook for real-time preferences validation
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  validateField,
  validateBasicInfo,
  validateContentPreferences,
  validateUserPreferences,
  getValidationSummary,
  getValidationSuggestions,
  FieldValidator,
  basicInfoValidationRules,
  contentPreferencesValidationRules,
  VALIDATION_STATES
} from '@/utils/preferencesValidation';

export const usePreferencesValidation = (preferences, options = {}) => {
  const {
    debounceMs = 300,
    enableRealTime = true,
    validateOnMount = true
  } = options;

  const [validationState, setValidationState] = useState({
    isValid: true,
    errors: {},
    fieldStates: {},
    summary: null,
    suggestions: []
  });

  const fieldValidatorRef = useRef(new FieldValidator(debounceMs));

  // Validate entire preferences object
  const validateAll = useCallback(() => {
    if (!preferences) return;

    const validation = validateUserPreferences(preferences);
    const summary = getValidationSummary(preferences);
    const suggestions = getValidationSuggestions(preferences);

    setValidationState(prev => ({
      ...prev,
      isValid: validation.isValid,
      errors: validation.errors,
      summary,
      suggestions
    }));

    return validation;
  }, [preferences]);

  // Validate a specific field with real-time feedback
  const validateFieldRealTime = useCallback((section, fieldName, value) => {
    const rules = section === 'basic_info' ? basicInfoValidationRules : contentPreferencesValidationRules;
    
    // Set validating state
    setValidationState(prev => ({
      ...prev,
      fieldStates: {
        ...prev.fieldStates,
        [`${section}.${fieldName}`]: VALIDATION_STATES.VALIDATING
      }
    }));

    // Use debounced validation
    fieldValidatorRef.current.validateWithDebounce(
      `${section}.${fieldName}`,
      value,
      rules,
      (key, validation) => {
        setValidationState(prev => {
          const newErrors = { ...prev.errors };
          const newFieldStates = { ...prev.fieldStates };
          
          // Update field-specific validation state
          if (validation.isValid) {
            // Remove field errors if valid
            if (newErrors[section]) {
              delete newErrors[section][fieldName];
              if (Object.keys(newErrors[section]).length === 0) {
                delete newErrors[section];
              }
            }
            newFieldStates[key] = VALIDATION_STATES.VALID;
          } else {
            // Add field errors if invalid
            if (!newErrors[section]) {
              newErrors[section] = {};
            }
            newErrors[section][fieldName] = validation.errors;
            newFieldStates[key] = VALIDATION_STATES.INVALID;
          }

          return {
            ...prev,
            errors: newErrors,
            fieldStates: newFieldStates,
            isValid: Object.keys(newErrors).length === 0
          };
        });
      }
    );
  }, []);

  // Get validation state for a specific field
  const getFieldValidation = useCallback((section, fieldName) => {
    const key = `${section}.${fieldName}`;
    const fieldState = validationState.fieldStates[key] || VALIDATION_STATES.IDLE;
    const errors = validationState.errors[section]?.[fieldName] || [];

    return {
      state: fieldState,
      isValid: fieldState === VALIDATION_STATES.VALID || fieldState === VALIDATION_STATES.IDLE,
      isValidating: fieldState === VALIDATION_STATES.VALIDATING,
      hasErrors: errors.length > 0,
      errors,
      message: errors[0] // First error message for display
    };
  }, [validationState]);

  // Get validation state for a section
  const getSectionValidation = useCallback((section) => {
    const sectionErrors = validationState.errors[section] || {};
    const hasErrors = Object.keys(sectionErrors).length > 0;

    return {
      isValid: !hasErrors,
      hasErrors,
      errors: sectionErrors,
      errorCount: Object.keys(sectionErrors).length
    };
  }, [validationState]);

  // Clear validation for a specific field
  const clearFieldValidation = useCallback((section, fieldName) => {
    const key = `${section}.${fieldName}`;
    fieldValidatorRef.current.clearTimeout(key);

    setValidationState(prev => {
      const newErrors = { ...prev.errors };
      const newFieldStates = { ...prev.fieldStates };

      // Remove field errors
      if (newErrors[section]) {
        delete newErrors[section][fieldName];
        if (Object.keys(newErrors[section]).length === 0) {
          delete newErrors[section];
        }
      }

      // Reset field state
      newFieldStates[key] = VALIDATION_STATES.IDLE;

      return {
        ...prev,
        errors: newErrors,
        fieldStates: newFieldStates,
        isValid: Object.keys(newErrors).length === 0
      };
    });
  }, []);

  // Clear all validations
  const clearAllValidations = useCallback(() => {
    fieldValidatorRef.current.clearAllTimeouts();
    setValidationState({
      isValid: true,
      errors: {},
      fieldStates: {},
      summary: null,
      suggestions: []
    });
  }, []);

  // Validate on preferences change
  useEffect(() => {
    if (enableRealTime && preferences) {
      const timeoutId = setTimeout(() => {
        validateAll();
      }, debounceMs);

      return () => clearTimeout(timeoutId);
    }
  }, [preferences, enableRealTime, debounceMs, validateAll]);

  // Initial validation
  useEffect(() => {
    if (validateOnMount && preferences) {
      validateAll();
    }
  }, [validateOnMount, preferences, validateAll]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      fieldValidatorRef.current.clearAllTimeouts();
    };
  }, []);

  return {
    // Validation state
    isValid: validationState.isValid,
    errors: validationState.errors,
    summary: validationState.summary,
    suggestions: validationState.suggestions,
    
    // Validation methods
    validateAll,
    validateField: validateFieldRealTime,
    clearFieldValidation,
    clearAllValidations,
    
    // Getters
    getFieldValidation,
    getSectionValidation,
    
    // Utils
    hasErrors: !validationState.isValid,
    completionPercentage: validationState.summary?.completionPercentage || 0,
    validFields: validationState.summary?.validFields || 0,
    totalFields: validationState.summary?.totalFields || 0
  };
};

/**
 * Hook specifically for field-level validation
 */
export const useFieldValidation = (section, fieldName, value, options = {}) => {
  const [validationState, setValidationState] = useState({
    state: VALIDATION_STATES.IDLE,
    isValid: true,
    errors: [],
    message: ''
  });

  const fieldValidatorRef = useRef(new FieldValidator(options.debounceMs || 300));

  const validate = useCallback(() => {
    const rules = section === 'basic_info' ? basicInfoValidationRules : contentPreferencesValidationRules;
    
    setValidationState(prev => ({
      ...prev,
      state: VALIDATION_STATES.VALIDATING
    }));

    fieldValidatorRef.current.validateWithDebounce(
      `${section}.${fieldName}`,
      value,
      rules,
      (key, validation) => {
        setValidationState({
          state: validation.isValid ? VALIDATION_STATES.VALID : VALIDATION_STATES.INVALID,
          isValid: validation.isValid,
          errors: validation.errors,
          message: validation.errors[0] || ''
        });
      }
    );
  }, [section, fieldName, value]);

  useEffect(() => {
    if (options.enableRealTime !== false && value !== undefined) {
      validate();
    }
  }, [value, validate, options.enableRealTime]);

  useEffect(() => {
    return () => {
      fieldValidatorRef.current.clearAllTimeouts();
    };
  }, []);

  return {
    ...validationState,
    validate,
    isValidating: validationState.state === VALIDATION_STATES.VALIDATING
  };
};

export default usePreferencesValidation;