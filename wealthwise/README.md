# WealthWise - Responsive Investment Website

A modern, fully responsive investment platform website built with HTML, CSS, and JavaScript. Features a sleek design with real-time market data simulation, investment calculator, and mobile-first responsive layout.

## Features

- **Modern Hero Section** - Eye-catching design with animated gradient background and interactive dashboard mockup
- **Live Market Overview** - Real-time market data cards with simulated price updates
- **Investment Calculator** - Compound interest calculator with animated results
- **Responsive Design** - Fully responsive layout that works on desktop, tablet, and mobile
- **Mobile Navigation** - Hamburger menu with smooth animations
- **Scroll Animations** - Fade-in effects as you scroll through sections
- **Feature Cards** - Grid layout showcasing platform capabilities
- **Testimonials** - Customer review section with star ratings
- **Contact CTA** - Call-to-action section with trust badges

## Tech Stack

- HTML5
- CSS3 (with CSS Variables, Grid, Flexbox)
- Vanilla JavaScript (ES6+)
- Font Awesome Icons
- Google Fonts (Inter)

## Getting Started

### Local Development

1. Clone or download this repository
2. Open `index.html` in your browser
3. No build process required - it's ready to go!

### Deploy to Vercel

#### Option 1: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to project directory
cd investment-website

# Deploy
vercel
```

#### Option 2: Vercel Dashboard (Drag & Drop)

1. Go to [vercel.com](https://vercel.com) and sign up/log in
2. Click "Add New..." > "Project"
3. Select "Import Git Repository" or use "Upload" option
4. If uploading, zip the project folder and upload it
5. Vercel will automatically detect it as a static site
6. Click "Deploy"
7. Your site will be live in seconds!

#### Option 3: Git Repository

1. Push this code to a GitHub/GitLab/Bitbucket repository
2. Connect your repository to Vercel
3. Vercel will auto-deploy on every push to main

## Project Structure

```
investment-website/
├── index.html          # Main HTML file
├── styles.css          # All styles (responsive + animations)
├── script.js           # Interactive features & calculator
├── README.md           # This file
└── vercel.json         # Vercel configuration (optional)
```

## Customization

### Colors
Edit CSS variables in `styles.css`:

```css
:root {
    --primary-color: #6366f1;
    --secondary-color: #10b981;
    --gradient-start: #6366f1;
    --gradient-end: #8b5cf6;
    /* ... more variables */
}
```

### Content
Simply edit the HTML in `index.html` to update text, add sections, or modify content.

### Calculator
The investment calculator uses compound interest formula. Modify the calculation logic in `script.js`:

```javascript
function calculateInvestment() {
    // Custom calculation logic
}
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- No external JavaScript frameworks - lightweight and fast
- Optimized CSS with minimal redundancy
- Lazy loading ready (add `loading="lazy"` to images)
- Responsive images support

## License

MIT License - feel free to use for personal or commercial projects.

## Credits

- Icons: [Font Awesome](https://fontawesome.com)
- Font: [Google Fonts - Inter](https://fonts.google.com/specimen/Inter)
