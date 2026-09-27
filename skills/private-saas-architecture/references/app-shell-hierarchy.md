# True App-Shell Architecture & Viewport Hierarchy Rules

When designing or refactoring web dashboards and internal command tools (B2B SaaS / Private SaaS):

## 1. The True App-Shell Invariant (Anti-Double Navbar)

A genuine software application dashboard is an operational workbench, NOT a marketing website.

### What to eliminate:
- **Never stack a public landing-page header above an app sidebar**: Having a top menu (`Home`, `Reports`, `Billing`, `Docs`) and a left sidebar with another set of icons creates a confusing, amateurish double navigation that wastes 60–80px of vertical space.
- **Never add long narrative landing-page footers**: A web application ends where its functional workspace ends.
- **Never allow uncontrolled body scrolling**: The outer document frame should be locked (`height: 100vh; overflow: hidden;`).

### True App-Shell Structure:
```
+-----------------------------------------------------------------------------------------------+
| SIDEBAR (240-260px, 100vh) | CONTEXTUAL ACTION BAR (Height ~50-56px, Breadcrumbs & Actions)   |
| Logo / Workspace Switcher  +------------------------------------------------------------------+
| Command Search (⌘K)        | SCROLLABLE / FIT WORKSPACE (Flex: 1, Internal Scroll)            |
| Vertical Nav Module Stack  |  - Row 1: KPI Summary Quad (~125-140px max height)               |
| Pinned Accounts / Status   |  - Row 2: Deep Operational Workspace (Ledger, Chart, Details)   |
| User Profile & Settings    |           Fills remaining viewport height (~460-520px)           |
+----------------------------+------------------------------------------------------------------+
```

## 2. The Holistic Revision Ripple-Effect Rule

When a user or review asks to change the container structure (e.g. *"add a sidebar"*, *"remove top navbar"*):
1. **Calculate the Remaining Workspace Canvas**:
   - On a standard 1440x900 desktop screen, subtracting a 240px sidebar leaves ~1200px horizontal workspace.
2. **Re-calculate Child Aspect Ratios**:
   - A 3-column card row designed for 1440px will become squashed at 1200px, causing card contents to wrap and card height to inflate vertically.
   - If cards inflate to ~360px height, they consume 50% of the entire 1440x900 viewport, pushing the operational table below the fold.
3. **Re-proportion Top Cards to Compact KPI Tiles**:
   - Convert bulky cards into compact KPI metric tiles (~125-140px height).
   - Group high-level summaries horizontally across a 4-column quad.
4. **Allocate Maximum Canvas to Operational Data**:
   - The primary purpose of a dashboard is monitoring and transaction management.
   - Dedicate >=60% of the vertical space to the data grid/table, allowing 7–10 rows to render visibly without an awkward 80-100px micro-scroll.

## 3. Typographic Hierarchy & Anchor Metric

- **Anchor Metric (The North Star)**: The most critical numeric figure (e.g. Net Liquid Balance) MUST be the undisputed visual anchor (`font-size: 24-26px font-mono font-bold/black`).
- **Secondary Metrics**: Sized one level down (`20-22px`).
- **Greeting / Slogan**: Subordinate to the data (`font-size: 14-16px` or compact inline breadcrumb). Never make a casual greeting headline (`"Welcome Back, User"`) larger than the financial/operational data metrics.
- **Table Data Legibility**: Table rows must maintain comfortable vertical padding (`8-10px`, row height ~42-44px) and clear numeric alignment (`font-mono text-right`).
