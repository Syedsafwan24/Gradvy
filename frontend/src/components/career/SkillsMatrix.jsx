'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Plus, 
  Search, 
  Filter, 
  TrendingUp, 
  Target,
  Star,
  BookOpen,
  Award,
  BarChart3,
  Edit,
  Trash2,
  ExternalLink
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const SkillsMatrix = ({ skills = [], skillsByCategory = {} }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'radar'
  const [showAddSkill, setShowAddSkill] = useState(false);

  // Popular skills suggestions
  const popularSkills = [
    { name: 'Python', category: 'Programming', demand: 'Very High' },
    { name: 'JavaScript', category: 'Programming', demand: 'Very High' },
    { name: 'React', category: 'Frontend', demand: 'High' },
    { name: 'TypeScript', category: 'Programming', demand: 'High' },
    { name: 'Next.js', category: 'Frontend', demand: 'High' },
    { name: 'AWS', category: 'Cloud', demand: 'Very High' },
    { name: 'Docker', category: 'DevOps', demand: 'High' },
    { name: 'Kubernetes', category: 'DevOps', demand: 'High' },
    { name: 'PostgreSQL', category: 'Database', demand: 'High' },
    { name: 'MongoDB', category: 'Database', demand: 'Medium' },
    { name: 'GraphQL', category: 'Backend', demand: 'Medium' },
    { name: 'Machine Learning', category: 'AI/ML', demand: 'Very High' }
  ];

  const categories = [
    { id: 'all', name: 'All Skills', count: skills.length },
    ...Object.entries(skillsByCategory).map(([category, skillsInCategory]) => ({
      id: category.toLowerCase(),
      name: category,
      count: skillsInCategory.length
    }))
  ];

  const getSkillColor = (level) => {
    if (level >= 80) return 'bg-green-500';
    if (level >= 60) return 'bg-blue-500';
    if (level >= 40) return 'bg-yellow-500';
    return 'bg-gray-400';
  };

  const getSkillLabel = (level) => {
    if (level >= 90) return 'Expert';
    if (level >= 75) return 'Advanced';
    if (level >= 50) return 'Intermediate';
    if (level >= 25) return 'Beginner';
    return 'Learning';
  };

  const getDemandColor = (demand) => {
    switch (demand) {
      case 'Very High': return 'bg-red-100 text-red-700';
      case 'High': return 'bg-orange-100 text-orange-700';
      case 'Medium': return 'bg-yellow-100 text-yellow-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const filteredSkills = skills.filter(skill => {
    const matchesSearch = skill.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || skill.category.toLowerCase() === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const skillLevels = {
    beginner: skills.filter(s => s.level < 25).length,
    intermediate: skills.filter(s => s.level >= 25 && s.level < 75).length,
    advanced: skills.filter(s => s.level >= 75).length
  };

  const SkillCard = ({ skill }) => (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ y: -2 }}
      className="group"
    >
      <Card className="p-4 hover:shadow-md transition-all">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h3 className="font-semibold text-lg">{skill.name}</h3>
            <Badge className={`text-xs ${getSkillCategoryColor(skill.category)}`}>
              {skill.category}
            </Badge>
          </div>
          <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
              <Edit className="h-3 w-3" />
            </Button>
            <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-red-600 hover:text-red-700">
              <Trash2 className="h-3 w-3" />
            </Button>
          </div>
        </div>

        <div className="space-y-2 mb-3">
          <div className="flex items-center justify-between text-sm">
            <span>Proficiency</span>
            <span className="font-medium">{skill.level}% • {getSkillLabel(skill.level)}</span>
          </div>
          <Progress value={skill.level} className="h-2" />
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <TrendingUp className="h-4 w-4 text-green-500" />
            <span className="text-sm text-gray-600">In demand</span>
          </div>
          <Button variant="outline" size="sm">
            <BookOpen className="h-3 w-3 mr-1" />
            Learn
          </Button>
        </div>
      </Card>
    </motion.div>
  );

  const getSkillCategoryColor = (category) => {
    const colors = {
      'Programming': 'bg-blue-100 text-blue-700',
      'Frontend': 'bg-green-100 text-green-700',
      'Backend': 'bg-purple-100 text-purple-700',
      'Database': 'bg-yellow-100 text-yellow-700',
      'Tools': 'bg-gray-100 text-gray-700',
      'Cloud': 'bg-indigo-100 text-indigo-700',
      'DevOps': 'bg-red-100 text-red-700',
      'AI/ML': 'bg-pink-100 text-pink-700'
    };
    return colors[category] || 'bg-gray-100 text-gray-700';
  };

  const AddSkillModal = () => (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <motion.div
        initial={{ scale: 0.9 }}
        animate={{ scale: 1 }}
        className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Add New Skill</h3>
          <Button variant="ghost" size="sm" onClick={() => setShowAddSkill(false)}>
            ×
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium mb-3">Popular Skills</h4>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {popularSkills.map(skill => (
                <div key={skill.name} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <div>
                    <div className="font-medium">{skill.name}</div>
                    <div className="flex items-center space-x-2 text-sm">
                      <Badge className={getSkillCategoryColor(skill.category)}>
                        {skill.category}
                      </Badge>
                      <Badge className={getDemandColor(skill.demand)}>
                        {skill.demand}
                      </Badge>
                    </div>
                  </div>
                  <Button size="sm">Add</Button>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-medium mb-3">Custom Skill</h4>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Skill Name</label>
                <Input placeholder="Enter skill name..." />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Category</label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="programming">Programming</SelectItem>
                    <SelectItem value="frontend">Frontend</SelectItem>
                    <SelectItem value="backend">Backend</SelectItem>
                    <SelectItem value="database">Database</SelectItem>
                    <SelectItem value="cloud">Cloud</SelectItem>
                    <SelectItem value="devops">DevOps</SelectItem>
                    <SelectItem value="ai/ml">AI/ML</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Current Level</label>
                <div className="space-y-2">
                  <input type="range" min="0" max="100" defaultValue="50" className="w-full" />
                  <div className="text-sm text-gray-600 text-center">Intermediate (50%)</div>
                </div>
              </div>
              <Button className="w-full">Add Custom Skill</Button>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );

  return (
    <div className="space-y-6">
      {/* Header & Stats */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between space-y-4 lg:space-y-0">
        <div>
          <h2 className="text-2xl font-bold">Skills Matrix</h2>
          <p className="text-gray-600">Track and develop your technical skills</p>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-4 text-sm">
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-gray-400 rounded"></div>
              <span>Learning ({skillLevels.beginner})</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-yellow-500 rounded"></div>
              <span>Intermediate ({skillLevels.intermediate})</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-green-500 rounded"></div>
              <span>Advanced ({skillLevels.advanced})</span>
            </div>
          </div>
          <Button onClick={() => setShowAddSkill(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Skill
          </Button>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search skills..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={selectedCategory} onValueChange={setSelectedCategory}>
          <SelectTrigger className="w-48">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {categories.map(category => (
              <SelectItem key={category.id} value={category.id}>
                {category.name} ({category.count})
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <div className="flex items-center bg-gray-100 rounded-lg p-1">
          <Button
            variant={viewMode === 'grid' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('grid')}
          >
            Grid
          </Button>
          <Button
            variant={viewMode === 'chart' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('chart')}
          >
            Chart
          </Button>
        </div>
      </div>

      {/* Skills Content */}
      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="assessment">Assessment</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-6">
          {viewMode === 'grid' ? (
            // Skills Grid
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filteredSkills.map(skill => (
                <SkillCard key={skill.name} skill={skill} />
              ))}
            </div>
          ) : (
            // Skills by Category
            <div className="space-y-6">
              {Object.entries(skillsByCategory).map(([category, categorySkills]) => (
                <Card key={category} className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold">{category}</h3>
                    <Badge className={getSkillCategoryColor(category)}>
                      {categorySkills.length} skills
                    </Badge>
                  </div>
                  <div className="space-y-3">
                    {categorySkills.map(skill => (
                      <div key={skill.name} className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-medium">{skill.name}</span>
                            <span className="text-sm text-gray-600">{skill.level}%</span>
                          </div>
                          <Progress value={skill.level} className="h-2" />
                        </div>
                        <div className="ml-4 flex items-center space-x-1">
                          <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
                            <BookOpen className="h-3 w-3" />
                          </Button>
                          <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
                            <Edit className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="assessment" className="mt-6">
          <Card className="p-6">
            <div className="text-center py-12">
              <Target className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Skills Assessment</h3>
              <p className="text-gray-600 mb-6">
                Take our comprehensive skills assessment to get personalized recommendations
              </p>
              <Button size="lg">
                <Award className="h-5 w-5 mr-2" />
                Start Assessment
              </Button>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="recommendations" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Trending Skills</h3>
              <div className="space-y-3">
                {popularSkills.slice(0, 6).map(skill => (
                  <div key={skill.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <div className="font-medium">{skill.name}</div>
                      <Badge className={getDemandColor(skill.demand)}>
                        {skill.demand} Demand
                      </Badge>
                    </div>
                    <Button variant="outline" size="sm">
                      Learn
                    </Button>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Skill Gaps</h3>
              <div className="space-y-3">
                <div className="p-3 border border-orange-200 bg-orange-50 rounded-lg">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium text-orange-800">Cloud Computing</h4>
                      <p className="text-sm text-orange-600">Essential for modern development</p>
                    </div>
                    <Button variant="outline" size="sm">
                      <ExternalLink className="h-3 w-3 mr-1" />
                      Courses
                    </Button>
                  </div>
                </div>
                <div className="p-3 border border-blue-200 bg-blue-50 rounded-lg">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium text-blue-800">System Design</h4>
                      <p className="text-sm text-blue-600">Critical for senior roles</p>
                    </div>
                    <Button variant="outline" size="sm">
                      <ExternalLink className="h-3 w-3 mr-1" />
                      Courses
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Add Skill Modal */}
      {showAddSkill && <AddSkillModal />}
    </div>
  );
};

export default SkillsMatrix;