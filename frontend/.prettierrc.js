module.exports = {
  semi: true,
  trailingComma: 'es5',
  singleQuote: true,
  printWidth: 100,
  tabWidth: 2,
  useTabs: false,
  bracketSpacing: true,
  bracketSameLine: false,
  arrowParens: 'avoid',
  endOfLine: 'lf',
  jsxSingleQuote: false,
  quoteProps: 'as-needed',
  
  // Plugin-specific options
  plugins: ['prettier-plugin-tailwindcss'],
  
  // File-specific overrides
  overrides: [
    {
      files: '*.{js,jsx,ts,tsx}',
      options: {
        parser: 'babel-flow'
      }
    },
    {
      files: '*.json',
      options: {
        printWidth: 120
      }
    }
  ]
};