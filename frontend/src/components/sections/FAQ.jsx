'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, ChevronUp } from 'lucide-react';

const FAQ = () => {
	const [openIndex, setOpenIndex] = useState(0);

	const faqs = [
		{
			question: 'How does Gradvy create personalized learning paths?',
			answer:
				'Gradvy uses advanced AI algorithms to analyze your goals, background, time availability, and learning preferences. It then curates courses from top platforms like Udemy, Coursera, and YouTube to create a structured learning roadmap tailored specifically for you.',
		},
		{
			question: 'What platforms does Gradvy integrate with?',
			answer:
				'Gradvy integrates with major learning platforms including Udemy, Coursera, YouTube, and other educational resources. We continuously expand our partnerships to provide you with the best content available.',
		},
		{
			question: 'Can I use Gradvy without a specific career goal?',
			answer:
				'Absolutely! Gradvy offers an "Help me decide" flow that uses interest-detection quizzes to help you discover potential career paths. Our AI analyzes your responses to suggest suitable learning directions.',
		},
		{
			question: 'What is the coding playground feature?',
			answer:
				'The coding playground is an integrated development environment that supports multiple programming languages. It allows you to practice coding exercises, run code in real-time, and get instant feedback on your solutions.',
		},
		{
			question: 'How accurate are the career insights provided?',
			answer:
				'Our career insights are based on real-time job market data, salary information, and industry trends. We continuously update our database to provide accurate information about job roles, required skills, and career progression paths.',
		},
		{
			question: 'Is there a free version of Gradvy?',
			answer:
				'Yes! Gradvy offers a free Starter plan that includes basic learning path generation, access to free courses, progress tracking, and community access. You can upgrade to Pro for advanced features.',
		},
	];

	return (
		<section id='faq' className='py-24 bg-white'>
			<div className='max-w-4xl mx-auto px-4 sm:px-6 lg:px-8'>
				<motion.div
					initial={{ opacity: 0, y: 20 }}
					whileInView={{ opacity: 1, y: 0 }}
					viewport={{ once: true }}
					transition={{ duration: 0.6 }}
					className='text-center mb-16'
				>
					<h2 className='text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-4'>
						Frequently Asked <span className='gradient-text'>Questions</span>
					</h2>
					<p className='text-xl text-gray-600'>
						Everything you need to know about Gradvy's AI-powered learning
						platform.
					</p>
				</motion.div>

				<motion.div
					initial={{ opacity: 0 }}
					whileInView={{ opacity: 1 }}
					viewport={{ once: true }}
					transition={{ duration: 0.6, delay: 0.2 }}
					className='space-y-4'
				>
					{faqs.map((faq, index) => (
						<motion.div
							key={index}
							initial={{ opacity: 0, y: 20 }}
							whileInView={{ opacity: 1, y: 0 }}
							viewport={{ once: true }}
							transition={{ duration: 0.6, delay: index * 0.1 }}
							className='bg-gray-50 rounded-lg border border-gray-200 overflow-hidden'
						>
							<button
								className='w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-100 transition-colors duration-200 focus:outline-none focus:bg-gray-100'
								onClick={() => setOpenIndex(openIndex === index ? -1 : index)}
							>
								<h3 className='text-lg font-semibold text-gray-900 pr-4'>
									{faq.question}
								</h3>
								{openIndex === index ? (
									<ChevronUp className='h-5 w-5 text-primary flex-shrink-0' />
								) : (
									<ChevronDown className='h-5 w-5 text-gray-500 flex-shrink-0' />
								)}
							</button>

							<motion.div
								initial={false}
								animate={{
									height: openIndex === index ? 'auto' : 0,
									opacity: openIndex === index ? 1 : 0,
								}}
								transition={{ duration: 0.3, ease: 'easeInOut' }}
								className='overflow-hidden'
							>
								<div className='px-6 pb-4'>
									<p className='text-gray-600 leading-relaxed'>{faq.answer}</p>
								</div>
							</motion.div>
						</motion.div>
					))}
				</motion.div>

				<motion.div
					initial={{ opacity: 0, y: 20 }}
					whileInView={{ opacity: 1, y: 0 }}
					viewport={{ once: true }}
					transition={{ duration: 0.6, delay: 0.4 }}
					className='text-center mt-12'
				>
					<p className='text-gray-600 mb-4'>
						Still have questions? We'd love to help!
					</p>
					<button className='text-primary font-semibold hover:text-primary/80 transition-colors duration-200'>
						Contact our support team →
					</button>
				</motion.div>
			</div>
		</section>
	);
};

export default FAQ;
