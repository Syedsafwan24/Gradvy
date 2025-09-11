'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  MapPin, 
  Users, 
  Building,
  Calendar,
  Filter,
  ExternalLink,
  Briefcase,
  Star,
  AlertCircle,
  BarChart3,
  PieChart
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';

const MarketInsights = () => {
  const [selectedLocation, setSelectedLocation] = useState('us');
  const [selectedRole, setSelectedRole] = useState('all');

  const marketData = {
    overview: {
      totalJobs: 125000,
      avgSalary: '$89,000',
      growthRate: '+15%',
      demandScore: 8.7
    },
    salaryTrends: [
      { role: 'Full Stack Developer', salary: '$95,000', growth: '+12%', demand: 'Very High' },
      { role: 'DevOps Engineer', salary: '$120,000', growth: '+25%', demand: 'Very High' },
      { role: 'Frontend Developer', salary: '$85,000', growth: '+10%', demand: 'High' },
      { role: 'Backend Developer', salary: '$92,000', growth: '+15%', demand: 'High' },
      { role: 'Mobile Developer', salary: '$88,000', growth: '+8%', demand: 'Medium' },
      { role: 'Data Scientist', salary: '$110,000', growth: '+20%', demand: 'High' }
    ],
    skillDemand: [
      { skill: 'JavaScript', demand: 95, growth: '+18%', jobs: 45000 },
      { skill: 'Python', demand: 90, growth: '+22%', jobs: 38000 },
      { skill: 'React', demand: 85, growth: '+15%', jobs: 32000 },
      { skill: 'AWS', demand: 88, growth: '+28%', jobs: 28000 },
      { skill: 'Docker', demand: 75, growth: '+25%', jobs: 22000 },
      { skill: 'TypeScript', demand: 72, growth: '+30%', jobs: 18000 },
      { skill: 'Kubernetes', demand: 70, growth: '+35%', jobs: 15000 },
      { skill: 'Node.js', demand: 78, growth: '+12%', jobs: 25000 }
    ],
    locations: [
      { city: 'San Francisco', avgSalary: '$140,000', jobs: 15000, costOfLiving: 'Very High' },
      { city: 'New York', avgSalary: '$125,000', jobs: 18000, costOfLiving: 'Very High' },
      { city: 'Seattle', avgSalary: '$115,000', jobs: 12000, costOfLiving: 'High' },
      { city: 'Austin', avgSalary: '$95,000', jobs: 8000, costOfLiving: 'Medium' },
      { city: 'Denver', avgSalary: '$90,000', jobs: 6000, costOfLiving: 'Medium' },
      { city: 'Remote', avgSalary: '$85,000', jobs: 25000, costOfLiving: 'Variable' }
    ],
    companies: [
      { name: 'Google', jobs: 1200, avgSalary: '$150,000', rating: 4.4 },
      { name: 'Microsoft', jobs: 980, avgSalary: '$140,000', rating: 4.3 },
      { name: 'Amazon', jobs: 1500, avgSalary: '$135,000', rating: 3.9 },
      { name: 'Meta', jobs: 800, avgSalary: '$155,000', rating: 4.1 },
      { name: 'Apple', jobs: 600, avgSalary: '$145,000', rating: 4.2 },
      { name: 'Netflix', jobs: 300, avgSalary: '$160,000', rating: 4.3 }
    ],
    trends: [
      {
        title: 'AI/ML Skills in High Demand',
        description: 'Machine learning and AI skills are seeing unprecedented growth',
        impact: 'Very High',
        timeframe: 'Next 12 months'
      },
      {
        title: 'Remote Work Becoming Standard',
        description: 'More companies offering fully remote positions',
        impact: 'High',
        timeframe: 'Ongoing'
      },
      {
        title: 'Cloud Infrastructure Growth',
        description: 'DevOps and cloud skills are critical for modern applications',
        impact: 'High',
        timeframe: 'Next 6 months'
      },
      {
        title: 'JavaScript Frameworks Evolution',
        description: 'Next.js and modern React patterns gaining traction',
        impact: 'Medium',
        timeframe: 'Next 18 months'
      }
    ]
  };

  const getDemandColor = (demand) => {
    if (typeof demand === 'string') {
      switch (demand) {
        case 'Very High': return 'bg-red-100 text-red-700 border-red-200';
        case 'High': return 'bg-orange-100 text-orange-700 border-orange-200';
        case 'Medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
        default: return 'bg-gray-100 text-gray-700 border-gray-200';
      }
    }
    if (demand >= 80) return 'text-red-600';
    if (demand >= 60) return 'text-orange-600';
    return 'text-yellow-600';
  };

  const getGrowthColor = (growth) => {
    const value = parseInt(growth.replace('%', '').replace('+', ''));
    if (value >= 20) return 'text-green-600';
    if (value >= 10) return 'text-blue-600';
    return 'text-gray-600';
  };

  const getCostOfLivingColor = (cost) => {
    switch (cost) {
      case 'Very High': return 'bg-red-100 text-red-700';
      case 'High': return 'bg-orange-100 text-orange-700';
      case 'Medium': return 'bg-yellow-100 text-yellow-700';
      case 'Low': return 'bg-green-100 text-green-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between space-y-4 lg:space-y-0">
        <div>
          <h2 className="text-2xl font-bold">Market Insights</h2>
          <p className="text-gray-600">Stay informed about job market trends and opportunities</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Select value={selectedLocation} onValueChange={setSelectedLocation}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="us">United States</SelectItem>
              <SelectItem value="ca">Canada</SelectItem>
              <SelectItem value="uk">United Kingdom</SelectItem>
              <SelectItem value="de">Germany</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" size="sm">
            <Calendar className="h-4 w-4 mr-2" />
            Last Updated: Today
          </Button>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Job Openings</p>
              <p className="text-2xl font-bold">{marketData.overview.totalJobs.toLocaleString()}</p>
            </div>
            <Briefcase className="h-8 w-8 text-blue-500" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Average Salary</p>
              <p className="text-2xl font-bold">{marketData.overview.avgSalary}</p>
            </div>
            <DollarSign className="h-8 w-8 text-green-500" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Market Growth</p>
              <p className="text-2xl font-bold text-green-600">{marketData.overview.growthRate}</p>
            </div>
            <TrendingUp className="h-8 w-8 text-green-500" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Demand Score</p>
              <p className="text-2xl font-bold">{marketData.overview.demandScore}/10</p>
            </div>
            <BarChart3 className="h-8 w-8 text-purple-500" />
          </div>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="salaries">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="salaries">Salaries</TabsTrigger>
          <TabsTrigger value="skills">Skills</TabsTrigger>
          <TabsTrigger value="locations">Locations</TabsTrigger>
          <TabsTrigger value="companies">Companies</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
        </TabsList>

        <TabsContent value="salaries" className="mt-6">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold">Salary Insights by Role</h3>
              <Button variant="outline" size="sm">
                <ExternalLink className="h-4 w-4 mr-2" />
                Salary Calculator
              </Button>
            </div>
            
            <div className="space-y-4">
              {marketData.salaryTrends.map((role, index) => (
                <motion.div
                  key={role.role}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:shadow-sm"
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h4 className="font-medium">{role.role}</h4>
                      <Badge className={getDemandColor(role.demand)}>
                        {role.demand}
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-6 text-sm text-gray-600">
                      <span className="flex items-center space-x-1">
                        <DollarSign className="h-4 w-4" />
                        <span className="font-medium">{role.salary}</span>
                      </span>
                      <span className={`flex items-center space-x-1 ${getGrowthColor(role.growth)}`}>
                        <TrendingUp className="h-4 w-4" />
                        <span className="font-medium">{role.growth}</span>
                      </span>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">
                    View Jobs
                  </Button>
                </motion.div>
              ))}
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="skills" className="mt-6">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold">Most In-Demand Skills</h3>
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <span>Demand Score</span>
                <div className="w-4 h-4 bg-gradient-to-r from-yellow-400 to-red-500 rounded"></div>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {marketData.skillDemand.map((skill, index) => (
                <motion.div
                  key={skill.skill}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 border border-gray-200 rounded-lg"
                >
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium">{skill.skill}</h4>
                    <Badge variant="outline">
                      {skill.jobs.toLocaleString()} jobs
                    </Badge>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Market Demand</span>
                      <span className={`font-medium ${getDemandColor(skill.demand)}`}>
                        {skill.demand}%
                      </span>
                    </div>
                    <Progress value={skill.demand} className="h-2" />
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <span>Growth Rate</span>
                      <span className={`font-medium ${getGrowthColor(skill.growth)}`}>
                        {skill.growth}
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="locations" className="mt-6">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold">Top Tech Locations</h3>
              <Button variant="outline" size="sm">
                <MapPin className="h-4 w-4 mr-2" />
                Location Compare
              </Button>
            </div>
            
            <div className="space-y-4">
              {marketData.locations.map((location, index) => (
                <motion.div
                  key={location.city}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h4 className="font-medium text-lg">{location.city}</h4>
                      <Badge className={getCostOfLivingColor(location.costOfLiving)}>
                        {location.costOfLiving} COL
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-6 text-sm text-gray-600">
                      <span className="flex items-center space-x-1">
                        <DollarSign className="h-4 w-4" />
                        <span className="font-medium">{location.avgSalary}</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <Briefcase className="h-4 w-4" />
                        <span>{location.jobs.toLocaleString()} jobs</span>
                      </span>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">
                    <ExternalLink className="h-4 w-4" />
                  </Button>
                </motion.div>
              ))}
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="companies" className="mt-6">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold">Top Tech Companies</h3>
              <Button variant="outline" size="sm">
                <Building className="h-4 w-4 mr-2" />
                Company Insights
              </Button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {marketData.companies.map((company, index) => (
                <motion.div
                  key={company.name}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="p-4 hover:shadow-md transition-shadow">
                    <div className="text-center mb-4">
                      <h4 className="font-semibold text-lg">{company.name}</h4>
                      <div className="flex items-center justify-center space-x-1 mt-1">
                        <Star className="h-4 w-4 text-yellow-500 fill-current" />
                        <span className="text-sm text-gray-600">{company.rating}</span>
                      </div>
                    </div>
                    
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Open Positions</span>
                        <span className="font-medium">{company.jobs.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Avg Salary</span>
                        <span className="font-medium text-green-600">{company.avgSalary}</span>
                      </div>
                    </div>
                    
                    <Button className="w-full mt-4" size="sm">
                      View Jobs
                    </Button>
                  </Card>
                </motion.div>
              ))}
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="trends" className="mt-6">
          <div className="space-y-4">
            {marketData.trends.map((trend, index) => (
              <motion.div
                key={trend.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="font-semibold text-lg">{trend.title}</h3>
                        <Badge className={getDemandColor(trend.impact)}>
                          {trend.impact} Impact
                        </Badge>
                      </div>
                      <p className="text-gray-600 mb-3">{trend.description}</p>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span className="flex items-center space-x-1">
                          <Calendar className="h-4 w-4" />
                          <span>{trend.timeframe}</span>
                        </span>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" className="ml-4">
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default MarketInsights;