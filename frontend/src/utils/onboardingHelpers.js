/**
 * Onboarding Helper Functions
 * Smart logic for adaptive onboarding flow
 */

/**
 * Generate personalized learning suggestions based on user responses
 */
export const generatePersonalizedSuggestions = (formData) => {
  const suggestions = {
    learningPaths: [],
    recommendedPlatforms: [],
    contentTypes: [],
    timeManagement: null,
    difficultyProgression: null
  };

  // Analyze learning goals for path suggestions
  const goals = formData.learning_goals || [];
  
  if (goals.includes('web_dev')) {
    suggestions.learningPaths.push({
      title: 'Full Stack Web Development',
      description: 'HTML, CSS, JavaScript, React, Node.js',
      duration: '6-12 months',
      difficulty: formData.experience_level === 'complete_beginner' ? 'beginner' : 'intermediate'
    });
  }
  
  if (goals.includes('ai_ml')) {
    suggestions.learningPaths.push({
      title: 'AI & Machine Learning Specialist',
      description: 'Python, TensorFlow, Data Science',
      duration: '8-18 months',
      difficulty: formData.experience_level === 'complete_beginner' ? 'beginner' : 'advanced'
    });
  }
  
  if (goals.includes('mobile_dev')) {
    suggestions.learningPaths.push({
      title: 'Mobile App Development',
      description: 'React Native or Flutter',
      duration: '4-8 months',
      difficulty: 'intermediate'
    });
  }

  // Platform recommendations based on experience and goals
  if (formData.experience_level === 'complete_beginner') {
    suggestions.recommendedPlatforms = ['udemy', 'codecademy', 'freecodecamp'];
  } else if (formData.experience_level === 'advanced') {
    suggestions.recommendedPlatforms = ['coursera', 'edx', 'pluralsight'];
  } else {
    suggestions.recommendedPlatforms = ['udemy', 'coursera', 'pluralsight'];
  }

  // Content type suggestions based on learning style
  const learningStyles = formData.learning_style || [];
  if (learningStyles.includes('visual')) {
    suggestions.contentTypes.push('video', 'interactive');
  }
  if (learningStyles.includes('hands_on')) {
    suggestions.contentTypes.push('project', 'interactive');
  }
  if (learningStyles.includes('reading')) {
    suggestions.contentTypes.push('article', 'book');
  }

  // Time management suggestions
  const timeAvailability = formData.time_availability;
  if (timeAvailability === '1-2hrs') {
    suggestions.timeManagement = {
      strategy: 'Micro-learning',
      sessionLength: '15-30 minutes',
      frequency: '4-5 times per week',
      tips: ['Focus on bite-sized content', 'Use mobile learning apps', 'Set daily reminders']
    };
  } else if (timeAvailability === '5+hrs') {
    suggestions.timeManagement = {
      strategy: 'Intensive Learning',
      sessionLength: '2-3 hours',
      frequency: '2-3 times per week',
      tips: ['Take regular breaks', 'Practice active learning', 'Join study groups']
    };
  }

  // Difficulty progression based on experience
  const experienceLevel = formData.experience_level;
  if (experienceLevel === 'complete_beginner') {
    suggestions.difficultyProgression = {
      start: 'fundamentals',
      progression: ['basics', 'intermediate', 'advanced'],
      timeline: '3-6 months per level'
    };
  } else if (experienceLevel === 'advanced') {
    suggestions.difficultyProgression = {
      start: 'advanced',
      progression: ['specialization', 'expert'],
      timeline: '2-4 months per level'
    };
  }

  return suggestions;
};

/**
 * Validate onboarding data completeness
 */
export const validateOnboardingData = (formData) => {
  const errors = {};
  const warnings = {};

  // Required fields validation
  if (!formData.learning_goals || formData.learning_goals.length === 0) {
    errors.learning_goals = 'Please select at least one learning goal';
  }

  if (!formData.experience_level) {
    errors.experience_level = 'Please select your experience level';
  }

  if (!formData.preferred_pace) {
    errors.preferred_pace = 'Please select your preferred learning pace';
  }

  if (!formData.learning_style || formData.learning_style.length === 0) {
    warnings.learning_style = 'Consider selecting learning styles for better recommendations';
  }

  if (!formData.time_availability) {
    errors.time_availability = 'Please specify your available time for learning';
  }

  if (!formData.preferred_platforms || formData.preferred_platforms.length === 0) {
    warnings.preferred_platforms = 'Select platforms for personalized course recommendations';
  }

  // Logical validation
  if (formData.target_timeline === '3months' && formData.preferred_pace === 'slow') {
    warnings.timeline_pace = 'Your timeline and pace might not align. Consider adjusting one of them.';
  }

  if (formData.experience_level === 'complete_beginner' && formData.preferred_pace === 'fast') {
    warnings.experience_pace = 'Fast pace might be challenging for beginners. Consider moderate pace.';
  }

  return { errors, warnings, isValid: Object.keys(errors).length === 0 };
};

/**
 * Calculate onboarding completion score
 */
export const calculateCompletionScore = (formData) => {
  const weights = {
    learning_goals: 0.25,
    experience_level: 0.20,
    learning_preferences: 0.25, // pace + style + career + timeline
    availability: 0.30 // time + platforms + content_types + languages
  };

  let score = 0;

  // Learning goals score
  if (formData.learning_goals && formData.learning_goals.length > 0) {
    score += weights.learning_goals;
  }

  // Experience level score
  if (formData.experience_level) {
    score += weights.experience_level;
  }

  // Learning preferences score (average of sub-components)
  let preferencesScore = 0;
  let preferencesComponents = 0;

  if (formData.preferred_pace) {
    preferencesScore += 0.25;
    preferencesComponents++;
  }
  if (formData.learning_style && formData.learning_style.length > 0) {
    preferencesScore += 0.25;
    preferencesComponents++;
  }
  if (formData.career_stage) {
    preferencesScore += 0.25;
    preferencesComponents++;
  }
  if (formData.target_timeline) {
    preferencesScore += 0.25;
    preferencesComponents++;
  }

  if (preferencesComponents > 0) {
    score += weights.learning_preferences * (preferencesScore / preferencesComponents * 4);
  }

  // Availability score (average of sub-components)
  let availabilityScore = 0;
  let availabilityComponents = 0;

  if (formData.time_availability) {
    availabilityScore += 0.25;
    availabilityComponents++;
  }
  if (formData.preferred_platforms && formData.preferred_platforms.length > 0) {
    availabilityScore += 0.25;
    availabilityComponents++;
  }
  if (formData.content_types && formData.content_types.length > 0) {
    availabilityScore += 0.25;
    availabilityComponents++;
  }
  if (formData.language_preference && formData.language_preference.length > 0) {
    availabilityScore += 0.25;
    availabilityComponents++;
  }

  if (availabilityComponents > 0) {
    score += weights.availability * (availabilityScore / availabilityComponents * 4);
  }

  return Math.round(score * 100);
};

/**
 * Generate adaptive questionnaire based on previous answers
 */
export const getAdaptiveQuestions = (currentStep, formData) => {
  const adaptiveQuestions = {};

  switch (currentStep) {
    case 'experience':
      // Adapt experience questions based on learning goals
      const techGoals = formData.learning_goals?.filter(goal => 
        ['web_dev', 'mobile_dev', 'ai_ml', 'data_science', 'devops', 'languages'].includes(goal)
      ) || [];
      
      if (techGoals.length > 0) {
        adaptiveQuestions.additionalContext = {
          question: 'Do you have any programming experience?',
          options: ['Never coded before', 'Basic syntax knowledge', 'Built small projects', 'Professional experience']
        };
      }
      break;

    case 'preferences':
      // Adapt preference questions based on experience level
      if (formData.experience_level === 'complete_beginner') {
        adaptiveQuestions.recommendedPace = 'slow';
        adaptiveQuestions.highlightedStyles = ['visual', 'hands_on', 'videos'];
      } else if (formData.experience_level === 'advanced') {
        adaptiveQuestions.recommendedPace = 'fast';
        adaptiveQuestions.highlightedStyles = ['reading', 'interactive'];
      }
      break;

    case 'availability':
      // Adapt platform suggestions based on goals and experience
      const businessGoals = formData.learning_goals?.filter(goal => 
        ['business', 'marketing', 'finance'].includes(goal)
      ) || [];
      
      if (businessGoals.length > 0) {
        adaptiveQuestions.recommendedPlatforms = ['linkedin_learning', 'coursera', 'udemy'];
      } else if (techGoals.length > 0) {
        adaptiveQuestions.recommendedPlatforms = ['pluralsight', 'codecademy', 'udemy'];
      }
      break;
  }

  return adaptiveQuestions;
};

/**
 * Generate personalized course filters
 */
export const generatePersonalizedFilters = (formData) => {
  const filters = {
    difficulty: [],
    duration: [],
    platforms: formData.preferred_platforms || [],
    contentTypes: formData.content_types || [],
    language: formData.language_preference || ['english'],
    topics: formData.learning_goals || []
  };

  // Difficulty based on experience
  switch (formData.experience_level) {
    case 'complete_beginner':
      filters.difficulty = ['beginner'];
      break;
    case 'some_basics':
      filters.difficulty = ['beginner', 'intermediate'];
      break;
    case 'intermediate':
      filters.difficulty = ['intermediate', 'advanced'];
      break;
    case 'advanced':
      filters.difficulty = ['advanced', 'expert'];
      break;
  }

  // Duration based on time availability
  switch (formData.time_availability) {
    case '1-2hrs':
      filters.duration = ['short']; // < 10 hours
      break;
    case '3-5hrs':
      filters.duration = ['short', 'medium']; // < 40 hours
      break;
    case '5+hrs':
      filters.duration = ['medium', 'long']; // any duration
      break;
  }

  return filters;
};