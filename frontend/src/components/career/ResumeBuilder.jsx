'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  FileText, 
  Download, 
  Eye, 
  Edit,
  Plus,
  Trash2,
  Copy,
  Share2,
  Settings,
  Layout,
  User,
  Briefcase,
  GraduationCap,
  Award,
  Code
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';

const ResumeBuilder = () => {
  const [activeTemplate, setActiveTemplate] = useState('modern');
  const [resumeData, setResumeData] = useState({
    personalInfo: {
      firstName: 'John',
      lastName: 'Doe',
      email: 'john.doe@email.com',
      phone: '+1 (555) 123-4567',
      location: 'San Francisco, CA',
      website: 'johndoe.dev',
      linkedin: 'linkedin.com/in/johndoe',
      github: 'github.com/johndoe'
    },
    summary: 'Passionate Full Stack Developer with 3+ years of experience building scalable web applications using modern technologies. Strong background in JavaScript, React, Node.js, and cloud platforms.',
    experience: [
      {
        id: 1,
        title: 'Senior Software Developer',
        company: 'TechCorp Inc.',
        location: 'San Francisco, CA',
        startDate: '2022-01',
        endDate: 'Present',
        current: true,
        description: '• Led development of microservices architecture serving 100K+ users\n• Improved application performance by 40% through optimization\n• Mentored 3 junior developers and conducted code reviews'
      },
      {
        id: 2,
        title: 'Frontend Developer',
        company: 'StartupXYZ',
        location: 'Remote',
        startDate: '2020-06',
        endDate: '2021-12',
        current: false,
        description: '• Built responsive web applications using React and TypeScript\n• Collaborated with design team to implement pixel-perfect UIs\n• Reduced bundle size by 30% through code splitting and optimization'
      }
    ],
    education: [
      {
        id: 1,
        degree: 'Bachelor of Science in Computer Science',
        school: 'University of California, Berkeley',
        location: 'Berkeley, CA',
        graduationDate: '2020-05'
      }
    ],
    skills: [
      'JavaScript', 'TypeScript', 'React', 'Node.js', 'Python', 'AWS', 'Docker', 'PostgreSQL'
    ],
    projects: [
      {
        id: 1,
        name: 'E-commerce Platform',
        description: 'Full-stack e-commerce application built with React, Node.js, and PostgreSQL',
        technologies: ['React', 'Node.js', 'PostgreSQL', 'Stripe'],
        link: 'github.com/johndoe/ecommerce'
      }
    ],
    certifications: [
      {
        id: 1,
        name: 'AWS Solutions Architect Associate',
        issuer: 'Amazon Web Services',
        date: '2023-03'
      }
    ]
  });

  const templates = [
    {
      id: 'modern',
      name: 'Modern Professional',
      preview: '/api/placeholder/300/400',
      description: 'Clean, modern design perfect for tech roles'
    },
    {
      id: 'creative',
      name: 'Creative Designer',
      preview: '/api/placeholder/300/400',
      description: 'Bold design for creative professionals'
    },
    {
      id: 'minimal',
      name: 'Minimal Clean',
      preview: '/api/placeholder/300/400',
      description: 'Minimalist design focusing on content'
    },
    {
      id: 'executive',
      name: 'Executive',
      preview: '/api/placeholder/300/400',
      description: 'Professional template for senior roles'
    }
  ];

  const ResumePreview = () => (
    <Card className="p-8 bg-white shadow-lg max-w-2xl mx-auto">
      {/* Header */}
      <div className="text-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">
          {resumeData.personalInfo.firstName} {resumeData.personalInfo.lastName}
        </h1>
        <div className="flex justify-center items-center space-x-4 text-sm text-gray-600 mt-2">
          <span>{resumeData.personalInfo.email}</span>
          <span>•</span>
          <span>{resumeData.personalInfo.phone}</span>
          <span>•</span>
          <span>{resumeData.personalInfo.location}</span>
        </div>
        <div className="flex justify-center items-center space-x-4 text-sm text-blue-600 mt-1">
          <a href={`https://${resumeData.personalInfo.website}`} className="hover:underline">
            {resumeData.personalInfo.website}
          </a>
          <span>•</span>
          <a href={`https://${resumeData.personalInfo.linkedin}`} className="hover:underline">
            LinkedIn
          </a>
          <span>•</span>
          <a href={`https://${resumeData.personalInfo.github}`} className="hover:underline">
            GitHub
          </a>
        </div>
      </div>

      {/* Summary */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2 border-b border-gray-300 pb-1">
          Professional Summary
        </h2>
        <p className="text-gray-700 text-sm leading-relaxed">{resumeData.summary}</p>
      </div>

      {/* Experience */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2 border-b border-gray-300 pb-1">
          Work Experience
        </h2>
        <div className="space-y-4">
          {resumeData.experience.map(exp => (
            <div key={exp.id}>
              <div className="flex justify-between items-start mb-1">
                <div>
                  <h3 className="font-semibold text-gray-900">{exp.title}</h3>
                  <p className="text-gray-700">{exp.company} • {exp.location}</p>
                </div>
                <p className="text-gray-600 text-sm">
                  {exp.startDate} - {exp.current ? 'Present' : exp.endDate}
                </p>
              </div>
              <div className="text-gray-700 text-sm whitespace-pre-line">
                {exp.description}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Skills */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2 border-b border-gray-300 pb-1">
          Technical Skills
        </h2>
        <div className="flex flex-wrap gap-2">
          {resumeData.skills.map(skill => (
            <Badge key={skill} variant="secondary" className="text-xs">
              {skill}
            </Badge>
          ))}
        </div>
      </div>

      {/* Education */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2 border-b border-gray-300 pb-1">
          Education
        </h2>
        {resumeData.education.map(edu => (
          <div key={edu.id} className="flex justify-between items-start">
            <div>
              <h3 className="font-semibold text-gray-900">{edu.degree}</h3>
              <p className="text-gray-700">{edu.school}, {edu.location}</p>
            </div>
            <p className="text-gray-600 text-sm">{edu.graduationDate}</p>
          </div>
        ))}
      </div>

      {/* Projects */}
      {resumeData.projects.length > 0 && (
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-2 border-b border-gray-300 pb-1">
            Projects
          </h2>
          {resumeData.projects.map(project => (
            <div key={project.id} className="mb-3">
              <div className="flex justify-between items-start mb-1">
                <h3 className="font-semibold text-gray-900">{project.name}</h3>
                <a href={`https://${project.link}`} className="text-blue-600 text-sm hover:underline">
                  View Project
                </a>
              </div>
              <p className="text-gray-700 text-sm mb-1">{project.description}</p>
              <div className="flex flex-wrap gap-1">
                {project.technologies.map(tech => (
                  <Badge key={tech} variant="outline" className="text-xs">
                    {tech}
                  </Badge>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Certifications */}
      {resumeData.certifications.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2 border-b border-gray-300 pb-1">
            Certifications
          </h2>
          {resumeData.certifications.map(cert => (
            <div key={cert.id} className="flex justify-between items-start">
              <div>
                <h3 className="font-semibold text-gray-900">{cert.name}</h3>
                <p className="text-gray-700">{cert.issuer}</p>
              </div>
              <p className="text-gray-600 text-sm">{cert.date}</p>
            </div>
          ))}
        </div>
      )}
    </Card>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between space-y-4 lg:space-y-0">
        <div>
          <h2 className="text-2xl font-bold">Resume Builder</h2>
          <p className="text-gray-600">Create and customize your professional resume</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button variant="outline" size="sm">
            <Eye className="h-4 w-4 mr-2" />
            Preview
          </Button>
          <Button variant="outline" size="sm">
            <Share2 className="h-4 w-4 mr-2" />
            Share
          </Button>
          <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
            <Download className="h-4 w-4 mr-2" />
            Download PDF
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Editor Panel */}
        <div className="lg:col-span-2 space-y-6">
          <Tabs defaultValue="personal">
            <TabsList className="grid w-full grid-cols-6">
              <TabsTrigger value="personal">
                <User className="h-4 w-4 mr-1" />
                Personal
              </TabsTrigger>
              <TabsTrigger value="experience">
                <Briefcase className="h-4 w-4 mr-1" />
                Experience
              </TabsTrigger>
              <TabsTrigger value="education">
                <GraduationCap className="h-4 w-4 mr-1" />
                Education
              </TabsTrigger>
              <TabsTrigger value="skills">
                <Code className="h-4 w-4 mr-1" />
                Skills
              </TabsTrigger>
              <TabsTrigger value="projects">
                <FileText className="h-4 w-4 mr-1" />
                Projects
              </TabsTrigger>
              <TabsTrigger value="templates">
                <Layout className="h-4 w-4 mr-1" />
                Templates
              </TabsTrigger>
            </TabsList>

            <TabsContent value="personal">
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Personal Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">First Name</label>
                    <Input 
                      value={resumeData.personalInfo.firstName}
                      onChange={(e) => setResumeData({
                        ...resumeData,
                        personalInfo: { ...resumeData.personalInfo, firstName: e.target.value }
                      })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Last Name</label>
                    <Input 
                      value={resumeData.personalInfo.lastName}
                      onChange={(e) => setResumeData({
                        ...resumeData,
                        personalInfo: { ...resumeData.personalInfo, lastName: e.target.value }
                      })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Email</label>
                    <Input 
                      type="email"
                      value={resumeData.personalInfo.email}
                      onChange={(e) => setResumeData({
                        ...resumeData,
                        personalInfo: { ...resumeData.personalInfo, email: e.target.value }
                      })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Phone</label>
                    <Input 
                      value={resumeData.personalInfo.phone}
                      onChange={(e) => setResumeData({
                        ...resumeData,
                        personalInfo: { ...resumeData.personalInfo, phone: e.target.value }
                      })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Location</label>
                    <Input 
                      value={resumeData.personalInfo.location}
                      onChange={(e) => setResumeData({
                        ...resumeData,
                        personalInfo: { ...resumeData.personalInfo, location: e.target.value }
                      })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Website</label>
                    <Input 
                      value={resumeData.personalInfo.website}
                      onChange={(e) => setResumeData({
                        ...resumeData,
                        personalInfo: { ...resumeData.personalInfo, website: e.target.value }
                      })}
                    />
                  </div>
                </div>
                
                <Separator className="my-6" />
                
                <div>
                  <label className="block text-sm font-medium mb-1">Professional Summary</label>
                  <Textarea 
                    className="min-h-[100px]"
                    value={resumeData.summary}
                    onChange={(e) => setResumeData({ ...resumeData, summary: e.target.value })}
                    placeholder="Write a brief professional summary..."
                  />
                </div>
              </Card>
            </TabsContent>

            <TabsContent value="experience">
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Work Experience</h3>
                  <Button size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Experience
                  </Button>
                </div>
                
                <div className="space-y-6">
                  {resumeData.experience.map(exp => (
                    <div key={exp.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div>
                          <label className="block text-sm font-medium mb-1">Job Title</label>
                          <Input value={exp.title} />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-1">Company</label>
                          <Input value={exp.company} />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-1">Start Date</label>
                          <Input type="month" value={exp.startDate} />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-1">End Date</label>
                          <Input type="month" value={exp.endDate} disabled={exp.current} />
                        </div>
                      </div>
                      <div className="mb-4">
                        <label className="block text-sm font-medium mb-1">Description</label>
                        <Textarea 
                          className="min-h-[100px]"
                          value={exp.description}
                          placeholder="Describe your responsibilities and achievements..."
                        />
                      </div>
                      <div className="flex justify-end space-x-2">
                        <Button variant="outline" size="sm">
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm" className="text-red-600">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </TabsContent>

            <TabsContent value="templates">
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Choose Template</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {templates.map(template => (
                    <div
                      key={template.id}
                      className={`p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                        activeTemplate === template.id 
                          ? 'border-blue-500 bg-blue-50' 
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => setActiveTemplate(template.id)}
                    >
                      <div className="aspect-[3/4] bg-gray-100 rounded-lg mb-3 flex items-center justify-center">
                        <FileText className="h-12 w-12 text-gray-400" />
                      </div>
                      <h4 className="font-medium">{template.name}</h4>
                      <p className="text-sm text-gray-600 mt-1">{template.description}</p>
                    </div>
                  ))}
                </div>
              </Card>
            </TabsContent>

            {/* Other tabs would have similar implementations */}
          </Tabs>
        </div>

        {/* Preview Panel */}
        <div className="lg:col-span-1">
          <div className="sticky top-6">
            <div className="mb-4">
              <h3 className="font-semibold mb-2">Live Preview</h3>
              <p className="text-sm text-gray-600">See your changes in real-time</p>
            </div>
            <div className="transform scale-50 origin-top-left w-[200%]">
              <ResumePreview />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResumeBuilder;