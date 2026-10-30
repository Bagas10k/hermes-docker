---
name: shared-dialog-controls
description: "Use when adapting custom dropdowns inside native dialogs."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ui, dialog, datepicker, select, accessibility]
---

# Shared Controls inside Native Dialogs and Popovers

## Problem Statement

When porting or reusing custom UI controls (such as themed calendar datepickers, floating single-select options panels, or custom filter disclosures) into modern applications that use native `<dialog>` elements or top-layer modals, two critical pitfalls occur:

1. **Top-Layer Occlusion & Stacking Context Trapping:**
   Native `<dialog open>` renders in the browser's top layer. If a custom select dropdown or datepicker popover is appended to `document.body` or styled with `z-index: 9999`, it is completely occluded behind the `<dialog>` modal backdrop or trapped inside the dialog's overflow container.

2. **Parent Modal Dismissal on Escape / Outside Click:**
   Pressing `Escape` to close the dropdown or calendar inadvertently fires the native dialog's `cancel` event, closing the parent input form and losing all unsaved user data.

## Verified Implementation Architecture

### 1. Unified Placement in Top Layer (Popover API + Dialog Relative Mounting)

- Use the HTML Popover API (`popover="manual"`) on the floating panel (`.select-options` or `#app-date-picker`) where supported. This elevates the panel to the top layer alongside or above the active dialog:
  ```js
  panel.setAttribute('popover', 'manual');
  if (panel.showPopover) panel.showPopover();
  ```
- Dynamically attach the panel to the closest open dialog if one exists, otherwise fallback to `document.body`:
  ```js
  const container = shell.closest('dialog[open], .modal-overlay') || document.body;
  container.appendChild(panel);
  ```
- When closing, hide the popover and restore visibility:
  ```js
  if (panel.matches(':popover-open')) panel.hidePopover();
  panel.hidden = true;
  ```

### 2. Isolation of Escape and Focus Restoration

- **Stop Propagation:** Intercept `Escape` on the custom control and call `event.stopPropagation()` so the event never bubbles to the parent `<dialog>`:
  ```js
  if (event.key === 'Escape') {
      event.preventDefault();
      event.stopPropagation();
      closeControl({ restoreFocus: true });
      return;
  }
  ```
- **Restore Focus to Trigger:** Explicitly restore keyboard focus to the triggering button (`trigger.focus({ preventScroll: true })`).
- **Clean Teardown on Parent Dialog Close:** Listen to the `close` event on document capture. If the parent `<dialog>` closes, immediately dismiss the floating panel without animation:
  ```js
  document.addEventListener('close', event => {
      if (activeControl && event.target.matches?.('dialog')) {
          closeControl({ restoreFocus: false });
      }
  }, true);
  ```

### 3. Non-Mutating Filter State Contract

- Filter bars (e.g. Sales History or Master filters) must remain **GET requests** or purely read-only state changes.
- Selecting options, toggling calendar dates, or opening/closing accordions must record **0 POST/PUT/PATCH write requests**.
- Always verify that query parameters (e.g. `start_date`, `end_date`, `search`, `method`) are sanitized, preserved across pagination links, and cleanly cleared on "Reset".
