# SKILL: High-End Minimalist Design System (Awwwards Style)

## ?? Design Philosophy
The goal is to create a digital experience that feels like a luxury art gallery: minimal, precise, and focused on high-impact interactions.

## ?? Visual Guidelines
- **Typography**: 
  - Headings: `Playfair Display` (Serif) for authority and elegance.
  - Body: `Inter` (Sans-Serif) for clarity and modernism.
- **Palette**: Strictly monochromatic (Pure Black #000, Pure White #FFF, Muted Grey #666).
- **Spacing**: Generous negative space. Elements should breathe.
- **Images**: High-resolution, mostly grayscale, transitioning to color on hover.

## ? Interaction Patterns
- **The Magnetic Cursor**: 
  - A small dot (cursor) and a fluid follower.
  - Elements marked with `.magnetic` should attract the cursor and slightly shift their position.
- **Text-Masking Reveal**:
  - Headings should be wrapped in a `.text-mask` container (`overflow: hidden`).
  - Use `transform: translateY(100%)` transitioning to `translateY(0)` on scroll.
- **Cinematic Overlays**:
  - Navigation should use a full-screen overlay with staggered animation for links.
- **Smooth Transitions**:
  - Always use `cubic-bezier(0.22, 1, 0.36, 1)` for an "expensive" feel.

## ??? Technical Implementation
- **Animations**: Use `IntersectionObserver` for scroll-triggered reveals.
- **Performance**: Implement a preloader to ensure assets are ready and to create a "premium" entrance.
- **Responsiveness**: Mobile views should maintain the minimalist feel, simplifying the layout but keeping the high-contrast typography.
