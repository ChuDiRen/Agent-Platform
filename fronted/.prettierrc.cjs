module.exports = {
  printWidth: 100,
  tabWidth: 2,
  useTabs: false,
  semi: false,
  singleQuote: true,
  trailingComma: 'all',
  bracketSpacing: true,
  arrowParens: 'always',
  overrides: [
    {
      files: '*.json',
      options: { printWidth: 200 },
    },
  ],
}
