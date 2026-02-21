# UI/UX Architecture & User Flow Documentation

**AI Data Dictionary Agent - Design System & User Experience**

Version: 1.0  
Last Updated: February 21, 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Information Architecture](#information-architecture)
4. [User Personas & Journeys](#user-personas--journeys)
5. [Page Structure & Layout](#page-structure--layout)
6. [Component Architecture](#component-architecture)
7. [User Flows](#user-flows)
8. [Interaction Patterns](#interaction-patterns)
9. [Navigation System](#navigation-system)
10. [Responsive Design](#responsive-design)
11. [Accessibility](#accessibility)
12. [Visual Design System](#visual-design-system)

---

## Overview

The AI Data Dictionary Agent is designed as a dual-audience platform serving both **Business Data Analysts** and **Data Engineers**. The UI/UX architecture prioritizes:

- **Quick discovery** for analysts who need to find data fast
- **Deep inspection** for engineers who need full context
- **AI-assisted workflows** to reduce manual work
- **Visual lineage** to understand data relationships
- **Real-time collaboration** through shared sessions

### Core User Flows

1. **Database Connection & Discovery** (5 min setup)
2. **Schema Exploration & Search** (2-3 min to find tables)
3. **AI-Powered Chat** (20 sec SQL generation)
4. **Quality Analysis & Monitoring** (drill-down investigation)
5. **Lineage Visualization** (impact analysis)

---

## Design Principles

### 1. **Progressive Disclosure**
- Show essential information first (table names, descriptions)
- Hide technical details behind expand/hover (column types, indexes)
- Use tabs to separate concerns (Overview, Quality, Lineage, Documentation)

### 2. **Contextual Assistance**
- AI chat always available in sidebar/bottom drawer
- Inline help tooltips on technical terms
- Suggested next actions based on current context

### 3. **Feedback & Status**
- Loading states for long-running tasks (schema extraction, quality analysis)
- Progress indicators with time estimates
- Success/error notifications with actionable messages

### 4. **Search-First Navigation**
- Global search (Cmd/Ctrl+K) as primary discovery method
- Faceted search with filters (schemas, table types, tags)
- Hybrid search (exact match + semantic similarity)

### 5. **Visual Hierarchy**
- Critical data (table names, quality scores) in large, bold text
- Secondary info (row counts, last updated) in smaller, muted text
- Interactive elements (links, buttons) with clear affordance

---

## Information Architecture

### Site Map

```
Root (/)
├── Dashboard (/dashboard)
│   ├── Recent Activity
│   ├── Quality Overview
│   └── Quick Actions
│
├── Databases (/databases)
│   ├── Database List
│   ├── Add Database (/databases/new)
│   └── Database Details (/databases/:id)
│       ├── Overview
│       ├── Schemas (/databases/:id/schemas/:schema)
│       │   ├── Tables List
│       │   └── Table Details (/databases/:id/tables/:table)
│       │       ├── Overview Tab
│       │       ├── Columns Tab
│       │       ├── Quality Tab
│       │       ├── Lineage Tab
│       │       └── Documentation Tab
│       └── Settings
│
├── Quality (/quality)
│   ├── Quality Dashboard
│   ├── Metrics Overview
│   ├── Alerts (/quality/alerts)
│   └── Rules (/quality/rules)
│
├── Lineage (/lineage)
│   ├── Graph View
│   └── Table Impact Analysis
│
├── Documentation (/documentation)
│   ├── Auto-Generated Docs
│   └── Manual Documentation
│
├── Chat (/chat)
│   ├── New Session
│   ├── Session History (/chat/:sessionId)
│   └── Saved Queries
│
├── Export (/export)
│   ├── Export History
│   └── New Export
│
└── Settings (/settings)
    ├── Profile
    ├── Preferences
    ├── API Keys
    └── Audit Log
```

---

## User Personas & Journeys

### Maria - Business Data Analyst

**Primary Goals:**
1. Find relevant tables quickly
2. Understand business context without deep technical knowledge
3. Generate SQL queries with AI assistance
4. Trust data quality before analysis

**Key User Journeys:**

#### Journey 1: New Analyst Onboarding (First Time User)
1. **Entry:** Receives invite link, lands on empty dashboard
2. **Discovery:** Sees "Connect Your First Database" prompt
3. **Connection:** Fills simple form (host, port, database, credentials)
4. **Wait:** Watches progress bar (5-10 min schema extraction)
5. **Explore:** Browses tables with search, clicks on `orders` table
6. **Learn:** Reads AI-generated description, sees sample data
7. **Generate SQL:** Opens chat, asks "Show me orders from last month"
8. **Execute:** Copies SQL, runs in their SQL client
9. **Success:** Saves useful tables to favorites

#### Journey 2: Daily Data Search
1. **Entry:** Opens app, uses global search (Cmd+K)
2. **Search:** Types "customer purchase history"
3. **Results:** Sees semantic matches (orders, customers, order_items)
4. **Filter:** Adds filter "schema: public"
5. **Select:** Clicks `order_items` table
6. **Verify:** Checks quality score (95% - green badge)
7. **Export:** Clicks "Export DDL" for documentation

#### Journey 3: Quality Investigation
1. **Entry:** Receives email alert "NULL spike in payment_value"
2. **Navigate:** Clicks alert link → payments table quality tab
3. **Analyze:** Sees trend chart showing 5% → 25% NULL increase
4. **Drill-down:** Filters by date range, sees issue started 3 days ago
5. **Chat:** Asks "Why are payment_value NULLs increasing?"
6. **Insight:** AI suggests checking upstream order_items table
7. **Lineage:** Switches to lineage tab, traces dependencies
8. **Report:** Exports quality report, shares with team

### Carlos - Data Engineer

**Primary Goals:**
1. Keep documentation updated automatically
2. Track schema changes and impact
3. Assess data quality proactively
4. Manage dependencies before deployments

**Key User Journeys:**

#### Journey 1: Schema Migration Planning
1. **Entry:** Needs to drop deprecated `old_orders` table
2. **Navigate:** Goes to `old_orders` table → Lineage tab
3. **Visualize:** Sees graph with 3 downstream tables using FK
4. **Impact:** Notes dependencies (ETL jobs, dashboards)
5. **Export:** Downloads dependency report (PDF)
6. **Plan:** Creates migration plan to update downstream first
7. **Monitor:** Adds table to watchlist for change tracking

#### Journey 2: Quality Monitoring Setup
1. **Entry:** Wants proactive alerts for critical tables
2. **Navigate:** Quality → Rules → New Rule
3. **Configure:** Selects `orders` table, adds rules:
   - NULL check on `order_status` (0% allowed)
   - Freshness check (updated within 24 hours)
   - Row count anomaly detection (±10% from 30-day avg)
4. **Alert:** Sets Slack webhook for violations
5. **Test:** Runs manual quality check to verify
6. **Schedule:** Confirms 6-hour check interval
7. **Dashboard:** Pins quality metrics to dashboard

#### Journey 3: Auto-Documentation Review
1. **Entry:** AI generated documentation for new `refunds` table
2. **Navigate:** Documentation tab for `refunds`
3. **Review:** Reads AI description, column explanations
4. **Edit:** Adds business context AI couldn't infer
5. **Approve:** Marks documentation as "Reviewed"
6. **Share:** Generates shareable link for team
7. **Version:** Tracks changes in version history

---

## Page Structure & Layout

### Global Layout Components

```
┌─────────────────────────────────────────────────────────┐
│ Top Navigation Bar (64px fixed)                        │
│ [Logo] [Search] [Notifications] [Profile]              │
└─────────────────────────────────────────────────────────┘
┌──────────┬──────────────────────────────────────────────┐
│          │                                              │
│  Sidebar │         Main Content Area                    │
│  (240px) │         (Responsive width)                   │
│          │                                              │
│  [Nav]   │  ┌──────────────────────────────────────┐   │
│  [Nav]   │  │ Breadcrumbs                          │   │
│  [Nav]   │  ├──────────────────────────────────────┤   │
│          │  │                                      │   │
│  Active  │  │  Page Header                         │   │
│  Item    │  │  - Title, actions, tabs              │   │
│          │  │                                      │   │
│          │  ├──────────────────────────────────────┤   │
│          │  │                                      │   │
│          │  │  Content Area                        │   │
│          │  │  - Cards, lists, tables, charts      │   │
│          │  │                                      │   │
│          │  │                                      │   │
│          │  └──────────────────────────────────────┘   │
│          │                                              │
└──────────┴──────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│ AI Chat Drawer (Expandable from bottom/right)          │
└─────────────────────────────────────────────────────────┘
```

### Page Templates

#### 1. **List Page** (Databases, Tables, Quality Alerts)
```
Header
├── Title + Count
├── Search Bar (with filters)
├── Primary Action Button (e.g., "Add Database")
└── View Toggle (Grid/List)

Content
├── Filters Sidebar (left, collapsible)
├── List/Grid Items
│   ├── Item Card (thumbnail, title, meta)
│   └── Quick Actions (hover/context menu)
└── Pagination
```

#### 2. **Detail Page** (Table Details, Database Details)
```
Header
├── Breadcrumbs
├── Title + Status Badge
├── Action Toolbar (Edit, Delete, Sync, Export)
└── Tabs (Overview, Quality, Lineage, Documentation)

Content
├── Hero Section (key metrics, description)
├── Primary Content (depends on active tab)
│   ├── Overview: Stats cards, sample data
│   ├── Quality: Charts, metrics table
│   ├── Lineage: Interactive graph
│   └── Documentation: Rich text editor
└── Related Items Sidebar (right)
```

#### 3. **Dashboard Page**
```
Header
├── Welcome Message
└── Date Range Selector

Content
├── Quick Actions Row (Connect DB, Run Quality Check)
├── Metrics Grid (4 stat cards)
├── Quality Overview Chart (time series)
├── Recent Activity Feed
└── Pinned Tables (favorites)
```

---

## Component Architecture

### Core Component Hierarchy

```
App
├── Layout
│   ├── TopNav
│   │   ├── Logo
│   │   ├── GlobalSearch (Command+K)
│   │   ├── NotificationBell
│   │   └── UserMenu
│   ├── Sidebar
│   │   ├── NavItem (x7)
│   │   ├── FavoritesList
│   │   └── CollapseToggle
│   └── ChatDrawer (global)
│       ├── ChatHeader
│       ├── MessageList
│       ├── MessageInput
│       └── SuggestedPrompts
│
├── Pages
│   ├── DatabaseListPage
│   │   ├── DatabaseCard (repeating)
│   │   └── AddDatabaseDialog
│   │
│   ├── TableDetailPage
│   │   ├── TableHeader
│   │   ├── TabNavigation
│   │   ├── OverviewTab
│   │   │   ├── StatsBar (4 metrics)
│   │   │   ├── DescriptionCard
│   │   │   ├── ColumnList
│   │   │   └── SampleDataTable
│   │   ├── QualityTab
│   │   │   ├── QualityScore (gauge)
│   │   │   ├── MetricsChart (Recharts)
│   │   │   └── IssuesList
│   │   ├── LineageTab
│   │   │   ├── LineageGraph (React Flow)
│   │   │   └── ImpactSummary
│   │   └── DocumentationTab
│   │       ├── AIGeneratedBadge
│   │       ├── MarkdownRenderer
│   │       └── EditButton
│   │
│   └── QualityDashboardPage
│       ├── OverviewMetrics
│       ├── TrendChart
│       └── AlertsTable
│
└── Shared Components
    ├── Button (Primary, Secondary, Ghost, Danger)
    ├── Card (Base, Stat, Feature)
    ├── Badge (Status, Quality, Type)
    ├── Dialog (Modal, Drawer, Alert)
    ├── Table (Sortable, Filterable, Paginated)
    ├── Search (Basic, Advanced with facets)
    ├── LoadingState (Spinner, Skeleton, Progress)
    └── EmptyState (Icon, Message, Action)
```

### Component Design Patterns

#### 1. **Compound Components** (for complex UI)
```tsx
<TableDetail>
  <TableDetail.Header>
    <TableDetail.Title />
    <TableDetail.Actions />
  </TableDetail.Header>
  <TableDetail.Tabs>
    <TableDetail.Tab name="overview">
      <OverviewContent />
    </TableDetail.Tab>
  </TableDetail.Tabs>
</TableDetail>
```

#### 2. **Render Props** (for data fetching)
```tsx
<QueryLoader 
  queryKey={["table", tableId]}
  render={({ data, isLoading }) => (
    isLoading ? <Skeleton /> : <TableCard table={data} />
  )}
/>
```

#### 3. **Composition** (for layouts)
```tsx
<PageLayout>
  <PageHeader title="Databases" action={<AddButton />} />
  <PageContent>
    <FilterSidebar />
    <MainContent />
  </PageContent>
</PageLayout>
```

---

## User Flows

### Flow 1: Database Connection
**Goal:** Connect to PostgreSQL database and extract schema

**Steps:**
1. Click "Add Database" button
2. Fill connection form (host, port, database, username, password)
3. Click "Test Connection" → See green checkmark
4. Click "Save & Extract Schema"
5. See progress modal (5-10 min estimate)
6. Receive notification when complete
7. Navigate to database details page

**Success Criteria:**
- Connection tested before saving
- Clear progress indication
- Auto-redirect on completion

**Error Handling:**
- Invalid credentials → Show specific error, highlight field
- Network timeout → Suggest firewall/VPN check
- Permission denied → Explain required privileges

---

### Flow 2: Semantic Table Search
**Goal:** Find tables related to "customer purchases" using AI

**Steps:**
1. Press Cmd+K to open global search
2. Type "customer purchases"
3. See results with relevance scores:
   - `orders` (95% match)
   - `order_items` (92% match)
   - `customers` (78% match)
4. Filter by schema: "public"
5. Click `orders` table
6. Land on table detail page

**Success Criteria:**
- Results appear within 500ms
- Relevance scores clearly displayed
- Keyboard navigation (↑↓ to navigate, Enter to select)

**Edge Cases:**
- No results → Suggest broadening search
- Exact match → Show at top with badge
- Too many results → Show top 10, "View all" link

---

### Flow 3: AI Chat SQL Generation
**Goal:** Generate SQL query using natural language

**Steps:**
1. Navigate to `orders` table (or any context)
2. Click floating chat button (bottom-right)
3. Drawer slides up 50% of screen
4. See suggested prompts:
   - "Show me columns in this table"
   - "Generate SQL for last 30 days"
   - "Check for quality issues"
5. Type custom: "Show me orders with payment issues"
6. AI responds in 3-5 sec:
   - Intent classification: "SQL Generation"
   - SQL query with syntax highlighting
   - Copy button
   - Explanation of logic
7. Click "Copy SQL"
8. See "Copied!" toast notification

**Success Criteria:**
- Context-aware (knows current table)
- Fast response (<8 sec p95)
- SQL validated before showing
- Copyable with one click

**Fallback:**
- If AI fails → Show error, suggest rephrasing
- If ambiguous → Ask clarifying question
- If unsafe SQL → Block, explain risk

---

### Flow 4: Quality Drill-Down
**Goal:** Investigate quality alert for NULL spike

**Steps:**
1. See notification bell (red dot)
2. Click bell → Dropdown shows recent alerts
3. Click alert: "payment_value NULL rate: 25% (was 5%)"
4. Navigate to `payments` table → Quality tab
5. See quality score: 78% (yellow, was 95%)
6. View trend chart: sharp increase 3 days ago
7. Scroll to "NULL Rate by Column" table
8. Click `payment_value` row → Drill-down modal
9. See detailed time series + affected row count
10. Click "View Sample Rows" → Table with NULLs
11. Click "Ask AI" → Chat analyzes pattern
12. Export report: PDF with charts + recommendations

**Success Criteria:**
- Alert links directly to problem area
- Visual trend makes spike obvious
- Can drill down to row-level data
- AI provides actionable insights

---

### Flow 5: Lineage Impact Analysis
**Goal:** Check dependencies before dropping table

**Steps:**
1. Navigate to `old_orders` table
2. Click "Lineage" tab
3. See React Flow graph:
   - Center node: `old_orders` (highlighted)
   - Upstream: `raw_orders` (source)
   - Downstream: `order_summary`, `customer_360`, `sales_report`
4. Click node `order_summary` → Side panel shows:
   - Table description
   - Relationship type: Foreign Key
   - Column: `order_id`
   - Query count: 1,247/day
5. Click "Export Dependency Report"
6. Download PDF with full impact analysis
7. Use report to plan migration

**Success Criteria:**
- Graph renders in <2 sec
- Nodes are clickable for details
- Clear visual hierarchy (upstream/downstream)
- Export includes all dependencies

---

## Interaction Patterns

### 1. **Command Palette (Cmd+K)**
- Global search for tables, databases, documentation
- Quick actions: "Add database", "Run quality check"
- Recent searches for fast access
- Keyboard-first navigation

### 2. **Contextual Actions**
- Hover on table row → Show quick actions (View, Edit, Delete)
- Right-click → Context menu with all actions
- Select multiple items → Bulk actions toolbar appears

### 3. **Loading States**
- Skeleton screens for initial page load
- Inline spinners for button actions
- Progress bars for long tasks (with time estimate)
- Optimistic updates for instant feedback

### 4. **Notifications**
- Toast notifications for success/error (bottom-right, 5 sec)
- Notification bell for alerts (persistent until dismissed)
- Email digest for daily quality summary

### 5. **Inline Editing**
- Click text field → Edit inline (table descriptions)
- ESC to cancel, Enter to save
- Loading state while saving
- Success checkmark animation

---

## Navigation System

### Primary Navigation (Sidebar)

```
[Icon] Dashboard
[Icon] Databases (5)          ← Badge shows count
[Icon] Quality (3 alerts)     ← Red badge for alerts
[Icon] Lineage
[Icon] Documentation
[Icon] Chat
[Icon] Export

────────────────────────────

[⭐] Favorites
  ├─ orders
  ├─ customers
  └─ products

────────────────────────────

[Settings]
[Help]
```

**Behavior:**
- Active item highlighted with accent color
- Collapsible to icon-only mode (56px wide)
- Favorites drag-and-drop to reorder
- Favorites sync across devices

### Breadcrumbs

```
Home > Databases > ecommerce_db > public > orders
```

**Behavior:**
- Clickable at each level
- Last item (current page) not clickable
- Ellipsis (...) if too long, click to expand
- Mobile: Show only last 2 levels

### Tabs (Table Detail)

```
[Overview] [Quality] [Lineage] [Documentation]
```

**Behavior:**
- Horizontal scroll on mobile
- Active tab underlined with accent color
- Badge on tab for alerts (e.g., "Quality (3)")
- URL updates on tab change (/tables/:id/quality)

---

## Responsive Design

### Breakpoints

- **Mobile:** 0-639px (1 column, stacked)
- **Tablet:** 640-1023px (2 columns, collapsible sidebar)
- **Desktop:** 1024-1535px (3 columns, full sidebar)
- **Wide:** 1536px+ (3 columns, wider content)

### Mobile Adaptations

#### Bottom Navigation (Mobile only)
```
[Dashboard] [Search] [Chat] [Profile]
```
Replaces sidebar navigation on mobile.

#### Tables → Cards
Convert data tables to card lists:
```
┌──────────────────────┐
│ orders               │
│ 1.2M rows · Updated 2h ago
│ Quality: 95% ✓       │
│ [View] [⋮]           │
└──────────────────────┘
```

#### Drawer Overlays
Instead of sidebars, use full-screen drawers:
- Filters drawer (slide from left)
- Chat drawer (slide from bottom)
- Details drawer (slide from right)

---

## Accessibility

### WCAG 2.1 AA Compliance

#### Keyboard Navigation
- Tab order follows visual hierarchy
- Skip links ("Skip to main content")
- Focus indicators (2px accent outline)
- Keyboard shortcuts with legend (? key)

#### Screen Reader Support
- Semantic HTML (header, nav, main, aside)
- ARIA labels on icons ("Delete database")
- Live regions for dynamic content (notifications)
- Alt text on all images/charts

#### Color & Contrast
- Minimum 4.5:1 contrast for text
- Color not sole indicator (use icons + text)
- Testing with achromatic vision simulator

#### Motion & Animation
- Respect `prefers-reduced-motion`
- Disable autoplay for animations
- Provide pause controls for auto-refreshing data

---

## Visual Design System

### Color Palette

**Brand Colors:**
- Primary: `#3B82F6` (Blue 500) - Actions, links
- Secondary: `#8B5CF6` (Violet 500) - Highlights
- Accent: `#10B981` (Green 500) - Success states

**Semantic Colors:**
- Success: `#10B981` (Green 500)
- Warning: `#F59E0B` (Amber 500)
- Error: `#EF4444` (Red 500)
- Info: `#3B82F6` (Blue 500)

**Neutrals:**
- Gray scale: 50-900 (Tailwind)
- Dark mode: Inverted with adjusted opacity

**Quality Score Colors:**
- Excellent (90-100%): `#10B981` (Green)
- Good (75-89%): `#3B82F6` (Blue)
- Fair (50-74%): `#F59E0B` (Amber)
- Poor (<50%): `#EF4444` (Red)

### Typography

**Font Family:**
- Sans: `Inter` (UI text, body)
- Mono: `JetBrains Mono` (code, SQL)

**Scale:**
- XS: 12px (captions, meta)
- SM: 14px (body, labels)
- Base: 16px (default body)
- LG: 18px (subheadings)
- XL: 20px (section titles)
- 2XL: 24px (page titles)
- 3XL: 30px (hero titles)

**Weights:**
- Regular: 400 (body text)
- Medium: 500 (labels, buttons)
- Semibold: 600 (headings)
- Bold: 700 (emphasis)

### Spacing

**Scale (px):** 4, 8, 12, 16, 24, 32, 48, 64, 96, 128

**Usage:**
- Component padding: 16px (base), 24px (large cards)
- Section gaps: 32px (vertical), 24px (horizontal)
- Card spacing: 16px gap in grid
- Form field spacing: 12px between label and input

### Shadows

- SM: `0 1px 2px rgba(0,0,0,0.05)` (subtle depth)
- Base: `0 1px 3px rgba(0,0,0,0.1)` (cards)
- LG: `0 10px 15px rgba(0,0,0,0.1)` (modals)
- XL: `0 20px 25px rgba(0,0,0,0.1)` (overlays)

### Border Radius

- SM: 4px (buttons, badges)
- Base: 8px (cards, inputs)
- LG: 12px (large cards)
- Full: 9999px (pills, avatars)

### Icons

**Library:** Lucide React (consistent 24x24px)

**Usage:**
- Navigation: 20px icons
- Buttons: 16px icons (with 8px gap to text)
- Status badges: 12px icons
- Hero sections: 48px icons

---

## Implementation Checklist

### Phase 1: Foundation (Week 1-2)
- [ ] Setup Tailwind CSS with custom theme
- [ ] Implement layout components (TopNav, Sidebar, PageLayout)
- [ ] Create design system components (Button, Card, Badge)
- [ ] Build global search component
- [ ] Implement responsive navigation

### Phase 2: Core Pages (Week 3-4)
- [ ] Database list page with cards
- [ ] Add database form and connection flow
- [ ] Table detail page with tabs
- [ ] Quality dashboard with charts
- [ ] Lineage graph with React Flow

### Phase 3: AI Integration (Week 5-6)
- [ ] Chat drawer component
- [ ] Message list with streaming
- [ ] AI response formatting (SQL syntax highlighting)
- [ ] Suggested prompts based on context

### Phase 4: Polish (Week 7-8)
- [ ] Loading states and skeletons
- [ ] Empty states with illustrations
- [ ] Error boundaries and fallbacks
- [ ] Notification system
- [ ] Accessibility audit and fixes

---

## Appendix: Design Inspiration

### Similar Products
- **Atlan** - Metadata management, clean table views
- **Alation** - Search-first discovery, quality badges
- **DataHub** - Lineage visualization, tag system
- **dbt Docs** - Auto-generated documentation, column-level lineage
- **Metabase** - SQL editor, question-to-SQL
- **Notion** - Collaborative editing, slash commands

### UI Patterns
- Command palette: Linear, Raycast, GitHub
- Table exploration: Airtable, Notion databases
- Graph visualization: Neo4j, Miro
- Chat interface: ChatGPT, Intercom
- Dashboard design: Datadog, Grafana

---

**End of UI/UX Architecture Document**
