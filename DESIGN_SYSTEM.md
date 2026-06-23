# Astro Horoscope - Design System (Issue #77)

## Overview
Complete design specifications for the redesigned layout featuring a bento grid layout with responsive mobile, tablet, and desktop views. The design supports both dark and light themes.

---

## Color Scheme

### Dark Theme (Primary)
- **Background Gradient**: Navy to darker navy (`--bg-gradient-start: #1a1a2e`, `--bg-gradient-end: #16213e`)
- **Primary Accent (Cyan/Turquoise)**: `#00CED1` or bright cyan `#00FFFF`
  - Used for: Headings, links, highlights, borders, accents
  - Examples: "cosmic vibe" text, section labels (DAILY, COSMIC CRAVINGS, CHAT), icon strokes
- **Text Primary**: `#FFFFFF` (White)
- **Text Secondary**: Light gray `#a1a1aa`
- **Card Background**: Slightly lighter navy `#18181b` or `#1a1a24`
- **Border Color**: Cyan/turquoise with rounded corners (12-16px radius)
- **Icon Colors**:
  - Primary icons (action buttons): Purple/Violet `#9333ea` or similar
  - Accent icons (informational): Cyan/turquoise
- **Decorative Stars**: Mixed cyan and purple/blue sparkles
- **Selection/Highlight**: Magenta/pink `#ea66cd`

### Light Theme (Secondary)
- **Background**: Very pale cyan-tinted white or `#f0f9ff`
- **Card Background**: White `#ffffff` or very light gray
- **Text Primary**: Dark gray/black `#1a1a1a` or `#333333`
- **Text Secondary**: Medium gray `#666666`
- **Border Color**: Light cyan or light gray borders
- **Accent Colors**: Same cyan/turquoise maintained for consistency
- **Overall**: Inverted colors from dark theme while maintaining cyan accent throughout

### Accessibility
- Selection Background: `#ea66cd` (magenta/pink)
- Selection Text: `#ffffff` (dark mode) / `#2d3748` (light mode)
- Sufficient contrast maintained on both themes

---

## Typography

### Font Families (via @fontsource packages)

| Role | Font Family | Package | Weights | CSS Token |
|------|-------------|---------|---------|-----------|
| Display (headings, logo, hero) | Space Grotesk | @fontsource/space-grotesk | 400, 500, 700 | var(--font-display) / font-display utility |
| Body (paragraphs, UI text) | DM Sans | @fontsource/dm-sans | 400, 500, 700 | var(--font-sans) / Tailwind default sans |
| Mono (eyebrows, meta, stat labels, code-like pills) | JetBrains Mono | @fontsource/jetbrains-mono | 400, 500 | var(--font-mono) / font-mono utility |

### Installation
```bash
bun add @fontsource/space-grotesk @fontsource/dm-sans @fontsource/jetbrains-mono
```
Then @import each weight in global stylesheet (see src/styles.css top of file).

---

## Icons

**Pack**: [lucide-react](https://lucide.dev/) — only pack used, no mixing

**Icons Referenced**:
- Sun
- Moon
- Sparkles
- BellRing
- MessageCircleQuestion
- ArrowUpRight
- ArrowLeft
- Pencil
- Settings2
- Send

**Icon Styling**:
- **strokeWidth**: `1.5` for hero/tile icons, default `2` elsewhere
- **Size**: Via Tailwind utilities (h-4 w-4, h-5 w-5, h-6 w-6)
- **Colors**: Primarily cyan for informational, purple for action buttons

---

## Responsive Layout - Bento Grid

### Viewport Breakpoints
- **Mobile**: 390w (viewport width)
- **Tablet**: 834w
- **Desktop**: 1440w

Theme = dark|light, Size = mobile (390w), tablet (834w), desktop (1440w)

### Mobile Layout (390w)
**Structure**: Single-column full-width stack

**Components (top to bottom)**:
1. Header Section
   - Logo "astro-horoscope" with cyan accent
   - "Edit chart" button (top-right, cyan border)
   - "Your cosmic vibe check" hero title (with "cosmic vibe" in cyan)
   - Description text

2. Bento Grid Tiles (full width, stacked):
   - "Ask the stars" (CHAT WITH THE COSMOS section)
   - "The sky is listening" (with suggested prompts and input field)
   - "Today's reading" (DAILY section with content)
   - "Your Taco Bell order" (COSMIC CRAVINGS section)
   - "Ask the stars" (CHAT section)

3. Footer
   - "BUILT UNDER A WAXING CRESCENT" with decorative plus signs

**Tile Styling**:
- Full width with padding/margins
- Rounded corners (border-radius: 12-16px)
- Cyan/turquoise borders (2px)
- Icon in top-left (sun, bell, question mark, etc.)
- External link icon in top-right (ArrowUpRight)
- Heading in larger text (Space Grotesk)
- Description text in smaller gray
- Padding: ~20-24px internal
- Margin between tiles: ~16-20px

### Tablet Layout (834w)
**Structure**: Multi-column grid (appears to be 2-column or similar)

**Key Changes**:
- Components begin to layout in columns
- Some tiles remain full-width
- Better spacing utilization
- Possible side-by-side placement of smaller tiles

### Desktop Layout (1440w)
**Structure**: Full bento grid (3+ columns, variable sizing)

**Grid Structure** (observed from screenshots):
```
┌─────────────────────────────────────────────────┐
│  Zodiac Pills Row (Cancer, Virgo, Capricorn)   │
│  Placements Table (BODY | SIGN | HOUSE)         │
├──────────────────────────────────┬──────────────┤
│  "Your cosmic vibe check" Hero   │              │
├──────────────────────────────────┤              │
│                                  │              │
│  Today's Reading (Left, Large)   │ Full Birth   │
│  (~50% width or column-span 2)   │ Chart        │
│                                  │ (Top-right)  │
├──────────────────┬───────────────┤              │
│ Cosmic Cravings  │ Ask the stars │              │
│ (Taco Bell)      │ (Chat)        │              │
└──────────────────┴───────────────┴──────────────┘
```

**Tile Sizing**:
- Large tiles: Span 2 columns or wider
- Small tiles: Single column width
- Hero section: Full width or multi-column span
- Consistent gaps between grid items (~16-24px)

**Grid Properties**:
- Display: CSS Grid or similar
- Gap: 16-24px (consistent spacing)
- Max-width: 1440px (desktop) or similar
- Margin: auto (center on larger screens)

---

## Component Styling

### Hero Section ("Your cosmic vibe check")
- **Layout**: Full width
- **Background**: Card background color (navy with slight transparency or solid)
- **Border**: Optional subtle border, rounded corners
- **Title Text**:
  - Font: Space Grotesk, Weight: 500-700, Size: 32-48px
  - Color: White with "cosmic" and "vibe" highlighted in cyan
  - Line-height: 1.2-1.3
- **Description Text**:
  - Font: DM Sans, Weight: 400, Size: 14-16px
  - Color: Light gray
  - Max-width: 600px

### "Edit Chart" Button
- **Style**: Ghost/outline button
- **Border**: 2px cyan/turquoise
- **Border-radius**: 24-32px (pill shape)
- **Padding**: 10-12px 20-24px
- **Text**: White, DM Sans 500
- **Position**: Top-right of hero section or inline
- **Hover**: Slight glow, lighter background, maintain border
- **Icon**: Pencil icon (Lucide)

### Bento Grid Tiles
**Base Styling**:
- **Border**: 2px solid cyan/turquoise
- **Border-radius**: 12-16px
- **Background**: Card background (navy)
- **Padding**: 20-24px
- **Box-shadow**: None or very subtle (0 1px 3px rgba(0,0,0,0.1)) on dark
- **Transition**: All 0.3s ease (for hover effects)

**Tile Components**:

1. **Top Section (Icon + External Link)**:
   - Flexbox between space-between
   - Icon (left): Cyan colored, size h-5 w-5 or h-6 w-6
   - External link icon (right): ArrowUpRight, cyan, smaller size h-4 w-4
   - Optional: Label text (mono font) above icon (e.g., "CHAT WITH THE COSMOS", "DAILY")
     - Font: JetBrains Mono, weight 500, size 12px, color: cyan/turquoise
     - Letter-spacing: 1-2px (uppercase)

2. **Title**:
   - Font: Space Grotesk, Weight: 500-700, Size: 18-24px
   - Color: White
   - Margin: 8-12px below icon section
   - Line-height: 1.2

3. **Description**:
   - Font: DM Sans, Weight: 400, Size: 14px
   - Color: Light gray/secondary text
   - Margin: 8px below title
   - Line-height: 1.4-1.5

**Hover Effects**:
- Shadow elevation: 0 8-12px 24px rgba(0,206,209,0.15) (cyan glow)
- Transform: translateY(-4px) (slight lift)
- Optional: Slight border glow or opacity increase

### Section Labels (Eyebrows)
- **Font**: JetBrains Mono, Weight: 500, Size: 11-12px
- **Color**: Cyan/turquoise
- **Text-transform**: uppercase
- **Letter-spacing**: 1.5-2px
- **Margin-bottom**: 12px
- **Placement**: Above title in each tile

### Input Field ("Ask anything...")
- **Style**: Rounded large input
- **Border**: 2px cyan/turquoise
- **Border-radius**: 24-32px (pill shape)
- **Background**: Slightly lighter navy or transparent
- **Padding**: 12-16px 20px (with room for button)
- **Placeholder**: "Ask anything..." in gray
- **Placeholder-color**: `#6b7280` or similar
- **Font**: DM Sans, 400, 14-16px
- **Color**: White
- **Focus**: Border color lighter, slight shadow

### Send Button (Inside Input)
- **Position**: Absolute right inside input
- **Style**: Circular or rounded square
- **Background**: Purple/violet `#9333ea` or similar
- **Color**: White (icon)
- **Size**: h-8 w-8 to h-10 w-10
- **Icon**: Send icon (Lucide)
- **Border**: None
- **Border-radius**: 8-12px or 50%
- **Cursor**: pointer
- **Hover**: Slightly lighter purple, subtle shadow

### Suggested Prompt Buttons
- **Style**: Outline/ghost buttons
- **Border**: 2px cyan/turquoise
- **Border-radius**: 24px (pill shape)
- **Background**: Transparent
- **Padding**: 8-10px 16-20px
- **Text**: DM Sans 400, 13-14px, white
- **Layout**: Horizontal list, wrapped if needed, gap 8-12px
- **Hover**: Light cyan background, glow effect

### Placements Table
- **Font**: DM Sans 400
- **Header Row**:
  - Font-weight: 500
  - Color: Cyan/turquoise
  - Background: Slightly darker or transparent
  - Text-transform: uppercase
  - Font-size: 12px
  - Letter-spacing: 0.5px
- **Data Rows**:
  - Color: White
  - Border-bottom: 1px solid rgba(0,206,209,0.1)
  - Padding: 10-12px per cell
- **Cell Alignment**: Left-aligned, with some right alignment for numbers
- **Striped Rows**: Optional alternate background color (very subtle)

### Zodiac Pills/Badges
- **Style**: Rounded pill buttons
- **Border**: 2px cyan/turquoise
- **Background**: Transparent or very light
- **Padding**: 8-10px 16-20px
- **Font**: DM Sans 500, 13-14px
- **Color**: White (text) / Cyan (border)
- **Display**: Horizontal inline-flex, gap 8-12px
- **Hover**: Light cyan background

### Decorative Elements
- **Stars**: Scattered throughout design
  - Colors: Cyan and purple/blue mix
  - Icons: Star-like shapes (Lucide Sparkles)
  - Opacity: 0.6-0.8
  - Positioned: Absolute or semi-relative for visual interest
- **Footer Text**: "BUILT UNDER A WAXING CRESCENT"
  - Font: JetBrains Mono, 12px, centered
  - Color: Cyan with decorative plus signs (+) on sides
  - Format: `+ BUILT UNDER A WAXING CRESCENT +`

---

## Spacing & Sizing Guide

### Padding
- Container outer padding: 20-24px (mobile), 32px (tablet/desktop)
- Tile/Card padding: 20-24px
- Small elements padding: 8-12px

### Margins
- Between sections: 24-32px
- Between tiles in grid: 16-20px
- Between elements within tile: 8-16px

### Border Radius
- Large elements (tiles, hero): 12-16px
- Buttons/pills: 24-32px
- Input fields: 24-32px

### Shadows
- Subtle: `0 1px 3px rgba(0,0,0,0.1)`
- Card hover: `0 8-12px 24px rgba(0,206,209,0.15)` (cyan glow)
- Focus states: `0 0 0 3px rgba(0,206,209,0.3)` (outline glow)

---

## Edit Chart Slide-Over (Referenced but not detailed in screenshots)

**Expected Specifications**:
- **Type**: Modal/Slide-over panel (likely right-slide overlay)
- **Trigger**: "Edit chart" button in hero section
- **Background**: Semi-transparent dark overlay on main content
- **Panel Styling**:
  - Background: Card background color (navy)
  - Border: Cyan/turquoise left border (4-6px) optional
  - Border-radius: 12px top corners or full
  - Shadow: `0 -4px 12px rgba(0,0,0,0.3)` or larger
  - Width: Full on mobile, ~400-500px on tablet/desktop
- **Content**:
  - Header: "Edit Chart" title with close button (X)
  - Form fields: Location, birth time, date, etc.
  - Buttons: Cancel/Close (ghost), Save (solid cyan)
- **Animation**: Slide-in from right, 0.3-0.4s ease
- **Close triggers**: Close button, Escape key, click outside

---

## CSS Classes & Tokens

### Root Variables (Dark Mode)
```css
:root {
    --bg-gradient-start: #1a1a2e;
    --bg-gradient-end: #16213e;
    --container-bg: #0f1419;
    --text-color: #e4e4e7;
    --text-secondary: #a1a1aa;
    --text-tertiary: #d4d4d8;
    --border-color: #27272a;
    --section-bg: #1a1a24;
    --card-bg: #18181b;
    --input-bg: #27272a;
    --primary-accent: #00CED1; /* Cyan */
    --secondary-accent: #9333ea; /* Purple */
    --font-display: 'Space Grotesk';
    --font-sans: 'DM Sans';
    --font-mono: 'JetBrains Mono';
}
```

### Recommended Utility Classes
- `bento-grid`: CSS Grid container
- `bento-tile`: Individual grid tile
- `bento-tile--large`: Larger tile (span 2 columns)
- `bento-tile--small`: Smaller tile (single column)
- `eyebrow`: Section label styling
- `button-primary`: Cyan border, white text
- `button-secondary`: Purple background
- `button-ghost`: Transparent border
- `input-base`: Standard input styling
- `card-hover`: Hover effects for cards

---

## Implementation Notes

### Mobile-First Approach
1. Design mobile at 390w
2. Tablet breakpoint at 834w (add multi-column)
3. Desktop breakpoint at 1440w (full bento grid)
4. Use CSS Grid for bento layout with auto-fit/auto-fill

### Performance
- Optimize decorative SVG/icons for web
- Lazy-load images/content
- Use CSS transitions (not animations) for smooth effects
- Minimize shadow/blur effects on mobile

### Accessibility
- Ensure 4.5:1 contrast ratio on all text
- Provide focus states on all interactive elements (ring: cyan)
- Use semantic HTML
- Alt text for all icons
- Keyboard navigation support

### Dark/Light Theme Toggle
- Use CSS custom properties for easy switching
- Smooth transitions on theme change (0.3s)
- Persist user preference (localStorage)
- Respect system preference (prefers-color-scheme media query)

---

## Color Reference Card

| Element | Dark Theme | Light Theme | Hex Code (Dark) |
|---------|-----------|-------------|-----------------|
| Primary Background | Navy | Pale Cyan | #1a1a2e |
| Primary Text | White | Dark Gray | #ffffff |
| Accent (Cyan) | Cyan | Cyan | #00CED1 |
| Accent (Purple) | Purple | Purple | #9333ea |
| Card Background | Navy | White | #18181b |
| Border | Cyan | Light Cyan | #00CED1 |
| Hover Shadow | Cyan Glow | Light Cyan | rgba(0,206,209,0.15) |
| Disabled Text | Gray | Medium Gray | #a1a1aa |

---

## Testing Checklist

- [ ] All text meets contrast requirements on both themes
- [ ] Layout responsive at all three breakpoints
- [ ] Hover effects smooth and visible on tiles
- [ ] Input fields and buttons accessible via keyboard
- [ ] Icons render correctly across browsers
- [ ] Fonts load correctly from @fontsource
- [ ] Theme toggle works smoothly
- [ ] Edit chart button opens modal/slide-over correctly
- [ ] Responsive images/charts scale properly
- [ ] No layout shifts during font load
