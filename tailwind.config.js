/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./js/**/*.js"],
  theme: {
    extend: {
      colors: {
        purple: {
          DEFAULT: '#450C3F',
          dark: '#300229',
          light: '#6B1B62'
        },
        green: {
          DEFAULT: '#B9D175',
          dark: '#9BB859'
        }
      },
      fontFamily: {
        sans: ['Noto Sans KR', 'sans-serif'],
        serif: ['Gowun Batang', 'serif']
      }
    }
  },
  plugins: []
}
