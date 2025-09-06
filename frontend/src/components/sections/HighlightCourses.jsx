'use client';

import { motion } from 'framer-motion';
import { Star, Clock, Users, ExternalLink, ArrowRight } from 'lucide-react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';

const HighlightCourses = () => {
	const highlightCourses = [
		{
			id: '1',
			title: 'Complete Python Bootcamp',
			thumbnail:
				'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=400&h=250&fit=crop',
			provider: 'Udemy',
			rating: 4.8,
			reviews: 15420,
			duration: '22 hours',
			level: 'Beginner',
			description:
				'Learn Python from scratch with hands-on projects and real-world applications.',
			originalPrice: '$89.99',
			discountPrice: '$12.99',
		},
		{
			id: '2',
			title: 'JavaScript: The Complete Guide',
			thumbnail:
				'https://images.unsplash.com/photo-1627398242454-45a1465c2479?w=400&h=250&fit=crop',
			provider: 'Coursera',
			rating: 4.9,
			reviews: 8934,
			duration: '18 hours',
			level: 'Intermediate',
			description:
				'Master JavaScript fundamentals and advanced concepts with practical projects.',
			originalPrice: '$79.99',
			discountPrice: '$9.99',
		},
		{
			id: '3',
			title: 'Data Science with R',
			thumbnail:
				'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=250&fit=crop',
			provider: 'YouTube',
			rating: 4.7,
			reviews: 5672,
			duration: '15 hours',
			level: 'Advanced',
			description:
				'Comprehensive R programming for data analysis and statistical modeling.',
			originalPrice: 'Free',
			discountPrice: 'Free',
		},
	];

	const containerVariants = {
		hidden: { opacity: 0 },
		visible: {
			opacity: 1,
			transition: {
				staggerChildren: 0.2,
			},
		},
	};

	const courseVariants = {
		hidden: { opacity: 0, y: 30 },
		visible: {
			opacity: 1,
			y: 0,
			transition: { duration: 0.6 },
		},
	};

	return (
		<section className='py-20 bg-white'>
			<div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
				{/* Header */}
				<motion.div
					initial={{ opacity: 0, y: 20 }}
					whileInView={{ opacity: 1, y: 0 }}
					viewport={{ once: true }}
					transition={{ duration: 0.6 }}
					className='text-center mb-16'
				>
					<h2 className='text-4xl font-bold text-slate-900 mb-4'>
						Featured Learning Paths
					</h2>
					<p className='text-xl text-slate-600 max-w-3xl mx-auto'>
						Discover hand-picked courses from top platforms to accelerate your
						learning journey. Start with these popular choices curated by our
						AI.
					</p>
				</motion.div>

				{/* Courses Grid */}
				<motion.div
					variants={containerVariants}
					initial='hidden'
					whileInView='visible'
					viewport={{ once: true }}
					className='grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12'
				>
					{highlightCourses.map((course, index) => (
						<motion.div
							key={course.id}
							variants={courseVariants}
							className='group'
						>
							<Card className='h-full overflow-hidden hover:shadow-xl transition-all duration-300 group-hover:-translate-y-2'>
								{/* Course Image */}
								<div className='relative overflow-hidden'>
									<img
										src={course.thumbnail}
										alt={course.title}
										className='w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300'
									/>
									<div className='absolute top-4 left-4'>
										<span className='bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-medium text-slate-700'>
											{course.provider}
										</span>
									</div>
									<div className='absolute top-4 right-4'>
										<span
											className={`px-3 py-1 rounded-full text-sm font-medium ${
												course.level === 'Beginner'
													? 'bg-green-100 text-green-700'
													: course.level === 'Intermediate'
													? 'bg-blue-100 text-blue-700'
													: 'bg-purple-100 text-purple-700'
											}`}
										>
											{course.level}
										</span>
									</div>
								</div>

								{/* Course Content */}
								<div className='p-6'>
									<h3 className='text-xl font-semibold text-slate-900 mb-2 group-hover:text-blue-600 transition-colors'>
										{course.title}
									</h3>
									<p className='text-slate-600 mb-4 line-clamp-2'>
										{course.description}
									</p>

									{/* Rating & Duration */}
									<div className='flex items-center justify-between mb-4'>
										<div className='flex items-center space-x-1'>
											<Star className='w-4 h-4 text-yellow-400 fill-current' />
											<span className='text-sm font-medium text-slate-700'>
												{course.rating}
											</span>
											<span className='text-sm text-slate-500'>
												({course.reviews.toLocaleString()})
											</span>
										</div>
										<div className='flex items-center space-x-1 text-slate-500'>
											<Clock className='w-4 h-4' />
											<span className='text-sm'>{course.duration}</span>
										</div>
									</div>

									{/* Price */}
									<div className='flex items-center justify-between mb-4'>
										<div className='flex items-center space-x-2'>
											{course.discountPrice !== 'Free' &&
												course.originalPrice !== course.discountPrice && (
													<span className='text-sm text-slate-500 line-through'>
														{course.originalPrice}
													</span>
												)}
											<span
												className={`font-bold ${
													course.discountPrice === 'Free'
														? 'text-green-600'
														: 'text-blue-600'
												}`}
											>
												{course.discountPrice}
											</span>
										</div>
										<div className='flex items-center space-x-1 text-slate-500'>
											<Users className='w-4 h-4' />
											<span className='text-sm'>
												{course.reviews.toLocaleString()}
											</span>
										</div>
									</div>

									{/* CTA Button */}
									<Button
										variant='outline'
										className='w-full group-hover:bg-blue-600 group-hover:text-white group-hover:border-blue-600 transition-all duration-300'
									>
										Start Learning
										<ExternalLink className='w-4 h-4 ml-2' />
									</Button>
								</div>
							</Card>
						</motion.div>
					))}
				</motion.div>

				{/* CTA Section */}
				<motion.div
					initial={{ opacity: 0, y: 20 }}
					whileInView={{ opacity: 1, y: 0 }}
					viewport={{ once: true }}
					transition={{ duration: 0.6, delay: 0.4 }}
					className='text-center'
				>
					<p className='text-slate-600 mb-6'>
						Want a personalized learning path? Let our AI create a custom
						curriculum just for you.
					</p>
					<Button
						size='lg'
						className='bg-blue-600 hover:bg-blue-700 text-white group'
					>
						Browse All Courses
						<ArrowRight className='w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform' />
					</Button>
				</motion.div>
			</div>
		</section>
	);
};

export default HighlightCourses;
