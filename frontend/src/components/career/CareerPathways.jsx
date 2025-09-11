'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Code, 
  Palette, 
  Server, 
  Database, 
  Shield, 
  BarChart3,
  Smartphone,
  Cloud,
  ChevronRight,
  Star,
  Clock,
  DollarSign,
  TrendingUp,
  Users
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

const CareerPathways = () => {
  const [selectedPath, setSelectedPath] = useState(null);

  const careerPaths = [
    {
      id: 'frontend',
      title: 'Frontend Developer',
      icon: Palette,
      description: 'Create beautiful, interactive user interfaces',
      demandLevel: 'High',
      avgSalary: '$75,000 - $120,000',
      growthRate: '+15%',
      timeToLearn: '6-12 months',
      skills: ['HTML/CSS', 'JavaScript', 'React', 'Vue.js', 'TypeScript', 'SASS/SCSS'],
      roadmap: [
        { title: 'HTML & CSS Fundamentals', duration: '2-4 weeks', completed: true },
        { title: 'JavaScript ES6+', duration: '4-6 weeks', completed: true },
        { title: 'React.js Framework', duration: '6-8 weeks', completed: false },
        { title: 'State Management (Redux)', duration: '3-4 weeks', completed: false },
        { title: 'Testing (Jest, Cypress)', duration: '3-4 weeks', completed: false },
        { title: 'Build Tools & Deployment', duration: '2-3 weeks', completed: false }
      ],
      companies: ['Google', 'Meta', 'Netflix', 'Airbnb', 'Uber'],
      pros: ['Creative work', 'High demand', 'Remote opportunities', 'Quick feedback'],
      cons: ['Fast-changing technologies', 'Browser compatibility', 'Design constraints']
    },
    {
      id: 'backend',
      title: 'Backend Developer',
      icon: Server,
      description: 'Build robust server-side applications and APIs',
      demandLevel: 'Very High',
      avgSalary: '$80,000 - $130,000',
      growthRate: '+18%',
      timeToLearn: '8-15 months',
      skills: ['Python/Java/Node.js', 'Databases', 'APIs', 'Cloud Services', 'Security', 'Testing'],
      roadmap: [
        { title: 'Programming Language (Python/Java)', duration: '6-8 weeks', completed: true },
        { title: 'Database Design (SQL/NoSQL)', duration: '4-6 weeks', completed: false },
        { title: 'API Development (REST/GraphQL)', duration: '4-5 weeks', completed: false },
        { title: 'Authentication & Security', duration: '3-4 weeks', completed: false },
        { title: 'Cloud Platforms (AWS/GCP)', duration: '6-8 weeks', completed: false },
        { title: 'Microservices Architecture', duration: '5-6 weeks', completed: false }
      ],
      companies: ['Amazon', 'Microsoft', 'Google', 'Stripe', 'Spotify'],
      pros: ['High salaries', 'Job security', 'System thinking', 'Scalability challenges'],
      cons: ['Complex debugging', 'Less visual feedback', 'On-call responsibilities']
    },
    {
      id: 'fullstack',
      title: 'Full Stack Developer',
      icon: Code,
      description: 'Master both frontend and backend development',
      demandLevel: 'Very High',
      avgSalary: '$85,000 - $140,000',
      growthRate: '+20%',
      timeToLearn: '12-18 months',
      skills: ['Frontend Frameworks', 'Backend Languages', 'Databases', 'DevOps', 'System Design'],
      roadmap: [
        { title: 'Frontend Mastery', duration: '8-10 weeks', completed: true },
        { title: 'Backend Development', duration: '10-12 weeks', completed: false },
        { title: 'Database Design', duration: '4-6 weeks', completed: false },
        { title: 'DevOps & Deployment', duration: '6-8 weeks', completed: false },
        { title: 'System Design', duration: '8-10 weeks', completed: false },
        { title: 'Advanced Architecture', duration: '6-8 weeks', completed: false }
      ],
      companies: ['Startup Ecosystem', 'Medium Companies', 'Tech Consultancies', 'Digital Agencies'],
      pros: ['Complete ownership', 'Higher salaries', 'Startup opportunities', 'Versatile skill set'],
      cons: ['Broad knowledge requirement', 'Keeping up with trends', 'Context switching']
    },
    {
      id: 'mobile',
      title: 'Mobile Developer',
      icon: Smartphone,
      description: 'Create mobile apps for iOS and Android',
      demandLevel: 'High',
      avgSalary: '$70,000 - $125,000',
      growthRate: '+12%',
      timeToLearn: '8-12 months',
      skills: ['React Native/Flutter', 'Swift/Kotlin', 'Mobile UI/UX', 'App Store Guidelines'],
      roadmap: [
        { title: 'Mobile Development Basics', duration: '4-6 weeks', completed: false },
        { title: 'React Native/Flutter', duration: '8-10 weeks', completed: false },
        { title: 'Native Features Integration', duration: '6-8 weeks', completed: false },
        { title: 'App Store Deployment', duration: '2-3 weeks', completed: false },
        { title: 'Performance Optimization', duration: '4-5 weeks', completed: false }
      ],
      companies: ['Apple', 'Google', 'Meta', 'Spotify', 'Instagram'],
      pros: ['Growing market', 'User impact', 'App store revenue', 'Cross-platform skills'],
      cons: ['Platform restrictions', 'Device fragmentation', 'App store approval']
    },
    {
      id: 'devops',
      title: 'DevOps Engineer',
      icon: Cloud,
      description: 'Bridge development and operations for scalable systems',
      demandLevel: 'Very High',
      avgSalary: '$90,000 - $150,000',
      growthRate: '+25%',
      timeToLearn: '10-15 months',
      skills: ['Docker', 'Kubernetes', 'AWS/Azure', 'CI/CD', 'Infrastructure as Code', 'Monitoring'],
      roadmap: [
        { title: 'Linux & Command Line', duration: '3-4 weeks', completed: false },
        { title: 'Docker Containerization', duration: '4-6 weeks', completed: false },
        { title: 'Cloud Platforms', duration: '8-10 weeks', completed: false },
        { title: 'CI/CD Pipelines', duration: '6-8 weeks', completed: false },
        { title: 'Kubernetes Orchestration', duration: '8-10 weeks', completed: false },
        { title: 'Monitoring & Observability', duration: '4-6 weeks', completed: false }
      ],
      companies: ['Netflix', 'Uber', 'Airbnb', 'Tesla', 'SpaceX'],
      pros: ['Highest salaries', 'Critical role', 'Automation focus', 'System-wide impact'],
      cons: ['High responsibility', 'Complex systems', 'On-call duties', 'Continuous learning']
    },
    {
      id: 'data',
      title: 'Data Scientist',
      icon: BarChart3,
      description: 'Extract insights from data using statistical methods and ML',
      demandLevel: 'High',
      avgSalary: '$85,000 - $140,000',
      growthRate: '+22%',
      timeToLearn: '12-18 months',
      skills: ['Python/R', 'Statistics', 'Machine Learning', 'SQL', 'Data Visualization', 'Domain Knowledge'],
      roadmap: [
        { title: 'Statistics & Probability', duration: '6-8 weeks', completed: false },
        { title: 'Python for Data Science', duration: '8-10 weeks', completed: false },
        { title: 'Machine Learning Algorithms', duration: '10-12 weeks', completed: false },
        { title: 'Data Visualization', duration: '4-6 weeks', completed: false },
        { title: 'Deep Learning', duration: '8-10 weeks', completed: false },
        { title: 'MLOps & Deployment', duration: '6-8 weeks', completed: false }
      ],
      companies: ['Google', 'Meta', 'Netflix', 'Tesla', 'OpenAI'],
      pros: ['High impact decisions', 'Interdisciplinary work', 'Research opportunities', 'Future-focused'],
      cons: ['Math-heavy', 'Data quality issues', 'Business alignment', 'Reproducibility challenges']
    }
  ];

  const PathwayCard = ({ path, isSelected, onClick }) => {
    const Icon = path.icon;
    
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        whileHover={{ y: -5 }}
        className={`cursor-pointer transition-all ${isSelected ? 'ring-2 ring-blue-500' : ''}`}
        onClick={onClick}
      >
        <Card className="p-6 h-full hover:shadow-lg transition-shadow">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Icon className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">{path.title}</h3>
                <Badge className={
                  path.demandLevel === 'Very High' ? 'bg-red-100 text-red-700' :
                  path.demandLevel === 'High' ? 'bg-orange-100 text-orange-700' :
                  'bg-yellow-100 text-yellow-700'
                }>
                  {path.demandLevel} Demand
                </Badge>
              </div>
            </div>
            <ChevronRight className={`h-5 w-5 text-gray-400 transition-transform ${isSelected ? 'rotate-90' : ''}`} />
          </div>

          <p className="text-gray-600 mb-4">{path.description}</p>

          <div className="space-y-2 mb-4">
            <div className="flex items-center justify-between text-sm">
              <span className="flex items-center space-x-1">
                <DollarSign className="h-4 w-4 text-green-500" />
                <span>Salary</span>
              </span>
              <span className="font-medium">{path.avgSalary}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="flex items-center space-x-1">
                <TrendingUp className="h-4 w-4 text-blue-500" />
                <span>Growth</span>
              </span>
              <span className="font-medium text-green-600">{path.growthRate}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="flex items-center space-x-1">
                <Clock className="h-4 w-4 text-purple-500" />
                <span>Time to Learn</span>
              </span>
              <span className="font-medium">{path.timeToLearn}</span>
            </div>
          </div>

          <div className="flex flex-wrap gap-1 mb-4">
            {path.skills.slice(0, 3).map(skill => (
              <Badge key={skill} variant="secondary" className="text-xs">
                {skill}
              </Badge>
            ))}
            {path.skills.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{path.skills.length - 3} more
              </Badge>
            )}
          </div>

          <Button 
            className="w-full" 
            variant={isSelected ? "default" : "outline"}
          >
            {isSelected ? 'View Details' : 'Learn More'}
          </Button>
        </Card>
      </motion.div>
    );
  };

  const PathwayDetails = ({ path }) => {
    const completedSteps = path.roadmap.filter(step => step.completed).length;
    const progressPercentage = (completedSteps / path.roadmap.length) * 100;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mt-8"
      >
        <Card className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">Career Roadmap: {path.title}</h2>
            <Button>
              <Star className="h-4 w-4 mr-2" />
              Set as Goal
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Roadmap */}
            <div className="lg:col-span-2">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Learning Path</h3>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Progress:</span>
                  <span className="text-sm font-medium">{Math.round(progressPercentage)}%</span>
                </div>
              </div>

              <div className="space-y-4">
                {path.roadmap.map((step, index) => (
                  <div key={index} className="flex items-center space-x-4">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                      step.completed 
                        ? 'bg-green-500 text-white' 
                        : index === completedSteps
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 text-gray-600'
                    }`}>
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h4 className={`font-medium ${step.completed ? 'text-green-700' : ''}`}>
                          {step.title}
                        </h4>
                        <span className="text-sm text-gray-500">{step.duration}</span>
                      </div>
                      {step.completed && (
                        <p className="text-sm text-green-600">✓ Completed</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Details */}
            <div className="space-y-6">
              {/* Skills Required */}
              <div>
                <h3 className="font-semibold mb-3">Key Skills</h3>
                <div className="flex flex-wrap gap-2">
                  {path.skills.map(skill => (
                    <Badge key={skill} variant="outline">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>

              <Separator />

              {/* Companies */}
              <div>
                <h3 className="font-semibold mb-3">
                  <Users className="h-4 w-4 inline mr-2" />
                  Top Companies
                </h3>
                <div className="space-y-2">
                  {path.companies.map(company => (
                    <div key={company} className="text-sm text-gray-700">
                      • {company}
                    </div>
                  ))}
                </div>
              </div>

              <Separator />

              {/* Pros & Cons */}
              <div>
                <h3 className="font-semibold mb-3">Pros & Cons</h3>
                <div className="space-y-3">
                  <div>
                    <h4 className="text-sm font-medium text-green-700 mb-1">Pros:</h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {path.pros.map(pro => (
                        <li key={pro}>• {pro}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-red-700 mb-1">Cons:</h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {path.cons.map(con => (
                        <li key={con}>• {con}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              <Separator />

              <div className="space-y-2">
                <Button className="w-full">
                  Start Learning Path
                </Button>
                <Button variant="outline" className="w-full">
                  Find Courses
                </Button>
              </div>
            </div>
          </div>
        </Card>
      </motion.div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold mb-2">Choose Your Career Path</h2>
        <p className="text-gray-600">
          Explore different career paths in technology and find the one that matches your interests and goals.
        </p>
      </div>

      {/* Career Paths Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {careerPaths.map(path => (
          <PathwayCard
            key={path.id}
            path={path}
            isSelected={selectedPath?.id === path.id}
            onClick={() => setSelectedPath(selectedPath?.id === path.id ? null : path)}
          />
        ))}
      </div>

      {/* Selected Pathway Details */}
      {selectedPath && <PathwayDetails path={selectedPath} />}
    </div>
  );
};

export default CareerPathways;