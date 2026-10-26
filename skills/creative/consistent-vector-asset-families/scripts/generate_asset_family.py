#!/usr/bin/env python3
"""
generate_asset_family.py - Master Procedural SVG Asset Family Generator.
V2 Upgrade: Master Glass Architecture (Double-Wall Refraction, Crescent Specular Ribbons, Solid Crystal Pedestals).
"""

import os
import sys
import argparse

SHARED_DEFS = """
  <defs>
    <!-- Ultra Sharp Metallic Rose Gold Core -->
    <linearGradient id="metalCore" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFF2EE" />
      <stop offset="20%" stop-color="#F0A694" />
      <stop offset="55%" stop-color="#BD634E" />
      <stop offset="85%" stop-color="#782E1E" />
      <stop offset="100%" stop-color="#42150C" />
    </linearGradient>

    <!-- Crystal Clear Glass Hull with Refractive Dark Edge -->
    <linearGradient id="glassHull" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.80" />
      <stop offset="25%" stop-color="#FFFFFF" stop-opacity="0.08" />
      <stop offset="65%" stop-color="#5E2619" stop-opacity="0.22" />
      <stop offset="90%" stop-color="#FFFFFF" stop-opacity="0.20" />
      <stop offset="100%" stop-color="#4A1A10" stop-opacity="0.45" />
    </linearGradient>

    <!-- Razor Sharp Specular Ribbon -->
    <linearGradient id="sharpRibbon" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.95" />
      <stop offset="40%" stop-color="#FFFFFF" stop-opacity="0.60" />
      <stop offset="80%" stop-color="#FFE5DF" stop-opacity="0.10" />
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0.0" />
    </linearGradient>

    <!-- Soft Ambient Ground Shadow with Refractive Caustic Light -->
    <radialGradient id="crystalShadow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#FFD8CE" stop-opacity="0.75" />
      <stop offset="30%" stop-color="#63261A" stop-opacity="0.22" />
      <stop offset="70%" stop-color="#63261A" stop-opacity="0.06" />
      <stop offset="100%" stop-color="#63261A" stop-opacity="0.0" />
    </radialGradient>
  </defs>
"""

def wrap_svg(content, width=400, height=400):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
{SHARED_DEFS}
  <!-- Clean Luxury Backdrop -->
  <rect width="{width}" height="{height}" fill="#FAFAFA" />
{content}
</svg>"""

def subject_vintage_camera():
    return """
  <!-- Ground Caustic Shadow -->
  <ellipse cx="200" cy="335" rx="125" ry="16" fill="url(#crystalShadow)" />
  <ellipse cx="190" cy="335" rx="40" ry="6" fill="#FFFFFF" opacity="0.7" />

  <g id="camera-body">
    <!-- Camera Chassis: Double-Walled Solid Crystal Glass Housing -->
    <rect x="85" y="155" width="230" height="150" rx="18" fill="url(#glassHull)" stroke="#4A1A10" stroke-width="1.2" />
    <!-- Inner Refracted Metal Chamber -->
    <rect x="95" y="165" width="210" height="130" rx="12" fill="url(#metalCore)" opacity="0.9" />

    <!-- Top Solid Rose Gold Mechanism Plate -->
    <path d="M 85 180 L 85 142 C 85 134 92 128 100 128 L 300 128 C 308 128 315 134 315 142 L 315 180 Z" fill="url(#metalCore)" />
    
    <!-- Dials & Mechanical Knurled Knobs -->
    <rect x="115" y="114" width="38" height="14" rx="3" fill="url(#metalCore)" stroke="#FFF2EE" stroke-width="1" />
    <rect x="250" y="118" width="30" height="10" rx="3" fill="url(#metalCore)" />

    <!-- Multi-Tiered Crystal Lens with Domed Sapphire Front -->
    <circle cx="200" cy="230" r="58" fill="url(#metalCore)" />
    <circle cx="200" cy="230" r="48" fill="#36120A" />
    <!-- Inner Lens Aperture Ring -->
    <circle cx="200" cy="230" r="42" fill="url(#metalCore)" />
    
    <!-- Domed Front Glass Element -->
    <circle cx="200" cy="230" r="38" fill="url(#glassHull)" stroke="#FFFFFF" stroke-width="1.5" />
    <!-- Crescent Glare on Lens -->
    <path d="M 175 205 C 190 195 215 195 230 208 C 220 200 200 200 185 208 Z" fill="url(#sharpRibbon)" />
    <ellipse cx="184" cy="214" rx="12" ry="5" fill="#FFFFFF" opacity="0.95" transform="rotate(-35 184 214)" />
    
    <!-- Camera Body Specular Ribbon (Top-Left Edge Light) -->
    <path d="M 90 160 L 310 160" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" opacity="0.8" />
  </g>
"""

def subject_desk_lamp():
    return """
  <!-- Ground Caustic Shadow -->
  <ellipse cx="200" cy="345" rx="95" ry="14" fill="url(#crystalShadow)" />
  <ellipse cx="195" cy="345" rx="30" ry="5" fill="#FFFFFF" opacity="0.75" />

  <g id="desk-lamp">
    <!-- Solid Glass Weighted Pedestal Base with Refracted Metal Inlay -->
    <ellipse cx="200" cy="335" rx="65" ry="14" fill="url(#metalCore)" />
    <ellipse cx="200" cy="331" rx="60" ry="11" fill="url(#glassHull)" stroke="#FFFFFF" stroke-width="1.5" />
    <ellipse cx="185" cy="328" rx="20" ry="5" fill="#FFFFFF" opacity="0.9" />

    <!-- Articulated Rose Gold Arms with Machined Pivot Screws -->
    <line x1="200" y1="325" x2="155" y2="210" stroke="url(#metalCore)" stroke-width="7" stroke-linecap="round" />
    <circle cx="155" cy="210" r="9" fill="url(#metalCore)" stroke="#FFF2EE" stroke-width="1" />
    <line x1="155" y1="210" x2="225" y2="135" stroke="url(#metalCore)" stroke-width="7" stroke-linecap="round" />
    <circle cx="225" cy="135" r="9" fill="url(#metalCore)" stroke="#FFF2EE" stroke-width="1" />

    <!-- Cantilevered Bell Lamp Shade in Crystal Glass with Internal Rose Gold Reflector -->
    <!-- Inner Metallic Core Reflector Cone -->
    <path d="M 225 135 L 265 158 L 240 205 L 200 182 Z" fill="url(#metalCore)" />
    <!-- Outer Blown Glass Shade (Double-Wall Thickness) -->
    <path d="M 222 130 L 278 162 C 285 180 270 215 235 220 L 190 190 C 205 160 215 135 222 130 Z" 
          fill="url(#glassHull)" stroke="#FFFFFF" stroke-width="1.5" />
    
    <!-- Razor Sharp Specular Glare along Cone Shoulder -->
    <path d="M 226 138 L 270 166" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.95" />
    <ellipse cx="232" cy="144" rx="8" ry="3" fill="#FFFFFF" opacity="0.9" transform="rotate(30 232 144)" />
  </g>
"""

def subject_seashell():
    return """
  <!-- Ground Caustic Shadow -->
  <ellipse cx="200" cy="340" rx="115" ry="18" fill="url(#crystalShadow)" />
  <ellipse cx="190" cy="340" rx="35" ry="6" fill="#FFFFFF" opacity="0.8" />

  <g id="seashell">
    <!-- Sculpted Metallic Core Flutes BEHIND Glass -->
    <path d="M 200 325 C 180 250 160 170 175 105" fill="none" stroke="url(#metalCore)" stroke-width="6" stroke-linecap="round" />
    <path d="M 200 325 C 195 240 205 160 215 88" fill="none" stroke="url(#metalCore)" stroke-width="7" stroke-linecap="round" />
    <path d="M 200 325 C 215 250 240 180 255 115" fill="none" stroke="url(#metalCore)" stroke-width="6" stroke-linecap="round" />

    <!-- Solid Crystal Glass Shell Body (Outer Transparent Shell with Refraction) -->
    <path d="M 200 330 C 120 285 70 180 135 115 C 195 55 265 55 295 125 C 335 210 275 295 200 330 Z" 
          fill="url(#glassHull)" stroke="#4A1A10" stroke-width="1" />

    <!-- Inner Wall Refraction Lip -->
    <path d="M 200 320 C 130 278 85 185 142 125 C 195 70 258 70 285 132 C 322 208 268 285 200 320 Z" 
          fill="none" stroke="#FFFFFF" stroke-width="1.8" opacity="0.75" />

    <!-- Razor Sharp Specular Wave Highlights (Simulating Curved Glass Grooves) -->
    <path d="M 140 130 C 170 95 220 90 260 130" fill="none" stroke="url(#sharpRibbon)" stroke-width="3.5" stroke-linecap="round" />
    <ellipse cx="170" cy="110" rx="14" ry="5" fill="#FFFFFF" opacity="0.95" transform="rotate(-20 170 110)" />
    
    <!-- Thick Glass Hinge Base at Bottom -->
    <ellipse cx="200" cy="326" rx="24" ry="8" fill="url(#metalCore)" />
    <ellipse cx="200" cy="324" rx="20" ry="6" fill="#FFFFFF" opacity="0.6" />
  </g>
"""

def subject_cocktail_glass():
    return """
  <!-- Ground Caustic Shadow -->
  <ellipse cx="200" cy="350" rx="90" ry="14" fill="url(#crystalShadow)" />
  <ellipse cx="192" cy="350" rx="30" ry="5" fill="#FFFFFF" opacity="0.85" />

  <g id="cocktail-glass">
    <!-- Solid Metallic Base Plate -->
    <ellipse cx="200" cy="340" rx="60" ry="9" fill="url(#metalCore)" />
    <ellipse cx="200" cy="338" rx="55" ry="7" fill="#FFFFFF" opacity="0.45" />

    <!-- Slender Rose Gold Stem -->
    <path d="M 197 338 L 198 205 L 202 205 L 203 338 Z" fill="url(#metalCore)" />

    <!-- SOLID CRYSTAL JUNCTION KNOB (Translucent Bridge between Stem and Bowl) -->
    <circle cx="200" cy="204" r="7" fill="url(#glassHull)" stroke="#FFFFFF" stroke-width="1.5" />
    <circle cx="198" cy="202" r="2.5" fill="#FFFFFF" />

    <!-- SOLID METALLIC LIQUID CORE (With Refraction Meniscus inside Glass) -->
    <path d="M 128 120 C 150 170 175 200 200 200 C 225 200 250 170 272 120 Z" fill="url(#metalCore)" />
    <ellipse cx="200" cy="120" rx="72" ry="14" fill="url(#metalCore)" />
    <ellipse cx="200" cy="120" rx="68" ry="11" fill="#FFF0EC" opacity="0.55" />

    <!-- CRYSTAL CLEAR GLASS OUTER HULL (Wall Thickness 8px) -->
    <path d="M 115 90 C 145 165 175 208 200 208 C 225 208 255 165 285 90 C 260 85 140 85 115 90 Z" 
          fill="url(#glassHull)" stroke="#4A1A10" stroke-width="1.2" />

    <!-- Top Rim of the Glass (Double Oval showing thickness) -->
    <ellipse cx="200" cy="90" rx="85" ry="18" fill="none" stroke="#4A1A10" stroke-width="1.5" opacity="0.4" />
    <ellipse cx="200" cy="90" rx="80" ry="14" fill="url(#glassHull)" stroke="#FFFFFF" stroke-width="2" />

    <!-- RAZOR SHARP SPECULAR REFLECTION RIBBONS -->
    <path d="M 118 96 C 145 158 170 196 195 204 C 188 200 162 160 130 102 Z" fill="url(#sharpRibbon)" />
    <ellipse cx="125" cy="102" rx="12" ry="4" fill="#FFFFFF" opacity="0.95" transform="rotate(-30 125 102)" />

    <!-- Right Rim Light Glare -->
    <path d="M 282 96 C 258 155 235 195 206 202 C 212 198 235 160 268 102 Z" fill="#FFFFFF" opacity="0.35" />
  </g>
"""

def subject_wristwatch():
    return """
  <!-- Ground Shadow -->
  <ellipse cx="200" cy="345" rx="85" ry="14" fill="url(#crystalShadow)" />

  <g id="wristwatch">
    <!-- Metallic Straps with Natural Ergonomic Curved Ends (Not Rigid Cuts) -->
    <path d="M 165 70 C 180 65 220 65 235 70 L 230 135 L 170 135 Z" fill="url(#metalCore)" />
    <!-- Lower Strap with Subtle Curved Ground Flare -->
    <path d="M 170 265 L 230 265 L 236 330 C 220 336 180 336 164 330 Z" fill="url(#metalCore)" />

    <!-- Multi-Tiered Beveled Metal Bezel Casing -->
    <circle cx="200" cy="200" r="70" fill="url(#metalCore)" />
    <circle cx="200" cy="200" r="62" fill="#36120A" />
    <circle cx="200" cy="200" r="58" fill="url(#metalCore)" />

    <!-- Deep Sunburst Dial Face -->
    <circle cx="200" cy="200" r="52" fill="#5E2619" />
    
    <!-- Machined Metallic Hands & Crown -->
    <rect x="268" y="196" width="7" height="9" rx="2" fill="url(#metalCore)" />
    <line x1="200" y1="200" x2="200" y2="168" stroke="#FFF2EE" stroke-width="3" stroke-linecap="round" />
    <line x1="200" y1="200" x2="226" y2="200" stroke="#F0A694" stroke-width="2" stroke-linecap="round" />
    <circle cx="200" cy="200" r="4" fill="#FFF2EE" />

    <!-- DOMED SAPPHIRE CRYSTAL GLASS (Master Curved Reflection) -->
    <circle cx="200" cy="200" r="52" fill="url(#glassHull)" stroke="#FFFFFF" stroke-width="1.5" />
    
    <!-- Crescent Domed Specular Glare -->
    <path d="M 165 165 C 200 148 235 165 242 182 C 228 166 192 158 170 174 Z" fill="url(#sharpRibbon)" />
    <ellipse cx="172" cy="168" rx="14" ry="5" fill="#FFFFFF" opacity="0.95" transform="rotate(-40 172 168)" />
    <path d="M 235 235 C 210 248 180 242 165 228 C 180 238 210 241 230 230 Z" fill="#FFFFFF" opacity="0.35" />
  </g>
"""

def generate_family(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    subjects = {
        "vintage_camera": subject_vintage_camera(),
        "desk_lamp": subject_desk_lamp(),
        "seashell": subject_seashell(),
        "cocktail_glass": subject_cocktail_glass(),
        "wristwatch": subject_wristwatch(),
    }

    generated_paths = []
    for name, content in subjects.items():
        svg_code = wrap_svg(content)
        path = os.path.join(output_dir, f"{name}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg_code)
        generated_paths.append(path)

    showcase_w = 1200
    showcase_h = 450
    showcase_cells = []
    keys = list(subjects.keys())
    for i, k in enumerate(keys):
        cell_x = 40 + i * 230
        cell_y = 60
        showcase_cells.append(f"""
    <g transform="translate({cell_x}, {cell_y}) scale(0.55)">
      {subjects[k]}
      <text x="200" y="380" font-family="'JetBrains Mono', sans-serif" font-size="22" font-weight="600" fill="#8B4F3E" text-anchor="middle">
        {k.replace('_', ' ').title()}
      </text>
    </g>
""")

    master_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {showcase_w} {showcase_h}" width="{showcase_w}" height="{showcase_h}">
{SHARED_DEFS}
  <!-- Clean Gallery Backdrop -->
  <rect width="{showcase_w}" height="{showcase_h}" fill="#FFFFFF" />
  
  <!-- Header Branding -->
  <text x="40" y="44" font-family="'Inter', sans-serif" font-size="20" font-weight="800" fill="#1A1C20" letter-spacing="0.05em">
    BEKVISUAL · ASSET FAMILY
  </text>
  <text x="{showcase_w - 40}" y="44" font-family="'JetBrains Mono', monospace" font-size="13" font-weight="600" fill="#BD634E" text-anchor="end">
    MASTER GLASS ARCHITECTURE (ROSE GOLD &amp; CRYSTAL)
  </text>
  <line x1="40" y1="58" x2="{showcase_w - 40}" y2="58" stroke="#EFEFEF" stroke-width="1.5" />

  {''.join(showcase_cells)}
</svg>"""

    showcase_path = os.path.join(output_dir, "asset_family_showcase.svg")
    with open(showcase_path, "w", encoding="utf-8") as f:
        f.write(master_svg)
    generated_paths.append(showcase_path)

    return generated_paths

def main():
    parser = argparse.ArgumentParser(description="Procedural SVG Asset Family Generator")
    parser.add_argument("--style", default="rose_gold", help="Material style preset (default: rose_gold)")
    parser.add_argument("--output-dir", default="/tmp/asset_family", help="Destination folder")
    parser.add_argument("--verify", action="store_true", help="Run automated integrity check")

    args = parser.parse_args()
    paths = generate_family(args.output_dir)

    if args.verify:
        assert len(paths) == 6, f"Expected 6 SVGs generated, found {len(paths)}"
        for p in paths:
            assert os.path.getsize(p) > 200, f"File {p} is too small or empty"
        print("All 5 asset family SVGs generated and validated successfully")
    else:
        print(f"Generated {len(paths)} assets in {args.output_dir}:")
        for p in paths:
            print(" -", p)

if __name__ == "__main__":
    main()
