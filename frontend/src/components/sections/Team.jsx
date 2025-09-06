'use client';

import { motion } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/Card';
import { Github, Linkedin, Twitter } from 'lucide-react';

const Team = () => {
	const teamMembers = [
		{
			name: 'Alex Thompson',
			role: 'CEO & AI Research Lead',
			avatar:
				'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=300&h=300&fit=crop&crop=face',
			bio: 'Former Google AI researcher with 10+ years in machine learning and educational technology.',
			social: {
				github: 'https://github.com',
				linkedin: 'https://linkedin.com',
				twitter: 'https://twitter.com',
			},
		},
		{
			name: 'Sarah Kim',
			role: 'Head of Product',
			avatar:
				'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=300&h=300&fit=crop&crop=face',
			bio: 'Product strategist who led learning platforms at Coursera and Udacity, passionate about democratizing education.',
			social: {
				github: 'https://github.com',
				linkedin: 'https://linkedin.com',
				twitter: 'https://twitter.com',
			},
		},
		{
			name: 'David Chen',
			role: 'Lead Engineer',
			avatar:
				'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop&crop=face',
			bio: 'Full-stack engineer with expertise in scalable AI systems and a passion for creating intuitive user experiences.',
			social: {
				github: 'https://github.com',
				linkedin: 'https://linkedin.com',
				twitter: 'https://twitter.com',
			},
		},
	];

	const containerVariants = {
		hidden: { opacity: 0 },
		visible: {
			opacity: 1,
			transition: {
				delayChildren: 0.2,
				staggerChildren: 0.1,
			},
		},
	};

	const itemVariants = {
		hidden: { y: 20, opacity: 0 },
		visible: {
			y: 0,
			opacity: 1,
			transition: {
				type: 'spring',
				stiffness: 100,
			},
		},
	};

	return (
		<section id='team' className='py-24 bg-gray-50'>
			<div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
				<motion.div
					initial={{ opacity: 0, y: 20 }}
					whileInView={{ opacity: 1, y: 0 }}
					viewport={{ once: true }}
					transition={{ duration: 0.6 }}
					className='text-center mb-16'
				>
					<h2 className='text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-4'>
						Meet Our <span className='gradient-text'>Team</span>
					</h2>
					<p className='text-xl text-gray-600 max-w-3xl mx-auto'>
						The passionate experts behind Gradvy's innovative AI-powered
						learning platform.
					</p>
				</motion.div>

				<motion.div
					variants={containerVariants}
					initial='hidden'
					whileInView='visible'
					viewport={{ once: true }}
					className='grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto'
				>
					{teamMembers.map((member, index) => (
						<motion.div
							key={member.name}
							variants={itemVariants}
							className='group'
						>
							<Card className='h-full bg-white border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-2'>
								<CardContent className='p-6 text-center'>
									<div className='relative mb-6'>
										<img
											src={member.avatar}
											alt={member.name}
											className='w-24 h-24 rounded-full mx-auto object-cover group-hover:scale-110 transition-transform duration-300'
										/>
										<div className='absolute inset-0 w-24 h-24 rounded-full mx-auto bg-gradient-to-r from-primary/20 to-accent/20 group-hover:opacity-100 opacity-0 transition-opacity duration-300' />
									</div>

									<h3 className='text-xl font-bold text-gray-900 mb-2'>
										{member.name}
									</h3>

									<p className='text-primary font-medium mb-4'>{member.role}</p>

									<p className='text-gray-600 text-sm leading-relaxed mb-6'>
										{member.bio}
									</p>

									<div className='flex justify-center space-x-4'>
										<a
											href={member.social.github}
											className='text-gray-400 hover:text-gray-600 transition-colors duration-200'
											aria-label={`${member.name} GitHub`}
										>
											<Github className='h-5 w-5' />
										</a>
										<a
											href={member.social.linkedin}
											className='text-gray-400 hover:text-blue-600 transition-colors duration-200'
											aria-label={`${member.name} LinkedIn`}
										>
											<Linkedin className='h-5 w-5' />
										</a>
										<a
											href={member.social.twitter}
											className='text-gray-400 hover:text-blue-400 transition-colors duration-200'
											aria-label={`${member.name} Twitter`}
										>
											<Twitter className='h-5 w-5' />
										</a>
									</div>
								</CardContent>
							</Card>
						</motion.div>
					))}
				</motion.div>

				{/* Company Stats */}
				<motion.div
					initial={{ opacity: 0, y: 20 }}
					whileInView={{ opacity: 1, y: 0 }}
					viewport={{ once: true }}
					transition={{ duration: 0.6, delay: 0.3 }}
					className='mt-20 text-center'
				>
					<div className='bg-gradient-to-r from-primary to-accent rounded-2xl p-8 text-white'>
						<h3 className='text-2xl font-bold mb-4'>
							Building the Future of Learning
						</h3>
						<div className='grid grid-cols-1 md:grid-cols-3 gap-8'>
							<div>
								<div className='text-3xl font-bold mb-2'>15+</div>
								<div className='text-blue-100'>Team Members</div>
							</div>
							<div>
								<div className='text-3xl font-bold mb-2'>3</div>
								<div className='text-blue-100'>Years of Research</div>
							</div>
							<div>
								<div className='text-3xl font-bold mb-2'>150k+</div>
								<div className='text-blue-100'>Learners Helped</div>
							</div>
						</div>
					</div>
				</motion.div>
			</div>
		</section>
	);
};

export default Team;
