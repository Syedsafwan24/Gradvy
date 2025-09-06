'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Button } from '../ui/Button';
import { Menu, X, Brain, ChevronDown } from 'lucide-react';

const Navbar = () => {
	const [isOpen, setIsOpen] = useState(false);

	const navigation = [
		{ name: 'Home', href: '/' },
		{ name: 'Courses', href: '/courses' },
		{ name: 'Dashboard', href: '/dashboard' },
		{ name: 'Playground', href: '/playground' },
		{ name: 'Career', href: '/career' },
	];

	return (
		<nav className='bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50'>
			<div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
				<div className='flex justify-between h-16'>
					<div className='flex items-center'>
						<Link href='/' className='flex items-center space-x-2'>
							<div className='w-8 h-8 bg-gradient-to-r from-primary to-accent rounded-lg flex items-center justify-center'>
								<Brain className='h-5 w-5 text-white' />
							</div>
							<span className='text-xl font-bold gradient-text'>Gradvy</span>
						</Link>
					</div>

					{/* Desktop Navigation */}
					<div className='hidden md:flex items-center space-x-8'>
						{navigation.map((item) => (
							<Link
								key={item.name}
								href={item.href}
								className='text-gray-600 hover:text-primary transition-colors duration-200 font-medium'
							>
								{item.name}
							</Link>
						))}
					</div>

					{/* Desktop CTA */}
					<div className='hidden md:flex items-center space-x-4'>
						<Button variant='ghost' size='sm'>
							Sign In
						</Button>
						<Button variant='gradient' size='sm'>
							Get Started
						</Button>
					</div>

					{/* Mobile menu button */}
					<div className='md:hidden flex items-center'>
						<button
							onClick={() => setIsOpen(!isOpen)}
							className='text-gray-500 hover:text-gray-600 transition-colors duration-200'
						>
							{isOpen ? (
								<X className='h-6 w-6' />
							) : (
								<Menu className='h-6 w-6' />
							)}
						</button>
					</div>
				</div>
			</div>

			{/* Mobile Navigation */}
			{isOpen && (
				<motion.div
					initial={{ opacity: 0, y: -10 }}
					animate={{ opacity: 1, y: 0 }}
					exit={{ opacity: 0, y: -10 }}
					className='md:hidden border-t border-gray-200 bg-white'
				>
					<div className='px-2 pt-2 pb-3 space-y-1'>
						{navigation.map((item) => (
							<Link
								key={item.name}
								href={item.href}
								className='block px-3 py-2 text-gray-600 hover:text-primary hover:bg-gray-50 rounded-md transition-colors duration-200'
								onClick={() => setIsOpen(false)}
							>
								{item.name}
							</Link>
						))}
						<div className='px-3 py-2 space-y-2'>
							<Button variant='ghost' size='sm' className='w-full'>
								Sign In
							</Button>
							<Button variant='gradient' size='sm' className='w-full'>
								Get Started
							</Button>
						</div>
					</div>
				</motion.div>
			)}
		</nav>
	);
};

export default Navbar;
