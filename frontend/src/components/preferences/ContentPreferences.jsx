'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { 
  BookOpen, 
  Play, 
  FileText, 
  Headphones,
  Globe,
  Clock,
  Star,
  TrendingUp,
  Settings,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

const PLATFORMS = [
  {
    id: 'udemy',
    name: 'Udemy',
    description: 'Comprehensive courses with lifetime access',
    icon: '🎓',
    popular: true,
    strengths: ['Practical projects', 'Affordable pricing', 'Wide variety']
  },
  {
    id: 'coursera',
    name: 'Coursera',
    description: 'University-level courses and specializations',
    icon: '🏛️',
    popular: true,
    strengths: ['Academic quality', 'Certificates', 'Structured learning']
  },
  {
    id: 'youtube',
    name: 'YouTube',
    description: 'Free tutorials and educational videos',
    icon: '📺',
    popular: true,
    strengths: ['Free content', 'Quick tutorials', 'Community']
  },
  {
    id: 'edx',
    name: 'edX',
    description: 'Courses from top universities',
    icon: '🎯',
    popular: false,
    strengths: ['University partnerships', 'High quality', 'Research-based']
  },
  {
    id: 'pluralsight',
    name: 'Pluralsight',
    description: 'Technology and creative skills',
    icon: '💡',
    popular: false,
    strengths: ['Tech focus', 'Skill assessments', 'Learning paths']
  },
  {
    id: 'linkedin_learning',
    name: 'LinkedIn Learning',
    description: 'Professional development courses',
    icon: '💼',
    popular: false,
    strengths: ['Professional skills', 'Career focus', 'Industry experts']
  },
  {
    id: 'codecademy',
    name: 'Codecademy',
    description: 'Interactive coding lessons',
    icon: '👨‍💻',
    popular: false,
    strengths: ['Interactive coding', 'Beginner friendly', 'Practice projects']
  },
  {
    id: 'freecodecamp',
    name: 'freeCodeCamp',
    description: 'Free coding bootcamp curriculum',
    icon: '🔥',
    popular: false,
    strengths: ['Completely free', 'Full curriculum', 'Certifications']
  }
];

const CONTENT_TYPES = [
  {
    id: 'video',
    name: 'Video Courses',
    description: 'Structured video lessons and tutorials',
    icon: Play,
    benefits: ['Visual learning', 'Step-by-step guidance', 'Replay ability']
  },
  {
    id: 'article',
    name: 'Articles & Blogs',
    description: 'Written tutorials and guides',
    icon: FileText,
    benefits: ['Quick reference', 'Detailed explanations', 'Searchable content']
  },
  {
    id: 'interactive',
    name: 'Interactive Content',
    description: 'Hands-on labs and coding exercises',
    icon: Settings,
    benefits: ['Practice while learning', 'Immediate feedback', 'Skill building']
  },
  {
    id: 'podcast',
    name: 'Podcasts',
    description: 'Audio content for learning on-the-go',
    icon: Headphones,
    benefits: ['Learn while commuting', 'Expert interviews', 'Industry insights']
  },
  {
    id: 'book',
    name: 'Books & eBooks',
    description: 'Comprehensive written materials',
    icon: BookOpen,
    benefits: ['In-depth coverage', 'Reference material', 'Structured knowledge']
  },
  {
    id: 'quiz',
    name: 'Quizzes & Tests',
    description: 'Practice tests and assessments',
    icon: CheckCircle,
    benefits: ['Knowledge validation', 'Progress tracking', 'Exam preparation']
  }
];

const LANGUAGES = [
  { id: 'english', name: 'English', flag: '🇺🇸' },
  { id: 'spanish', name: 'Spanish', flag: '🇪🇸' },
  { id: 'french', name: 'French', flag: '🇫🇷' },
  { id: 'german', name: 'German', flag: '🇩🇪' },
  { id: 'portuguese', name: 'Portuguese', flag: '🇵🇹' },
  { id: 'mandarin', name: 'Mandarin', flag: '🇨🇳' },
  { id: 'japanese', name: 'Japanese', flag: '🇯🇵' },
  { id: 'korean', name: 'Korean', flag: '🇰🇷' }
];

export default function ContentPreferences({ preferences, loading, onPreferenceChange }) {
  const contentPrefs = preferences?.content_preferences || {};
  
  const [selectedPlatforms, setSelectedPlatforms] = useState(contentPrefs.preferred_platforms || []);
  const [selectedContentTypes, setSelectedContentTypes] = useState(contentPrefs.content_types || []);
  const [selectedLanguages, setSelectedLanguages] = useState(contentPrefs.language_preference || ['english']);
  const [difficultyPreference, setDifficultyPreference] = useState(contentPrefs.difficulty_preference || 'mixed');
  const [durationPreference, setDurationPreference] = useState(contentPrefs.duration_preference || 'mixed');
  const [instructorRating, setInstructorRating] = useState([contentPrefs.instructor_ratings_min || 4.0]);

  const handlePlatformToggle = (platformId) => {
    const newPlatforms = selectedPlatforms.includes(platformId)
      ? selectedPlatforms.filter(id => id !== platformId)
      : [...selectedPlatforms, platformId];
    
    setSelectedPlatforms(newPlatforms);
    onPreferenceChange('content_preferences', { preferred_platforms: newPlatforms });
  };

  const handleContentTypeToggle = (typeId) => {
    const newTypes = selectedContentTypes.includes(typeId)
      ? selectedContentTypes.filter(id => id !== typeId)
      : [...selectedContentTypes, typeId];
    
    setSelectedContentTypes(newTypes);
    onPreferenceChange('content_preferences', { content_types: newTypes });
  };

  const handleLanguageToggle = (langId) => {
    const newLanguages = selectedLanguages.includes(langId)
      ? selectedLanguages.filter(id => id !== langId)
      : [...selectedLanguages, langId];
    
    setSelectedLanguages(newLanguages);
    onPreferenceChange('content_preferences', { language_preference: newLanguages });
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-3">
                {[1, 2, 3, 4, 5, 6].map((j) => (
                  <div key={j} className="h-16 bg-gray-200 rounded"></div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Current Selection Summary */}
      <motion.div variants={itemVariants}>
        <Card className="bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span>Your Content Preferences</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Platforms ({selectedPlatforms.length})</h4>
                <div className="flex flex-wrap gap-1">
                  {selectedPlatforms.slice(0, 3).map(platformId => {
                    const platform = PLATFORMS.find(p => p.id === platformId);
                    return platform ? (
                      <Badge key={platformId} variant="secondary" className="text-xs">
                        {platform.name}
                      </Badge>
                    ) : null;
                  })}
                  {selectedPlatforms.length > 3 && (
                    <Badge variant="outline" className="text-xs">
                      +{selectedPlatforms.length - 3} more
                    </Badge>
                  )}
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Content Types ({selectedContentTypes.length})</h4>
                <div className="flex flex-wrap gap-1">
                  {selectedContentTypes.slice(0, 3).map(typeId => {
                    const type = CONTENT_TYPES.find(t => t.id === typeId);
                    return type ? (
                      <Badge key={typeId} variant="outline" className="text-xs">
                        {type.name}
                      </Badge>
                    ) : null;
                  })}
                  {selectedContentTypes.length > 3 && (
                    <Badge variant="outline" className="text-xs">
                      +{selectedContentTypes.length - 3} more
                    </Badge>
                  )}
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Languages ({selectedLanguages.length})</h4>
                <div className="flex flex-wrap gap-1">
                  {selectedLanguages.map(langId => {
                    const language = LANGUAGES.find(l => l.id === langId);
                    return language ? (
                      <Badge key={langId} variant="outline" className="text-xs">
                        {language.flag} {language.name}
                      </Badge>
                    ) : null;
                  })}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Learning Platforms */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Globe className="h-5 w-5 text-blue-600" />
              <span>Learning Platforms</span>
            </CardTitle>
            <p className="text-sm text-gray-600">
              Choose your preferred platforms for course recommendations
            </p>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {PLATFORMS.map((platform) => {
                const isSelected = selectedPlatforms.includes(platform.id);
                
                return (
                  <motion.div
                    key={platform.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div
                      onClick={() => handlePlatformToggle(platform.id)}
                      className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                        isSelected
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300 bg-white'
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <span className="text-2xl">{platform.icon}</span>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <h4 className="font-medium text-gray-900">{platform.name}</h4>
                            {platform.popular && (
                              <Badge variant="secondary" className="text-xs bg-orange-100 text-orange-700">
                                Popular
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 mb-2">{platform.description}</p>
                          <div className="space-y-1">
                            {platform.strengths.slice(0, 2).map((strength, index) => (
                              <p key={index} className="text-xs text-green-600">
                                ✓ {strength}
                              </p>
                            ))}
                          </div>
                        </div>
                        <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                          isSelected ? 'border-blue-500 bg-blue-500' : 'border-gray-300'
                        }`}>
                          {isSelected && <div className="w-2 h-2 bg-white rounded-full" />}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Content Types */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BookOpen className="h-5 w-5 text-purple-600" />
              <span>Content Types</span>
            </CardTitle>
            <p className="text-sm text-gray-600">
              Select the types of content that work best for your learning style
            </p>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {CONTENT_TYPES.map((type) => {
                const isSelected = selectedContentTypes.includes(type.id);
                const Icon = type.icon;
                
                return (
                  <motion.div
                    key={type.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div
                      onClick={() => handleContentTypeToggle(type.id)}
                      className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                        isSelected
                          ? 'border-purple-500 bg-purple-50'
                          : 'border-gray-200 hover:border-gray-300 bg-white'
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <Icon className="h-6 w-6 text-purple-600 mt-1" />
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900 mb-1">{type.name}</h4>
                          <p className="text-sm text-gray-600 mb-2">{type.description}</p>
                          <div className="space-y-1">
                            {type.benefits.slice(0, 2).map((benefit, index) => (
                              <p key={index} className="text-xs text-purple-600">
                                ✓ {benefit}
                              </p>
                            ))}
                          </div>
                        </div>
                        <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                          isSelected ? 'border-purple-500 bg-purple-500' : 'border-gray-300'
                        }`}>
                          {isSelected && <div className="w-2 h-2 bg-white rounded-full" />}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Advanced Preferences */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Settings className="h-5 w-5 text-indigo-600" />
              <span>Advanced Preferences</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Difficulty and Duration */}
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Difficulty Preference
                </label>
                <Select value={difficultyPreference} onValueChange={(value) => {
                  setDifficultyPreference(value);
                  onPreferenceChange('content_preferences', { difficulty_preference: value });
                }}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="beginner">Beginner - Start with basics</SelectItem>
                    <SelectItem value="intermediate">Intermediate - Some experience required</SelectItem>
                    <SelectItem value="advanced">Advanced - In-depth and complex</SelectItem>
                    <SelectItem value="mixed">Mixed - All difficulty levels</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Course Duration Preference
                </label>
                <Select value={durationPreference} onValueChange={(value) => {
                  setDurationPreference(value);
                  onPreferenceChange('content_preferences', { duration_preference: value });
                }}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="short">Short - Under 10 hours</SelectItem>
                    <SelectItem value="medium">Medium - 10-40 hours</SelectItem>
                    <SelectItem value="long">Long - 40+ hours</SelectItem>
                    <SelectItem value="mixed">Mixed - Any duration</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Instructor Rating */}
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">
                Minimum Instructor Rating
              </label>
              <div className="space-y-2">
                <Slider
                  value={instructorRating}
                  onValueChange={(value) => {
                    setInstructorRating(value);
                    onPreferenceChange('content_preferences', { instructor_ratings_min: value[0] });
                  }}
                  min={1}
                  max={5}
                  step={0.5}
                  className="w-full"
                />
                <div className="flex items-center justify-between text-sm text-gray-600">
                  <span>1.0</span>
                  <div className="flex items-center space-x-1">
                    <Star className="h-4 w-4 text-yellow-500 fill-current" />
                    <span className="font-medium">{instructorRating[0].toFixed(1)}</span>
                  </div>
                  <span>5.0</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Language Preferences */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Globe className="h-5 w-5 text-green-600" />
              <span>Language Preferences</span>
            </CardTitle>
            <p className="text-sm text-gray-600">
              Select languages for course content and subtitles
            </p>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
              {LANGUAGES.map((language) => {
                const isSelected = selectedLanguages.includes(language.id);
                
                return (
                  <motion.div
                    key={language.id}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <div
                      onClick={() => handleLanguageToggle(language.id)}
                      className={`p-3 rounded-lg border-2 cursor-pointer transition-all text-center ${
                        isSelected
                          ? 'border-green-500 bg-green-50'
                          : 'border-gray-200 hover:border-gray-300 bg-white'
                      }`}
                    >
                      <div className="text-2xl mb-1">{language.flag}</div>
                      <p className="text-sm font-medium">{language.name}</p>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Recommendations Tip */}
      {selectedPlatforms.length === 0 || selectedContentTypes.length === 0 && (
        <motion.div variants={itemVariants}>
          <Card className="border-yellow-200 bg-yellow-50">
            <CardContent className="p-4">
              <div className="flex items-start space-x-3">
                <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-yellow-800">Improve Your Recommendations</h4>
                  <p className="text-sm text-yellow-700 mt-1">
                    {selectedPlatforms.length === 0 && "Select at least one learning platform "}
                    {selectedPlatforms.length === 0 && selectedContentTypes.length === 0 && "and "}
                    {selectedContentTypes.length === 0 && "choose your preferred content types "}
                    to get more relevant course suggestions.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </motion.div>
  );
}