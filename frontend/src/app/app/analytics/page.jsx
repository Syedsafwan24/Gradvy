'use client';

import { TrendingUp, Clock, Target, Award, BarChart3, Calendar } from 'lucide-react';
import PageLayout from '@/components/layouts/PageLayout';
import SectionCard from '@/components/layouts/SectionCard';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function AnalyticsPage() {
  // Mock data - replace with actual data from API
  const stats = [
    {
      title: 'Total Study Time',
      value: '42h 30m',
      change: '+12%',
      icon: Clock,
      trend: 'up'
    },
    {
      title: 'Completed Modules',
      value: '24',
      change: '+8',
      icon: Target,
      trend: 'up'
    },
    {
      title: 'Active Learning Paths',
      value: '3',
      change: 'Same',
      icon: BarChart3,
      trend: 'neutral'
    },
    {
      title: 'Achievements',
      value: '12',
      change: '+3',
      icon: Award,
      trend: 'up'
    }
  ];

  const recentActivity = [
    { date: '2024-01-15', action: 'Completed Module: JavaScript Basics', type: 'completed' },
    { date: '2024-01-14', action: 'Started Learning Path: Web Development', type: 'started' },
    { date: '2024-01-13', action: 'Earned Achievement: Quick Learner', type: 'achievement' },
    { date: '2024-01-12', action: 'Completed Assessment: React Fundamentals', type: 'assessment' },
  ];

  return (
    <PageLayout
      title="Analytics Dashboard"
      description="Insights into your learning patterns and progress"
    >
      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-6">
        {stats.map((stat, index) => (
          <Card key={index} className="p-4 sm:p-6 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <stat.icon className="w-5 h-5 text-primary" />
              </div>
              {stat.trend === 'up' && (
                <Badge variant="success" className="text-xs">
                  {stat.change}
                </Badge>
              )}
            </div>
            <h3 className="text-sm font-medium text-muted-foreground mb-1">
              {stat.title}
            </h3>
            <p className="text-2xl font-bold">{stat.value}</p>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
        {/* Learning Progress */}
        <div className="lg:col-span-2">
          <SectionCard title="Learning Progress">
            <div className="space-y-4">
              {/* Weekly Progress */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">This Week</span>
                  <span className="text-sm text-muted-foreground">8h 45m</span>
                </div>
                <div className="h-3 bg-muted rounded-full overflow-hidden">
                  <div className="h-full bg-primary w-3/4 rounded-full" />
                </div>
                <p className="text-xs text-muted-foreground mt-1">75% of weekly goal (12h)</p>
              </div>

              {/* Monthly Progress */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">This Month</span>
                  <span className="text-sm text-muted-foreground">42h 30m</span>
                </div>
                <div className="h-3 bg-muted rounded-full overflow-hidden">
                  <div className="h-full bg-success w-2/3 rounded-full" />
                </div>
                <p className="text-xs text-muted-foreground mt-1">68% of monthly goal (60h)</p>
              </div>

              {/* Learning Streak */}
              <div className="pt-4 border-t">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-warning/10 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-warning" />
                  </div>
                  <div>
                    <p className="font-semibold">7 Day Streak!</p>
                    <p className="text-sm text-muted-foreground">Keep up the great work</p>
                  </div>
                </div>
              </div>
            </div>
          </SectionCard>

          {/* Recent Activity */}
          <SectionCard title="Recent Activity" className="mt-4 sm:mt-6">
            <div className="space-y-3">
              {recentActivity.map((activity, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-muted rounded-lg">
                  <div className="p-2 bg-background rounded">
                    <Calendar className="w-4 h-4 text-muted-foreground" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{activity.action}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {new Date(activity.date).toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric', 
                        year: 'numeric' 
                      })}
                    </p>
                  </div>
                  <Badge 
                    variant={
                      activity.type === 'completed' ? 'success' :
                      activity.type === 'achievement' ? 'warning' :
                      'indigo'
                    }
                  >
                    {activity.type}
                  </Badge>
                </div>
              ))}
            </div>
          </SectionCard>
        </div>

        {/* Sidebar */}
        <div className="space-y-4 sm:space-y-6">
          {/* Top Categories */}
          <SectionCard title="Top Categories">
            <div className="space-y-3">
              {[
                { name: 'Web Development', hours: 18, color: 'indigo' },
                { name: 'Data Science', hours: 12, color: 'purple' },
                { name: 'Design', hours: 8, color: 'pink' }
              ].map((category, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{category.name}</span>
                    <span className="text-sm text-muted-foreground">{category.hours}h</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div 
                      className={`h-full bg-${category.color}-600 rounded-full`}
                      style={{ width: `${(category.hours / 18) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </SectionCard>

          {/* Achievements */}
          <SectionCard title="Recent Achievements">
            <div className="space-y-3">
              {[
                { name: 'Quick Learner', description: 'Complete 5 modules in a week' },
                { name: 'Dedicated', description: 'Maintain a 7-day streak' },
                { name: 'Knowledge Seeker', description: 'Finish 3 learning paths' }
              ].map((achievement, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-muted rounded-lg">
                  <div className="p-2 bg-warning/10 rounded">
                    <Award className="w-4 h-4 text-warning" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{achievement.name}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {achievement.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </SectionCard>
        </div>
      </div>
    </PageLayout>
  );
}