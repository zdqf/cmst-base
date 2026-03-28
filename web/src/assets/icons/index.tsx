import React from 'react'

const svgProps: React.SVGProps<SVGSVGElement> = {
  width: '1em',
  height: '1em',
  fill: 'currentColor',
  viewBox: '0 0 1024 1024',
}

export const HerbLeafIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg {...svgProps} {...props}>
    <path d="M512 96c-48 0-96 32-128 80-64 96-80 256-16 384 16 32 48 64 80 80 16-128 64-256 144-352 32-40 64-72 96-96-16-16-32-32-48-40C592 112 544 96 512 96zM320 640c-32 48-48 96-48 144 0 48 16 80 48 96 32 16 80 16 128-16 48-32 96-96 128-176-48-16-96-48-128-80-48-48-80-96-96-160-16 48-24 112-32 192z" />
    <path d="M704 192c-32 24-64 56-96 96-80 96-128 224-144 352 48 16 96 16 144 0 96-32 176-128 208-256 16-64 16-128 0-176-32-16-64-24-112-16z" opacity="0.6" />
  </svg>
)

export const LogoIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg width="1em" height="1em" viewBox="0 0 200 200" fill="currentColor" {...props}>
    <circle cx="100" cy="100" r="92" fill="none" stroke="currentColor" strokeWidth="3" opacity="0.3" />
    <circle cx="100" cy="100" r="80" fill="none" stroke="currentColor" strokeWidth="1.5" opacity="0.15" />
    <path d="M100 28c-12 22-32 44-32 76 0 34 16 56 32 66 16-10 32-32 32-66 0-32-20-54-32-76z" fill="currentColor" opacity="0.75" />
    <path d="M58 88c12-6 28-6 42 6 14-12 30-12 42-6-6 28-22 50-42 60-20-10-36-32-42-60z" fill="currentColor" opacity="0.35" />
    <circle cx="100" cy="112" r="6" fill="currentColor" opacity="0.9" />
    <path d="M100 140c-4 16-6 32-4 44 2-12 4-28 4-44z" fill="currentColor" opacity="0.4" />
  </svg>
)

export const WaveDecoration: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg viewBox="0 0 1440 120" fill="none" preserveAspectRatio="none" {...props}>
    <path d="M0 40c160-30 320 20 480 10s320-30 480 0 320 20 480-10v80H0z" fill="currentColor" opacity="0.06" />
    <path d="M0 60c240-25 480 25 720 0s480-25 720 0v60H0z" fill="currentColor" opacity="0.04" />
  </svg>
)

// ===== Product illustration SVGs =====
export const HerbBagIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg width="1em" height="1em" viewBox="0 0 120 120" fill="none" {...props}>
    <rect x="25" y="45" width="70" height="55" rx="8" fill="#d4edda" stroke="#2c6b4f" strokeWidth="1.5" />
    <path d="M35 45c0-15 10-25 25-25s25 10 25 25" fill="none" stroke="#2c6b4f" strokeWidth="1.5" strokeLinecap="round" />
    <path d="M45 65c5-3 12-3 15 2 3-5 10-5 15-2" fill="none" stroke="#2c6b4f" strokeWidth="1.2" strokeLinecap="round" />
    <circle cx="60" cy="78" r="3" fill="#2c6b4f" opacity="0.5" />
    <line x1="60" y1="81" x2="60" y2="90" stroke="#2c6b4f" strokeWidth="1" opacity="0.4" />
  </svg>
)

export const TeaCupIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg width="1em" height="1em" viewBox="0 0 120 120" fill="none" {...props}>
    <path d="M30 50h50v35c0 10-8 18-18 18H48c-10 0-18-8-18-18V50z" fill="#fff3e0" stroke="#e65100" strokeWidth="1.5" />
    <path d="M80 58c8 0 14 6 14 14s-6 14-14 14" fill="none" stroke="#e65100" strokeWidth="1.5" />
    <path d="M42 40c0-6 4-10 4-10" fill="none" stroke="#e65100" strokeWidth="1" strokeLinecap="round" opacity="0.5" />
    <path d="M55 38c0-8 4-12 4-12" fill="none" stroke="#e65100" strokeWidth="1" strokeLinecap="round" opacity="0.5" />
    <path d="M68 40c0-6 4-10 4-10" fill="none" stroke="#e65100" strokeWidth="1" strokeLinecap="round" opacity="0.5" />
    <ellipse cx="55" cy="50" rx="25" ry="3" fill="#e65100" opacity="0.1" />
  </svg>
)

export const GiftBoxIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg width="1em" height="1em" viewBox="0 0 120 120" fill="none" {...props}>
    <rect x="25" y="50" width="70" height="45" rx="6" fill="#ffebee" stroke="#c62828" strokeWidth="1.5" />
    <rect x="20" y="40" width="80" height="15" rx="4" fill="#ef9a9a" stroke="#c62828" strokeWidth="1.5" />
    <line x1="60" y1="40" x2="60" y2="95" stroke="#c62828" strokeWidth="1.5" />
    <path d="M60 40c-5-10-15-15-20-12s-5 12 0 17l20-5z" fill="#c62828" opacity="0.3" />
    <path d="M60 40c5-10 15-15 20-12s5 12 0 17l-20-5z" fill="#c62828" opacity="0.3" />
  </svg>
)

export const BottleIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg width="1em" height="1em" viewBox="0 0 120 120" fill="none" {...props}>
    <rect x="42" y="25" width="36" height="12" rx="3" fill="#e8eaf6" stroke="#3949ab" strokeWidth="1.5" />
    <path d="M42 37h36v8c0 0 8 4 8 12v30c0 6-5 10-10 10H44c-5 0-10-4-10-10V57c0-8 8-12 8-12V37z" fill="#e8eaf6" stroke="#3949ab" strokeWidth="1.5" />
    <rect x="40" y="62" width="40" height="8" rx="2" fill="#3949ab" opacity="0.15" />
    <circle cx="60" cy="80" r="4" fill="#3949ab" opacity="0.2" />
  </svg>
)

// ===== Category illustration SVGs =====
export const MountainHerbIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg width="1em" height="1em" viewBox="0 0 120 120" fill="none" {...props}>
    <path d="M10 90l30-50 20 20 20-35 30 65H10z" fill="#c8e6c9" opacity="0.5" />
    <path d="M60 30c-3 8-8 16-8 28 0 12 4 20 8 24 4-4 8-12 8-24 0-12-5-20-8-28z" fill="#2c6b4f" opacity="0.6" />
    <path d="M48 58c4-2 8-2 12 2 4-4 8-4 12-2-2 10-6 18-12 22-6-4-10-12-12-22z" fill="#2c6b4f" opacity="0.3" />
    <circle cx="60" cy="68" r="2" fill="#2c6b4f" />
  </svg>
)

export const VipCrownIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg width="1em" height="1em" viewBox="0 0 120 120" fill="none" {...props}>
    <path d="M20 75l15-35 25 15 25-15 15 35H20z" fill="#ffd54f" stroke="#f9a825" strokeWidth="1.5" />
    <rect x="20" y="75" width="80" height="12" rx="3" fill="#ffd54f" stroke="#f9a825" strokeWidth="1.5" />
    <circle cx="35" cy="40" r="4" fill="#f9a825" opacity="0.6" />
    <circle cx="60" cy="30" r="5" fill="#f9a825" opacity="0.8" />
    <circle cx="85" cy="40" r="4" fill="#f9a825" opacity="0.6" />
  </svg>
)
