# Bajaj Finserv Design Principles — Reference Summary

Source files: `Design Creation Principles.pdf`, `Design Application Principles.pdf`, `Functionality Guidelines.pdf`

---

## Design Creation Principles

### 1. Usability First
- Keep the user at the center. Prioritise usability over marketing.
- Use **icons over images** — graphical symbols reduce cognitive load and speed up comprehension.
- Identify and highlight primary actions and objectives **within the first 2 folds** of every page.

### 2. Clear Compartments
- Easily distinguishable separators within and outside components.
- Gutter space between components; margin & spacing within components defined in the library.

### 3. Tapability & Reachability
- Interactive elements positioned within the user's natural thumb/finger reach.
- Sufficient spacing around tappable elements to prevent accidental taps.
- Sizes for tappable elements defined at component level in the library.

### 4. Clear Action Callouts
- Interactive elements (buttons, links) must be visually prominent and distinct.
- Use clear labels, contrasting colours, and appropriate sizing to draw attention.

### 5. Relevant Assistance
- Provide in-context guidance directly related to the user's current context.
- Info icons provisioned on the majority of components.

### 6. Relatable Structuring
- Organise content using familiar patterns to aid intuitive navigation.
- Example: All demographic fields clustered together in a form.

### 7. Search Everywhere
- Persistent search bar available at every point in the experience.
- Enables quick access without navigating back to a home state.

### 8. Avoid Dark Patterns
- The 13 dark patterns defined by DDPI must be avoided.
- No false urgency, hidden costs, trick questions, or forced continuity.

### 9. Reduce Cognitive Load
- Limit the number of fields or choices shown at any stage.
- Prioritise information so users consume only what is relevant to their current journey.

---

## Design Application Principles

### 10. Re-use & Re-purpose
- Use existing components from the published design library.
- New components are created and added to the library via DCX.

### 11. Crisp & Clear Fonts
- Use legible, well-defined fonts across devices (size, weight, line height, embellishment).
- Separate height defined for header/subtitle vs. body text.

### 12. Flat Learning Curve
- Use existing, widely accepted interface patterns to reduce onboarding friction.
- Example: Radio button for single select; checkbox for multi-select.

### 13. One Action at a Time
- Present users with a singular task or decision at any given moment.
- **No page to have more than one Primary CTA.**

### 14. Direct Tone of Voice
- Straightforward, concise language throughout the interface.
- Sticker sheets in the library define appropriate content for each scenario.

### 15. Next Best Action Called Out
- Highlight the most relevant action for users to take next based on their context.
- Example: After completing online steps, show clear instructions on what happens next (e.g., "A Bajaj representative will call you").

### 16. Avoid Dead Ends
- At every journey end, provide appropriate actions for users to continue engaging.
- Example: On service denial, show cross-sell options and a CTA to return to homepage.

### 17. Videos Over Text
- Add video assistance wherever possible — easier to consume than text.
- Example: Videos in info drawers alongside text assistance.

### 18. Provide Exits
- Provide exit options at every journey or flow to avoid rage-quitting.
- Example: Every form page has a "Save & Exit" CTA.

---

## Functionality Guidelines — Key Component Rules

### Navigation: Back Button
- **Position:** Top-left corner of the screen.
- **Behaviour:** Returns user to the immediately previous screen; manages state.
- **Data Loss:** Show confirmation dialog before navigating back if unsaved data exists.
- **Accessibility:** Reachable via screen readers; label: "Go back to previous screen".
- **Progressive Disclosure:** In multi-step forms, back steps one level — does not exit the flow.
- **Don't use back to cancel:** Use a separate Cancel or Close (✕) instead.

### Navigation: Close Button
- **Position:** Top-right corner of the window or element it controls.
- **Behaviour:** Dismisses only the immediate context (modal, drawer, overlay). Never acts as a back button.
- **No permanent actions:** Close must be safe and dismissive — not perform an irreversible action.
- **Data Loss:** Show confirmation dialog if closing would lose user data.
- **Tap Target:** Minimum **40×40 px** tap target even if the icon is visually smaller.
- **Dismiss vs. Cancel clarity:** Close = exit the view; Cancel = discard changes. Do not overlap these.

### General Navigation Rules
- Consistent placement and appearance of back/close buttons across the app.
- Intuitive and predictable interactions following established design patterns.
- Clear visual feedback (e.g., animation) on click to confirm the action.
