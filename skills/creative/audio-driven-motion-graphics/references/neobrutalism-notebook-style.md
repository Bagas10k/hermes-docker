# Neobrutalism & Digital Notebook Visual Style

Token definitions and styling recipes for educational vertical reels (TikTok / Reels / Shorts).

## Color Tokens

```typescript
export const PALETTE = {
  bgGrid: '#F5F2EB',       // Warm cream graph paper background
  gridLine: '#E0DDD4',     // Subtle 1px grid coordinate lines
  inkBlack: '#1A1A1A',     // Primary border and text ink
  cardWhite: '#FFFFFF',    // Crisp bento card surface
  highlighterYellow: '#FFEB3B', // Neon accent highlighter
  stampRed: '#E63946',     // Verification / archive badge red
  accentBlue: '#2A9D8F',   // Supporting secondary metric color
  tapeYellow: 'rgba(245, 236, 180, 0.82)', // Semi-translucent masking tape
};
```

## CSS / Inline Style Patterns

### 1. Graph Paper Background
```css
background-color: #F5F2EB;
background-image: 
  linear-gradient(#E0DDD4 1px, transparent 1px),
  linear-gradient(90deg, #E0DDD4 1px, transparent 1px);
background-size: 40px 40px;
```

### 2. Bento Card with Hard Shadow
```css
background: #FFFFFF;
border: 3.5px solid #1A1A1A;
border-radius: 20px;
box-shadow: 8px 8px 0px rgba(26, 26, 26, 0.12);
padding: 32px;
position: relative;
```

### 3. Masking Tape Corner Accent
```tsx
export const MaskingTape: React.FC = () => (
  <div style={{
    position: 'absolute',
    top: -14,
    left: 28,
    width: 90,
    height: 28,
    background: 'rgba(245, 236, 180, 0.85)',
    border: '1px solid rgba(200, 190, 140, 0.4)',
    transform: 'rotate(-3.5deg)',
    boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
    zIndex: 10,
  }} />
);
```

### 4. Dynamic Yellow Highlighter Wipe
```tsx
const widthPercent = interpolate(frame, [start, end], [0, 100], {
  extrapolateLeft: 'clamp',
  extrapolateRight: 'clamp',
});

<span style={{ position: 'relative', display: 'inline-block' }}>
  <span style={{
    position: 'absolute',
    left: 0,
    bottom: 2,
    height: '42%',
    width: `${widthPercent}%`,
    backgroundColor: '#FFEB3B',
    zIndex: 0,
    borderRadius: 2,
  }} />
  <span style={{ position: 'relative', zIndex: 1, fontWeight: 800 }}>
    {text}
  </span>
</span>
```

### 5. Floating Number / Counter Badge
```tsx
<div style={{
  display: 'inline-flex',
  alignItems: 'center',
  padding: '6px 14px',
  background: '#1A1A1A',
  color: '#FFFFFF',
  borderRadius: 999,
  fontFamily: 'JetBrains Mono, monospace',
  fontSize: 14,
  fontWeight: 700,
  letterSpacing: '0.08em',
}}>
  FAKTA {current}/{total}
</div>
```
