'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Target, 
  Plus, 
  Calendar, 
  Clock,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Edit,
  Trash2,
  Play,
  Pause,
  Flag,
  BookOpen,
  Award,
  Users,
  ExternalLink
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const GoalTracker = ({ goals: initialGoals = [] }) => {
  const [goals, setGoals] = useState(initialGoals);
  const [showAddGoal, setShowAddGoal] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterPriority, setFilterPriority] = useState('all');

  const goalCategories = [
    { value: 'skill', label: 'Skill Development', icon: BookOpen },
    { value: 'certification', label: 'Certification', icon: Award },
    { value: 'career', label: 'Career Milestone', icon: TrendingUp },
    { value: 'project', label: 'Project', icon: Target },
    { value: 'networking', label: 'Networking', icon: Users }
  ];

  const priorities = [
    { value: 'high', label: 'High Priority', color: 'bg-red-100 text-red-700' },
    { value: 'medium', label: 'Medium Priority', color: 'bg-yellow-100 text-yellow-700' },
    { value: 'low', label: 'Low Priority', color: 'bg-green-100 text-green-700' }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-500';
      case 'in_progress': return 'bg-blue-500';
      case 'planned': return 'bg-gray-400';
      case 'paused': return 'bg-orange-500';
      default: return 'bg-gray-400';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return CheckCircle;
      case 'in_progress': return Play;
      case 'planned': return Clock;
      case 'paused': return Pause;
      default: return Clock;
    }
  };

  const getPriorityColor = (priority) => {
    const priorityObj = priorities.find(p => p.value === priority);
    return priorityObj?.color || 'bg-gray-100 text-gray-700';
  };

  const getDaysUntilDeadline = (deadline) => {
    const today = new Date();
    const deadlineDate = new Date(deadline);
    const diffTime = deadlineDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const filteredGoals = goals.filter(goal => {
    const statusMatch = filterStatus === 'all' || goal.status === filterStatus;
    const priorityMatch = filterPriority === 'all' || goal.priority === filterPriority;
    return statusMatch && priorityMatch;
  });

  const goalStats = {
    total: goals.length,
    completed: goals.filter(g => g.status === 'completed').length,
    inProgress: goals.filter(g => g.status === 'in_progress').length,
    planned: goals.filter(g => g.status === 'planned').length,
    overdue: goals.filter(g => {
      const daysUntil = getDaysUntilDeadline(g.deadline);
      return daysUntil < 0 && g.status !== 'completed';
    }).length
  };

  const AddGoalModal = () => {
    const [newGoal, setNewGoal] = useState({
      title: '',
      description: '',
      category: 'skill',
      priority: 'medium',
      deadline: '',
      milestones: []
    });

    const handleSubmit = () => {
      const goal = {
        ...newGoal,
        id: Date.now(),
        progress: 0,
        status: 'planned',
        createdAt: new Date().toISOString()
      };
      setGoals([...goals, goal]);
      setShowAddGoal(false);
      setNewGoal({
        title: '',
        description: '',
        category: 'skill',
        priority: 'medium',
        deadline: '',
        milestones: []
      });
    };

    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      >
        <motion.div
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          className="bg-white rounded-lg p-6 w-full max-w-md mx-4"
        >
          <h3 className="text-lg font-semibold mb-4">Add New Goal</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Goal Title</label>
              <Input
                value={newGoal.title}
                onChange={(e) => setNewGoal({ ...newGoal, title: e.target.value })}
                placeholder="Enter goal title..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Description</label>
              <Textarea
                value={newGoal.description}
                onChange={(e) => setNewGoal({ ...newGoal, description: e.target.value })}
                placeholder="Describe your goal..."
                className="min-h-[80px]"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Category</label>
                <Select 
                  value={newGoal.category} 
                  onValueChange={(value) => setNewGoal({ ...newGoal, category: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {goalCategories.map(category => (
                      <SelectItem key={category.value} value={category.value}>
                        {category.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Priority</label>
                <Select 
                  value={newGoal.priority} 
                  onValueChange={(value) => setNewGoal({ ...newGoal, priority: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {priorities.map(priority => (
                      <SelectItem key={priority.value} value={priority.value}>
                        {priority.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Target Deadline</label>
              <Input
                type="date"
                value={newGoal.deadline}
                onChange={(e) => setNewGoal({ ...newGoal, deadline: e.target.value })}
              />
            </div>
          </div>
          
          <div className="flex justify-end space-x-2 mt-6">
            <Button variant="outline" onClick={() => setShowAddGoal(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={!newGoal.title}>
              Create Goal
            </Button>
          </div>
        </motion.div>
      </motion.div>
    );
  };

  const GoalCard = ({ goal }) => {
    const StatusIcon = getStatusIcon(goal.status);
    const daysUntilDeadline = getDaysUntilDeadline(goal.deadline);
    const isOverdue = daysUntilDeadline < 0 && goal.status !== 'completed';
    const categoryInfo = goalCategories.find(c => c.value === goal.category);
    const CategoryIcon = categoryInfo?.icon || Target;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        whileHover={{ y: -2 }}
        className="group"
      >
        <Card className="p-6 hover:shadow-lg transition-all">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-start space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <CategoryIcon className="h-5 w-5 text-blue-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-lg mb-1">{goal.title}</h3>
                <p className="text-gray-600 text-sm mb-2">{goal.description}</p>
                <div className="flex items-center space-x-2">
                  <Badge className={getPriorityColor(goal.priority)}>
                    {goal.priority} priority
                  </Badge>
                  <Badge variant="outline">
                    {categoryInfo?.label}
                  </Badge>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <Edit className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-red-600">
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Progress */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Progress</span>
              <span className="text-sm text-gray-600">{goal.progress}%</span>
            </div>
            <Progress value={goal.progress} className="h-2" />
          </div>

          {/* Status and Deadline */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <StatusIcon className={`h-4 w-4 ${getStatusColor(goal.status).replace('bg-', 'text-')}`} />
              <span className="text-sm capitalize">{goal.status.replace('_', ' ')}</span>
            </div>
            
            <div className="flex items-center space-x-2 text-sm">
              {isOverdue ? (
                <div className="flex items-center space-x-1 text-red-600">
                  <AlertCircle className="h-4 w-4" />
                  <span>Overdue by {Math.abs(daysUntilDeadline)} days</span>
                </div>
              ) : daysUntilDeadline <= 7 && goal.status !== 'completed' ? (
                <div className="flex items-center space-x-1 text-orange-600">
                  <Clock className="h-4 w-4" />
                  <span>{daysUntilDeadline} days left</span>
                </div>
              ) : (
                <div className="flex items-center space-x-1 text-gray-600">
                  <Calendar className="h-4 w-4" />
                  <span>{new Date(goal.deadline).toLocaleDateString()}</span>
                </div>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="mt-4 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {goal.status === 'planned' && (
                <Button size="sm" variant="outline">
                  <Play className="h-3 w-3 mr-1" />
                  Start
                </Button>
              )}
              {goal.status === 'in_progress' && (
                <Button size="sm" variant="outline">
                  <Pause className="h-3 w-3 mr-1" />
                  Pause
                </Button>
              )}
              {goal.status !== 'completed' && (
                <Button size="sm" variant="outline">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Complete
                </Button>
              )}
            </div>
            
            <Button variant="ghost" size="sm">
              <ExternalLink className="h-3 w-3" />
            </Button>
          </div>
        </Card>
      </motion.div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between space-y-4 lg:space-y-0">
        <div>
          <h2 className="text-2xl font-bold">Goal Tracker</h2>
          <p className="text-gray-600">Track your career and learning objectives</p>
        </div>
        
        <Button onClick={() => setShowAddGoal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Goal
        </Button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-gray-900">{goalStats.total}</div>
          <div className="text-sm text-gray-600">Total Goals</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-green-600">{goalStats.completed}</div>
          <div className="text-sm text-gray-600">Completed</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-blue-600">{goalStats.inProgress}</div>
          <div className="text-sm text-gray-600">In Progress</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-gray-600">{goalStats.planned}</div>
          <div className="text-sm text-gray-600">Planned</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-red-600">{goalStats.overdue}</div>
          <div className="text-sm text-gray-600">Overdue</div>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="planned">Planned</SelectItem>
            <SelectItem value="in_progress">In Progress</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="paused">Paused</SelectItem>
          </SelectContent>
        </Select>

        <Select value={filterPriority} onValueChange={setFilterPriority}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="Filter by priority" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Priorities</SelectItem>
            <SelectItem value="high">High Priority</SelectItem>
            <SelectItem value="medium">Medium Priority</SelectItem>
            <SelectItem value="low">Low Priority</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Goals Content */}
      <Tabs defaultValue="active">
        <TabsList>
          <TabsTrigger value="active">Active Goals</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
          <TabsTrigger value="templates">Goal Templates</TabsTrigger>
        </TabsList>

        <TabsContent value="active" className="mt-6">
          {filteredGoals.filter(goal => goal.status !== 'completed').length === 0 ? (
            <Card className="p-12 text-center">
              <Target className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Active Goals</h3>
              <p className="text-gray-600 mb-6">Start by creating your first career goal.</p>
              <Button onClick={() => setShowAddGoal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Create Your First Goal
              </Button>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredGoals
                .filter(goal => goal.status !== 'completed')
                .map(goal => (
                  <GoalCard key={goal.id} goal={goal} />
                ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="completed" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredGoals
              .filter(goal => goal.status === 'completed')
              .map(goal => (
                <GoalCard key={goal.id} goal={goal} />
              ))}
          </div>
        </TabsContent>

        <TabsContent value="templates" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card className="p-6 border-dashed border-2 border-gray-300 hover:border-blue-400 cursor-pointer transition-colors">
              <div className="text-center">
                <BookOpen className="h-8 w-8 text-gray-400 mx-auto mb-3" />
                <h3 className="font-semibold mb-2">Learn New Technology</h3>
                <p className="text-sm text-gray-600 mb-4">Master a new programming language or framework</p>
                <Button variant="outline" size="sm">Use Template</Button>
              </div>
            </Card>
            
            <Card className="p-6 border-dashed border-2 border-gray-300 hover:border-blue-400 cursor-pointer transition-colors">
              <div className="text-center">
                <Award className="h-8 w-8 text-gray-400 mx-auto mb-3" />
                <h3 className="font-semibold mb-2">Get Certified</h3>
                <p className="text-sm text-gray-600 mb-4">Earn a professional certification</p>
                <Button variant="outline" size="sm">Use Template</Button>
              </div>
            </Card>
            
            <Card className="p-6 border-dashed border-2 border-gray-300 hover:border-blue-400 cursor-pointer transition-colors">
              <div className="text-center">
                <TrendingUp className="h-8 w-8 text-gray-400 mx-auto mb-3" />
                <h3 className="font-semibold mb-2">Career Advancement</h3>
                <p className="text-sm text-gray-600 mb-4">Get promoted to the next level</p>
                <Button variant="outline" size="sm">Use Template</Button>
              </div>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Add Goal Modal */}
      {showAddGoal && <AddGoalModal />}
    </div>
  );
};

export default GoalTracker;