'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { useSelector } from 'react-redux';
import { Button } from '../ui/Button';
import { Menu, X, Brain, ChevronDown, User, LogOut } from 'lucide-react';
import { selectIsAuthenticated, selectCurrentUser } from '../../store/slices/authSlice';
import { useLogoutMutation } from '../../store/api/authApi';
import toast from 'react-hot-toast';

const Navbar = () => {
	const [isOpen, setIsOpen] = useState(false);
	const [showUserMenu, setShowUserMenu] = useState(false);
	
	const router = useRouter();
	const isAuthenticated = useSelector(selectIsAuthenticated);
	const user = useSelector(selectCurrentUser);
	const [logout, { isLoading: isLoggingOut }] = useLogoutMutation();

	const navigation = [
		{ name: 'Home', href: '/' },
		{ name: 'Courses', href: '/courses' },
		...(isAuthenticated ? [{ name: 'Dashboard', href: '/dashboard' }] : []),
		{ name: 'Playground', href: '/playground' },
		{ name: 'Career', href: '/career' },
	];

	const handleLogout = async () => {
		try {
			await logout();
			toast.success('Logged out successfully');
			router.push('/');
			setShowUserMenu(false);
		} catch (error) {
			console.error('Logout error:', error);
			// Still show success and redirect since local state is cleared
			toast.success('Logged out successfully');
			router.push('/');
			setShowUserMenu(false);
		}
	};

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
						{isAuthenticated ? (
							<div className="relative">
								<button
									onClick={() => setShowUserMenu(!showUserMenu)}
									className="flex items-center space-x-2 text-gray-600 hover:text-primary transition-colors duration-200"
								>
									<div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
										<User className="h-4 w-4 text-blue-600" />
									</div>
									<span className="font-medium">{user?.first_name}</span>
									<ChevronDown className="h-4 w-4" />
								</button>
								
								{showUserMenu && (
									<motion.div
										initial={{ opacity: 0, y: -10 }}
										animate={{ opacity: 1, y: 0 }}
										exit={{ opacity: 0, y: -10 }}
										className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 py-1"
									>
										<Link
											href="/dashboard"
											className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
											onClick={() => setShowUserMenu(false)}
										>
											Dashboard
										</Link>
										<Link
											href="/profile"
											className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
											onClick={() => setShowUserMenu(false)}
										>
											Profile
										</Link>
										<Link
											href="/settings"
											className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
											onClick={() => setShowUserMenu(false)}
										>
											Settings
										</Link>
										<hr className="my-1" />
										<button
											onClick={handleLogout}
											disabled={isLoggingOut}
											className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 disabled:opacity-50"
										>
											<LogOut className="h-4 w-4 inline mr-2" />
											{isLoggingOut ? 'Logging out...' : 'Logout'}
										</button>
									</motion.div>
								)}
							</div>
						) : (
							<>
								<Link href="/login">
									<Button variant='ghost' size='sm'>
										Sign In
									</Button>
								</Link>
								<Link href="/register">
									<Button size='sm'>
										Get Started
									</Button>
								</Link>
							</>
						)}
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
							{isAuthenticated ? (
								<>
									<div className="flex items-center space-x-2 px-3 py-2 bg-gray-50 rounded-md">
										<div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
											<User className="h-4 w-4 text-blue-600" />
										</div>
										<span className="font-medium text-gray-700">{user?.first_name} {user?.last_name}</span>
									</div>
									<Link href="/dashboard" onClick={() => setIsOpen(false)}>
										<Button variant='ghost' size='sm' className='w-full justify-start'>
											Dashboard
										</Button>
									</Link>
									<Link href="/profile" onClick={() => setIsOpen(false)}>
										<Button variant='ghost' size='sm' className='w-full justify-start'>
											Profile
										</Button>
									</Link>
									<Button
										variant='ghost'
										size='sm'
										className='w-full justify-start text-red-600'
										onClick={() => {
											handleLogout();
											setIsOpen(false);
										}}
										disabled={isLoggingOut}
									>
										<LogOut className="h-4 w-4 mr-2" />
										{isLoggingOut ? 'Logging out...' : 'Logout'}
									</Button>
								</>
							) : (
								<>
									<Link href="/login" onClick={() => setIsOpen(false)}>
										<Button variant='ghost' size='sm' className='w-full'>
											Sign In
										</Button>
									</Link>
									<Link href="/register" onClick={() => setIsOpen(false)}>
										<Button variant='gradient' size='sm' className='w-full'>
											Get Started
										</Button>
									</Link>
								</>
							)}
						</div>
					</div>
				</motion.div>
			)}
		</nav>
	);
};

export default Navbar;
