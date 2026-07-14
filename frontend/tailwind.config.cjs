/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#0B1220',
          900: '#111827',
          800: '#1F2937',
          700: '#374151',
          600: '#4B5563',
          500: '#6B7280',
          400: '#9CA3AF',
        },
        brand: {
          50: '#ECFDF8',
          100: '#D1FAE5',
          200: '#A7F3D0',
          300: '#6EE7B7',
          400: '#34D399',
          500: '#059669',
          600: '#047857',
          700: '#065F46',
          800: '#064E3B',
        },
        accent: {
          400: '#F59E0B',
          500: '#D97706',
          600: '#B45309',
        },
        hot: {
          DEFAULT: '#DC2626',
          soft: '#FEF2F2',
          border: '#FECACA',
        },
        warm: {
          DEFAULT: '#D97706',
          soft: '#FFFBEB',
          border: '#FDE68A',
        },
        cold: {
          DEFAULT: '#64748B',
          soft: '#F8FAFC',
          border: '#E2E8F0',
        },
      },
      fontFamily: {
        display: ['"Fraunces"', 'Georgia', 'serif'],
        sans: ['"Manrope"', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        soft: '0 10px 40px -12px rgba(15, 23, 42, 0.18)',
        card: '0 1px 2px rgba(15, 23, 42, 0.04), 0 8px 24px -8px rgba(15, 23, 42, 0.12)',
      },
      backgroundImage: {
        'hero-grid':
          'radial-gradient(circle at 20% 20%, rgba(5,150,105,0.22), transparent 35%), radial-gradient(circle at 80% 10%, rgba(217,119,6,0.14), transparent 30%), linear-gradient(160deg, #0B1220 0%, #111827 45%, #064E3B 120%)',
        'app-mesh':
          'radial-gradient(ellipse at top left, rgba(5,150,105,0.07), transparent 42%), radial-gradient(ellipse at bottom right, rgba(217,119,6,0.05), transparent 38%), linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%)',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(-6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        rise: {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        fadeIn: 'fadeIn 0.25s ease forwards',
        rise: 'rise 0.45s ease forwards',
      },
    },
  },
  plugins: [],
}
