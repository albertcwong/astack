---
name: frontend-ui-engineering
description: Build or improve user-facing web interfaces, components, layouts, and interactions. Use when frontend work needs accessible, responsive, production-quality UI that follows the product's actual design system.
---

# Frontend UI engineering

Adapted from Addy Osmani's [frontend-ui-engineering](https://github.com/addyosmani/agent-skills/tree/main/skills/frontend-ui-engineering) skill (MIT).

Build interfaces that fit the product, work at supported screen sizes, and remain usable with a keyboard and assistive technology. Inspect the existing application before choosing patterns or adding dependencies.

## Before implementation

1. Read the repository rules and identify the frontend stack, test commands, design tokens, shared components, and current page patterns.
2. Read the screens and components being changed, their tests, and the API types they consume. Reuse existing components and conventions.
3. For a new or substantially changed screen, write a short design contract: the user's goal, information hierarchy, primary action, required loading/error/empty/success states, responsive behavior, and patterns to avoid. Use product references as evidence, not as a template. Do not copy another product's branding, text, imagery, or exact layout.
4. Define the view and interaction states before building. Use realistic content so wrapping, density, and overflow are visible.

## Component design

- Prefer small components composed from existing primitives. Separate data loading and mutations from presentational rendering when that makes the component easier to understand or test.
- Keep state at the narrowest sensible scope: local UI state locally, shareable filters and pagination in the URL, remote data in the project's server-state layer, and global state only when multiple distant consumers need it.
- Avoid passing props through components that do not use them. Prefer composition before adding configuration props or a new global store.
- Give forms, dialogs, menus, tables, and other interactions explicit focus, validation, dismissal, and error behavior.
- Handle loading, empty, error, success, and permission-denied states when they can occur. Do not leave a blank region or misleading success state.

## Visual quality

- Follow the project's actual colors, typography, spacing, radii, and elevation tokens. Do not add a second design system or arbitrary one-off values.
- Use content-first hierarchy and purposeful density. Avoid generic hero layouts, uniform card grids, decorative gradients, excessive rounding, heavy shadows, filler copy, and oversized spacing unless the product's design system calls for them.
- Keep heading levels semantic and ordered. Do not use a heading solely to get a visual style.
- Make focus, hover, pressed, disabled, loading, and validation states visible and consistent with the product.

## Accessibility

Target WCAG 2.1 AA unless the product specifies a stronger standard.

- Use native semantic elements. Use a real button or link instead of a clickable `div`.
- Give every input a programmatic label. Give icon-only controls an accessible name. Associate help and error text with the relevant field.
- Ensure keyboard access and a logical focus order. Manage focus when a dialog opens, closes, or navigation changes. Do not trap focus outside a modal or leave it behind removed content.
- Announce asynchronous status and validation changes where needed. Do not use color as the only way to convey meaning.
- Check text contrast (4.5:1 for normal text, 3:1 for large text and essential controls), zoom/reflow, reduced motion, and accessible names for controls.

## Responsive behavior

Build mobile-first using the repository's breakpoints and layout utilities. Check at least 320, 768, 1024, and 1440 CSS pixels, plus any product-specific breakpoints. Confirm navigation, tables, dialogs, forms, and long values remain usable without accidental horizontal overflow. Do not hide important actions on narrow screens without an equivalent path.

## Verification

Use the repository's real lint, type, unit, and build commands. For browser-facing changes, run the app and inspect the rendered result in a real browser. Follow `browser-testing-with-devtools` when Chrome DevTools MCP is configured; otherwise use the project's browser-test tooling or provide an exact manual review path. A mocked component test does not prove layout, keyboard flow, or browser behavior.

Check:

- [ ] No new console errors or failed requests
- [ ] Loading, empty, error, success, and permission states as applicable
- [ ] Keyboard navigation, visible focus, labels, heading structure, and accessible names
- [ ] Responsive layout at 320, 768, 1024, and 1440 pixels
- [ ] Existing design tokens and shared components are used
- [ ] The rendered page was inspected at the relevant sizes
- [ ] Automated accessibility checks are run when available; manual keyboard and semantic checks still apply

## Red flags

- More than one component owns the same state without a clear synchronization rule
- Click handlers on non-interactive elements
- Missing loading, empty, error, or permission states
- Raw colors, spacing, or typography that duplicate existing tokens
- UI changes described as visually accepted without inspecting rendered output
- A dependency added without checking whether the project already has an equivalent
