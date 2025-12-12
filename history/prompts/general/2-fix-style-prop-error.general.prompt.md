---
id: 2
title: "Fix Style Prop Error"
stage: general
date_iso: "2025-12-12"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "001-physical-ai-capstone"
user: "aamir"
command: "/sp.implement error resolve nahi hua button par click karne ke baad yeh arha hai page par \"The `style` prop expects a mapping from style properties to values, not a string. For example, style={{marginRight: spacing + 'em'}} when using JSX.\""
labels: ["react", "jsx", "style", "bug-fix", "docusaurus"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml: |
  - docs/intro.md
  - docs/src/pages/index.module.css
tests_yaml: |
  - Docusaurus build successful
  - Style prop error resolved
prompt_text: |
  error resolve nahi hua button par click karne ke baad yeh arha hai page par "
  The `style` prop expects a mapping from style properties to values, not a string. For example, style={{marginRight: spacing + 'em'}} when using JSX."
response_text: |
  Fixed the React style prop error in the intro.md file by converting HTML-style inline styles to CSS classes. The error was occurring because Docusaurus was interpreting HTML elements with string-based style attributes as JSX elements expecting object-based style props.

  Changes made:
  1. Updated intro.md to replace inline styles with CSS class names
  2. Added corresponding CSS rules in index.module.css for the new classes
  3. Used semantic class names like textbook-intro, textbook-module-card, etc.
  4. Maintained the same visual appearance while using proper React/Docusaurus patterns
outcome: "Style prop error resolved and Docusaurus site builds successfully"
evaluation: "Navigation buttons now work without React style prop errors"
---

# Fix Style Prop Error

## Summary
Resolved the React style prop error that was occurring when clicking navigation buttons.

## Context
The user reported a React error: "The `style` prop expects a mapping from style properties to values, not a string. For example, style={{marginRight: spacing + 'em'}} when using JSX." This error was occurring when clicking buttons on the page.

## Root Cause
The error was caused by HTML elements in the `intro.md` file that contained inline styles in string format (HTML-style: `style="..."`) but were being processed as JSX elements in Docusaurus which expect object format (React-style: `style={{...}}`).

## Changes Made

### 1. Updated intro.md
- **File**: `docs/intro.md`
- **Change**: Replaced HTML elements with inline styles with elements using CSS classes
- **Before**:
  ```html
  <div style="text-align: center; padding: 4rem 1rem; ...">
  ```
- **After**:
  ```html
  <div class="hero hero--primary textbook-intro">
  ```

### 2. Added CSS Styles
- **File**: `docs/src/pages/index.module.css`
- **Change**: Added corresponding CSS rules for the new classes
- **Result**: Maintained the same visual appearance while using proper CSS modules approach

## Verification
- Docusaurus site builds successfully without style prop errors
- Navigation buttons work properly without React warnings
- Visual appearance remains the same as intended

## Files Modified
- `docs/intro.md` - Updated HTML elements to use CSS classes instead of inline styles
- `docs/src/pages/index.module.css` - Added CSS rules for new classes

## Impact
- Resolved React style prop error
- Improved code maintainability by using CSS modules instead of inline styles
- Maintained visual design while following React/Docusaurus best practices