'use client';

import { motion } from 'framer-motion';
import {
	Code,
	Play,
	Terminal,
	Zap,
	CheckCircle,
	ArrowRight,
} from 'lucide-react';
import { Button } from '@/components/ui/button';

const CodePlayground = () => {
	const features = [
		{
			icon: <Code className='w-6 h-6' />,
			title: 'Multi-Language Support',
			description: 'Practice with Python, JavaScript, Java, C++, and more',
		},
		{
			icon: <Play className='w-6 h-6' />,
			title: 'Instant Execution',
			description: 'Run your code instantly and see results in real-time',
		},
		{
			icon: <Terminal className='w-6 h-6' />,
			title: 'Interactive Console',
			description: 'Debug and test with an integrated terminal experience',
		},
		{
			icon: <Zap className='w-6 h-6' />,
			title: 'AI-Powered Hints',
			description: "Get smart suggestions when you're stuck",
		},
	];

	const codeExample = `def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")`;

	return (
		<section className='py-20 bg-gradient-to-br from-slate-50 to-blue-50'>
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
						Practice Coding in Real-Time
					</h2>
					<p className='text-xl text-slate-600 max-w-3xl mx-auto'>
						Master programming concepts with our interactive coding playground.
						Write, run, and debug code instantly with AI-powered assistance.
					</p>
				</motion.div>

				<div className='grid lg:grid-cols-2 gap-12 items-center'>
					{/* Left: Code Editor Preview */}
					<motion.div
						initial={{ opacity: 0, x: -50 }}
						whileInView={{ opacity: 1, x: 0 }}
						viewport={{ once: true }}
						transition={{ duration: 0.6, delay: 0.2 }}
						className='relative'
					>
						<div className='bg-slate-900 rounded-xl overflow-hidden shadow-2xl'>
							{/* Editor Header */}
							<div className='flex items-center justify-between px-4 py-3 bg-slate-800 border-b border-slate-700'>
								<div className='flex items-center space-x-2'>
									<div className='w-3 h-3 bg-red-500 rounded-full'></div>
									<div className='w-3 h-3 bg-yellow-500 rounded-full'></div>
									<div className='w-3 h-3 bg-green-500 rounded-full'></div>
								</div>
								<div className='flex items-center space-x-2'>
									<span className='text-sm text-slate-400'>fibonacci.py</span>
									<Button size='sm' className='bg-blue-600 hover:bg-blue-700'>
										<Play className='w-4 h-4 mr-1' />
										Run
									</Button>
								</div>
							</div>

							{/* Code Content */}
							<div className='p-4'>
								<pre className='text-sm text-slate-300 leading-relaxed'>
									<code className='language-python'>{codeExample}</code>
								</pre>
							</div>

							{/* Output Panel */}
							<div className='bg-slate-800 px-4 py-3 border-t border-slate-700'>
								<div className='flex items-center mb-2'>
									<Terminal className='w-4 h-4 text-green-400 mr-2' />
									<span className='text-sm text-slate-400'>Output</span>
								</div>
								<div className='text-sm text-green-400 font-mono'>
									F(0) = 0<br />
									F(1) = 1<br />
									F(2) = 1<br />
									F(3) = 2<br />
									<span className='text-slate-500'>...</span>
								</div>
							</div>
						</div>

						{/* Floating Elements */}
						<motion.div
							animate={{ y: [0, -10, 0] }}
							transition={{ duration: 2, repeat: Infinity }}
							className='absolute -top-4 -right-4 bg-white rounded-lg shadow-lg p-3'
						>
							<CheckCircle className='w-6 h-6 text-green-500' />
						</motion.div>
					</motion.div>

					{/* Right: Features */}
					<motion.div
						initial={{ opacity: 0, x: 50 }}
						whileInView={{ opacity: 1, x: 0 }}
						viewport={{ once: true }}
						transition={{ duration: 0.6, delay: 0.4 }}
						className='space-y-8'
					>
						{features.map((feature, index) => (
							<motion.div
								key={index}
								initial={{ opacity: 0, y: 20 }}
								whileInView={{ opacity: 1, y: 0 }}
								viewport={{ once: true }}
								transition={{ duration: 0.6, delay: 0.1 * index }}
								className='flex items-start space-x-4'
							>
								<div className='flex-shrink-0 w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600'>
									{feature.icon}
								</div>
								<div>
									<h3 className='text-lg font-semibold text-slate-900 mb-2'>
										{feature.title}
									</h3>
									<p className='text-slate-600'>{feature.description}</p>
								</div>
							</motion.div>
						))}

						{/* CTA */}
						<motion.div
							initial={{ opacity: 0, y: 20 }}
							whileInView={{ opacity: 1, y: 0 }}
							viewport={{ once: true }}
							transition={{ duration: 0.6, delay: 0.6 }}
							className='pt-6'
						>
							<Button
								size='lg'
								className='bg-blue-600 hover:bg-blue-700 text-white group'
							>
								Try Playground Now
								<ArrowRight className='w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform' />
							</Button>
						</motion.div>
					</motion.div>
				</div>
			</div>
		</section>
	);
};

export default CodePlayground;
