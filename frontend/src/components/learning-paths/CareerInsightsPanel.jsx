// File: frontend/src/components/learning-paths/CareerInsightsPanel.jsx
// Description: Displays career insights for learning paths including job roles, salaries, and market demand
// Why: Shows users real-world career opportunities and job market data for their learning path
// Relevant Files: PathDetailHeader.jsx, ModulesList.jsx, backend/models.py

import React, { useState } from 'react';
import {
  Briefcase,
  DollarSign,
  TrendingUp,
  Users,
  ChevronDown,
  ChevronUp,
  Target,
  Award,
  BarChart3
} from 'lucide-react';

/**
 * Career Insights Panel Component
 *
 * Displays comprehensive career insights for a learning path including:
 * - Career roles and titles
 * - Salary ranges (entry, mid, senior)
 * - Current job openings count
 * - Market demand indicators
 * - Career progression paths
 * - Skills breakdown with importance scores
 */
const CareerInsightsPanel = ({ careerInsights }) => {
  const [expandedRole, setExpandedRole] = useState(null);
  const [showAllRoles, setShowAllRoles] = useState(false);

  if (!careerInsights || !careerInsights.career_roles || careerInsights.career_roles.length === 0) {
    return null;
  }

  const {
    career_roles = [],
    total_job_openings = 0,
    market_demand_score = 0,
    career_progression = []
  } = careerInsights;

  // Show top 3 roles by default, all when expanded
  const visibleRoles = showAllRoles ? career_roles : career_roles.slice(0, 3);

  const toggleRoleExpansion = (roleTitle) => {
    setExpandedRole(expandedRole === roleTitle ? null : roleTitle);
  };

  const getMarketDemandColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-50';
    if (score >= 60) return 'text-blue-600 bg-blue-50';
    if (score >= 40) return 'text-yellow-600 bg-yellow-50';
    return 'text-gray-600 bg-gray-50';
  };

  const getMarketDemandLabel = (score) => {
    if (score >= 80) return 'Very High Demand';
    if (score >= 60) return 'High Demand';
    if (score >= 40) return 'Medium Demand';
    return 'Low Demand';
  };

  const formatSalary = (min, max) => {
    if (!min || !max) return 'Salary not available';
    return `$${(min / 1000).toFixed(0)}k - $${(max / 1000).toFixed(0)}k`;
  };

  const getExperienceLevelBadge = (level) => {
    const badges = {
      'entry': { color: 'bg-green-100 text-green-800', label: 'Entry Level' },
      'mid': { color: 'bg-blue-100 text-blue-800', label: 'Mid Level' },
      'senior': { color: 'bg-purple-100 text-purple-800', label: 'Senior Level' }
    };
    return badges[level] || badges['entry'];
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="bg-indigo-100 p-3 rounded-lg">
            <Briefcase className="w-6 h-6 text-indigo-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Career Insights</h2>
            <p className="text-sm text-gray-600">Real-world opportunities for this learning path</p>
          </div>
        </div>
      </div>

      {/* Market Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* Total Job Openings */}
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-900">Total Job Openings</p>
              <p className="text-2xl font-bold text-blue-700 mt-1">
                {total_job_openings.toLocaleString()}
              </p>
            </div>
            <Users className="w-8 h-8 text-blue-600 opacity-70" />
          </div>
        </div>

        {/* Market Demand */}
        <div className={`rounded-lg p-4 ${getMarketDemandColor(market_demand_score)}`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Market Demand</p>
              <p className="text-2xl font-bold mt-1">
                {getMarketDemandLabel(market_demand_score)}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 opacity-70" />
          </div>
        </div>

        {/* Career Roles Available */}
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-purple-900">Career Roles</p>
              <p className="text-2xl font-bold text-purple-700 mt-1">
                {career_roles.length}
              </p>
            </div>
            <Target className="w-8 h-8 text-purple-600 opacity-70" />
          </div>
        </div>
      </div>

      {/* Career Roles List */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Available Career Paths</h3>

        {visibleRoles.map((role) => {
          const isExpanded = expandedRole === role.role_title;
          const experienceBadge = getExperienceLevelBadge(role.experience_level);

          return (
            <div
              key={role.role_title}
              className="border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
            >
              {/* Role Header */}
              <div
                className="p-4 cursor-pointer"
                onClick={() => toggleRoleExpansion(role.role_title)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h4 className="text-lg font-semibold text-gray-900">{role.role_title}</h4>
                      <span className={`px-2 py-1 text-xs font-medium rounded ${experienceBadge.color}`}>
                        {experienceBadge.label}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{role.role_description}</p>

                    {/* Quick Stats */}
                    <div className="flex flex-wrap gap-4 text-sm">
                      <div className="flex items-center space-x-2">
                        <DollarSign className="w-4 h-4 text-green-600" />
                        <span className="text-gray-700">
                          {formatSalary(role.salary_entry_min, role.salary_entry_max)}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Briefcase className="w-4 h-4 text-blue-600" />
                        <span className="text-gray-700">
                          {role.job_openings_count.toLocaleString()} openings
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <BarChart3 className="w-4 h-4 text-purple-600" />
                        <span className={`font-medium ${
                          role.market_demand === 'very_high' ? 'text-green-600' :
                          role.market_demand === 'high' ? 'text-blue-600' :
                          role.market_demand === 'medium' ? 'text-yellow-600' :
                          'text-gray-600'
                        }`}>
                          {role.market_demand.replace('_', ' ')}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Expand/Collapse Icon */}
                  <button className="ml-4 text-gray-400 hover:text-gray-600">
                    {isExpanded ? (
                      <ChevronUp className="w-5 h-5" />
                    ) : (
                      <ChevronDown className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>

              {/* Expanded Details */}
              {isExpanded && (
                <div className="px-4 pb-4 border-t border-gray-100">
                  {/* Salary Breakdown */}
                  <div className="mt-4 mb-4">
                    <h5 className="text-sm font-semibold text-gray-900 mb-3">Salary Progression</h5>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      <div className="bg-green-50 rounded-lg p-3">
                        <p className="text-xs text-green-800 font-medium mb-1">Entry Level</p>
                        <p className="text-lg font-bold text-green-700">
                          {formatSalary(role.salary_entry_min, role.salary_entry_max)}
                        </p>
                      </div>
                      <div className="bg-blue-50 rounded-lg p-3">
                        <p className="text-xs text-blue-800 font-medium mb-1">Mid Level</p>
                        <p className="text-lg font-bold text-blue-700">
                          {formatSalary(role.salary_mid_min, role.salary_mid_max)}
                        </p>
                      </div>
                      <div className="bg-purple-50 rounded-lg p-3">
                        <p className="text-xs text-purple-800 font-medium mb-1">Senior Level</p>
                        <p className="text-lg font-bold text-purple-700">
                          {formatSalary(role.salary_senior_min, role.salary_senior_max)}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Required Skills */}
                  {role.required_skills && role.required_skills.length > 0 && (
                    <div className="mb-4">
                      <h5 className="text-sm font-semibold text-gray-900 mb-3">Required Skills</h5>
                      <div className="flex flex-wrap gap-2">
                        {role.required_skills
                          .sort((a, b) => b.importance - a.importance)
                          .slice(0, 8)
                          .map((skillObj, idx) => (
                            <div
                              key={idx}
                              className="flex items-center space-x-2 px-3 py-1.5 bg-gray-100 rounded-full"
                            >
                              <span className="text-sm font-medium text-gray-800">
                                {skillObj.skill}
                              </span>
                              <span className={`text-xs px-1.5 py-0.5 rounded ${
                                skillObj.importance >= 90 ? 'bg-red-200 text-red-800' :
                                skillObj.importance >= 75 ? 'bg-orange-200 text-orange-800' :
                                'bg-blue-200 text-blue-800'
                              }`}>
                                {skillObj.importance}
                              </span>
                            </div>
                          ))}
                      </div>
                    </div>
                  )}

                  {/* Career Progression */}
                  {role.next_roles && role.next_roles.length > 0 && (
                    <div>
                      <h5 className="text-sm font-semibold text-gray-900 mb-3 flex items-center space-x-2">
                        <Award className="w-4 h-4 text-indigo-600" />
                        <span>Career Progression</span>
                      </h5>
                      <div className="flex flex-wrap gap-2">
                        {role.next_roles.map((nextRole, idx) => (
                          <span
                            key={idx}
                            className="px-3 py-1.5 bg-indigo-50 text-indigo-700 text-sm font-medium rounded-lg border border-indigo-200"
                          >
                            → {nextRole}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}

        {/* Show More/Less Button */}
        {career_roles.length > 3 && (
          <button
            onClick={() => setShowAllRoles(!showAllRoles)}
            className="w-full mt-2 py-2 text-sm font-medium text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 rounded-lg transition-colors"
          >
            {showAllRoles
              ? `Show Less`
              : `Show ${career_roles.length - 3} More Role${career_roles.length - 3 > 1 ? 's' : ''}`
            }
          </button>
        )}
      </div>

      {/* Career Progression Path */}
      {career_progression && career_progression.length > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <Target className="w-5 h-5 text-indigo-600" />
            <span>Typical Career Progression</span>
          </h3>
          <div className="flex items-center space-x-2 overflow-x-auto pb-2">
            {career_progression.map((role, idx) => (
              <React.Fragment key={idx}>
                <div className="flex items-center space-x-2 bg-gradient-to-r from-indigo-50 to-indigo-100 px-4 py-2 rounded-lg border border-indigo-200 whitespace-nowrap">
                  <span className="text-xs font-bold text-indigo-700">{idx + 1}</span>
                  <span className="text-sm font-medium text-indigo-900">{role}</span>
                </div>
                {idx < career_progression.length - 1 && (
                  <div className="text-indigo-400 font-bold">→</div>
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
      )}

      {/* Data Freshness Indicator */}
      {careerInsights.last_updated && (
        <div className="mt-6 text-xs text-gray-500 text-center">
          Career data last updated: {new Date(careerInsights.last_updated).toLocaleDateString()}
        </div>
      )}
    </div>
  );
};

export default CareerInsightsPanel;
