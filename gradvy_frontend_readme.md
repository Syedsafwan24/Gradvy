# Gradvy Frontend — Complete README & Copilot Prompt (Updated with Onboarding Flow)

> **Purpose:** This file is the authoritative frontend spec & Copilot prompt to scaffold a full-featured **Next.js + TailwindCSS + Framer Motion frontend** for **Gradvy — AI Personalized Learning Path Generator**. It defines the **entire frontend structure, components, pages, flows, and styling conventions**.

---

## Table of Contents
1. Purpose & Goals
2. Tech Stack
3. Design System
4. Accessibility
5. File & Folder Structure
6. Component Inventory
7. Pages & Layouts
8. Data Models
9. User Flows (updated)
10. API & Mocking Strategy
11. Animations
12. Development & Run Instructions
13. Copilot JSON Prompt

---

# 1. Purpose & Goals
- Deliver a **modern, responsive, accessible frontend** for Gradvy.
- Provide clear instructions for GitHub Copilot or other scaffolding tools.
- Reflect the **system architecture**: onboarding, quiz generation, learning path building, coding playground, and career insights.

---

# 2. Tech Stack
- **Next.js** (App Router)
- **React (JSX)**
- **TailwindCSS** (styling)
- **Framer Motion** (animations)
- **shadcn/ui** (UI primitives)
- **Lucide-react** (icons)
- **React Hook Form** (forms)
- **Axios / Ky** (API fetching)

---

# 3. Design System
### Colors
```yaml
primary: #1e40af
accent: #06b6d4
secondary: #0f172a
muted: #94a3b8
background: #f1f5f9
card-bg: #ffffff
text-primary: #0f172a
text-secondary: #475569
success: #10b981
danger: #ef4444
```

### Typography
- Font: Inter
- Scale: h1(48px), h2(36px), h3(28px), body(16px), small(14px)

### Breakpoints
- sm: 640px, md: 768px, lg: 1024px, xl: 1280px

---

# 4. Accessibility
- ARIA attributes for modals, accordions, navigation.
- High contrast for buttons & text.
- Keyboard navigation across all interactive UI.

---

# 5. File & Folder Structure
```
/ (root)
├─ package.json
├─ tailwind.config.js
├─ src/
   ├─ app/
   │  ├─ layout.jsx
   │  ├─ globals.css
   │  ├─ page.jsx (Home)
   │  ├─ courses/page.jsx
   │  ├─ courses/[id]/page.jsx
   │  ├─ dashboard/page.jsx
   │  ├─ onboarding/page.jsx
   │  ├─ faq/page.jsx
   │  ├─ team/page.jsx
   │  ├─ playground/page.jsx
   │  └─ career/page.jsx
   ├─ components/
   │  ├─ layout/ (Navbar, Footer)
   │  ├─ ui/ (Button, Card, Avatar, Modal, Loader)
   │  ├─ sections/ (Hero, Features, HowItWorks, Testimonials, FAQ, Team)
   │  ├─ courses/ (CourseCard, CourseFilters)
   │  └─ dashboard/ (ProgressCard, PathStepper)
   ├─ lib/ (api.js, mappers.js)
   └─ mock/ (courses.json, paths.json, users.json)
```

---

# 6. Component Inventory
- **Navbar**: Links, CTA, mobile drawer.
- **Footer**: Columns, newsletter, socials.
- **Hero**: Title, subtitle, CTA, animated illustration.
- **CourseCard**: Thumbnail, provider badge, rating, duration, CTA.
- **CourseFilters**: Provider, rating, duration, sort.
- **ProgressCard**: Path progress & next step.
- **PlanCard**: { name, features[], recommended }.
- **FAQ**: Accordion.

---

# 7. Pages & Layouts
- **Home**: Hero → Features → How It Works → Highlight Courses → Testimonials → FAQ → Team → Footer.
- **Courses**: Filters + grid of CourseCards.
- **Course Detail**: Thumbnail, title, rating, description, related courses.
- **Dashboard**: Paths, progress, career insights, quick continue.
- **Onboarding**: Stepper → Goal OR “Help me decide” → Background & Time → Assessment quiz or Cert Upload.
- **Playground**: Monaco editor + Judge0 integration (mock initially).
- **FAQ / Team / Career**: Static informational pages.

---

# 8. Data Models
### Course
```json
{ "id": "string", "title": "string", "thumbnail": "url", "provider": "string", "rating": "number", "reviews": "number", "duration": "string", "level": "string", "url": "string" }
```
### Path
```json
{ "id": "string", "name": "string", "modules": [{ "id": "m1", "title": "Intro", "completed": false }] }
```
### User
```json
{ "id": "string", "name": "string", "email": "string", "paths": ["pathId"] }
```

---

# 9. User Flows (Updated)

### 1. Home & Onboarding
- CTA: “Start with Goal” OR “Help me decide”.

### 2. Profile Setup
- Input: time/week, experience level, background.

### 3. Assessment
- **If Goal chosen** → Placement quiz or Cert Upload.
- **If No Goal** → Generate **interest-detection quiz** across mixed topics. Answers determine suggested path.

### 4. Path Generation
- AI builds structured learning path (Beginner → Advanced).
- Courses fetched (Udemy, Coursera, YouTube).

### 5. Learning Path UI
- Path with modules, quizzes per module, progress tracking.

### 6. Dashboard
- Shows streaks, next module, overall completion.
- Career insights: job roles, salaries, trending skills.

### 7. Coding Playground (for coding tracks only)
- Monaco Editor + Judge0 (execute code).

---

# 10. API & Mocking
- `/lib/api.js` for data fetch.
- Mock data in `/mock/`.
- Next.js API routes for local endpoints.

---

# 11. Animations
- Fade-in-up, staggered grid animations.
- Floating hero image.
- Smooth page transitions.

---

# 12. Development & Run
```bash
npm install
npm run dev
npm run build
npm run start
```

---

# 13. Copilot JSON Prompt
```json
{
  "project": "gradvy-frontend",
  "description": "Next.js + Tailwind frontend for Gradvy (AI learning path generator)",
  "tech": ["nextjs","tailwind","framer-motion","lucide-react"],
  "pages": ["/","/courses","/courses/[id]","/dashboard","/onboarding","/playground","/faq","/team","/career"],
  "components": {
    "layout": ["Navbar","Footer"],
    "ui": ["Button","Card","Avatar","Loader","Modal"],
    "sections": ["Hero","Features","HowItWorks","Testimonials","FAQ","Team"],
    "courses": ["CourseCard","CourseFilters"],
    "dashboard": ["ProgressCard","PathStepper"],
    "plans": ["PlanCard"]
  },
  "mocks": ["/mock/courses.json","/mock/paths.json","/mock/users.json"],
  "courseSchema": { "id":"string","title":"string","thumbnail":"url","provider":"string","rating":"number","reviews":"number","duration":"string","level":"string","url":"string" },
  "generateFiles": true
}
```

---

# Final Notes
This README integrates the **interest-detection quiz flow** (for users without a goal) into the onboarding. It mirrors the **system architecture diagram**: onboarding → assessment → path generation → dashboard → coding playground → career insights.

