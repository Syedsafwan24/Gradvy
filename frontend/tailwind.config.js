/** @type {import('tailwindcss').Config} */
module.exports = {
	darkMode: ['class'],
	content: [
		'./pages/**/*.{js,jsx}',
		'./components/**/*.{js,jsx}',
		'./app/**/*.{js,jsx}',
		'./src/**/*.{js,jsx}',
	],
	theme: {
    	container: {
    		center: true,
    		padding: '2rem',
    		screens: {
    			'2xl': '1400px'
    		}
    	},
    	extend: {
    		colors: {
    			border: 'hsl(var(--border))',
    			input: 'hsl(var(--input))',
    			ring: 'hsl(var(--ring))',
    			background: 'hsl(var(--background))',
    			foreground: 'hsl(var(--foreground))',
    			primary: {
    				DEFAULT: '#4F46E5',
    				foreground: '#FFFFFF',
    				50: '#EEF2FF',
    				100: '#E0E7FF',
    				200: '#C7D2FE',
    				300: '#A5B4FC',
    				400: '#818CF8',
    				500: '#6366F1',
    				600: '#4F46E5',
    				700: '#4338CA',
    				800: '#3730A3',
    				900: '#312E81'
    			},
    			secondary: {
    				DEFAULT: '#64748B',
    				foreground: '#FFFFFF'
    			},
    			accent: {
    				DEFAULT: '#06b6d4',
    				foreground: 'hsl(var(--accent-foreground))'
    			},
    			muted: {
    				DEFAULT: '#F1F5F9',
    				foreground: '#64748B'
    			},
    			destructive: {
    				DEFAULT: '#EF4444',
    				foreground: '#FFFFFF'
    			},
    			success: {
    				DEFAULT: '#10B981',
    				foreground: '#FFFFFF'
    			},
    			warning: {
    				DEFAULT: '#F59E0B',
    				foreground: '#FFFFFF'
    			},
    			info: {
    				DEFAULT: '#3B82F6',
    				foreground: '#FFFFFF'
    			},
    			card: {
    				DEFAULT: '#FFFFFF',
    				foreground: '#0F172A'
    			},
    			popover: {
    				DEFAULT: 'hsl(var(--popover))',
    				foreground: 'hsl(var(--popover-foreground))'
    			}
    		},
    		borderRadius: {
    			lg: 'var(--radius)',
    			md: 'calc(var(--radius) - 2px)',
    			sm: 'calc(var(--radius) - 4px)'
    		},
    		fontFamily: {
    			sans: [
    				'Inter',
    				'sans-serif'
    			]
    		},
    		keyframes: {
    			'accordion-down': {
    				from: {
    					height: '0'
    				},
    				to: {
    					height: 'var(--radix-accordion-content-height)'
    				}
    			},
    			'accordion-up': {
    				from: {
    					height: 'var(--radix-accordion-content-height)'
    				},
    				to: {
    					height: '0'
    				}
    			},
    			'fade-in-up': {
    				'0%': {
    					opacity: '0',
    					transform: 'translateY(20px)'
    				},
    				'100%': {
    					opacity: '1',
    					transform: 'translateY(0)'
    				}
    			},
    			float: {
    				'0%, 100%': {
    					transform: 'translateY(0px)'
    				},
    				'50%': {
    					transform: 'translateY(-20px)'
    				}
    			}
    		},
    		animation: {
    			'accordion-down': 'accordion-down 0.2s ease-out',
    			'accordion-up': 'accordion-up 0.2s ease-out',
    			'fade-in-up': 'fade-in-up 0.5s ease-out',
    			float: 'float 6s ease-in-out infinite'
    		}
    	}
    },
	plugins: [require('tailwindcss-animate')],
};
