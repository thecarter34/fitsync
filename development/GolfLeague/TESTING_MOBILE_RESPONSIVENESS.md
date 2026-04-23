# Mobile Responsiveness Testing Guide

## Quick Start Testing

### 1. Chrome DevTools Device Emulation

1. Open Chrome and navigate to:
   - http://localhost:8000/players
   - http://localhost:8000/teams

2. Open DevTools (F12 or Ctrl+Shift+I)

3. Toggle Device Toolbar (Ctrl+Shift+M)

4. Select these device presets and verify:

#### iPhone SE (375×667)

- ✅ Table rows display as cards
- ✅ Touch targets ≥44×44px
- ✅ Font sizes readable (≥14px)
- ✅ Action buttons properly spaced
- ✅ Modal fits screen with close button visible
- ✅ Checkboxes are tappable (44×44px area)

#### iPhone 14 Pro (390×844)

- ✅ Safe area insets respected (notch)
- ✅ Hamburger menu accessible
- ✅ Cards have proper margins
- ✅ No horizontal scrolling

#### Samsung Galaxy S21 (360×800)

- ✅ Android Chrome rendering
- ✅ Touch feedback working (scale animation)
- ✅ Table card layout intact

#### iPad Mini (768×1024)

- ✅ Tablet layout (still uses card layout at this width)
- ✅ Navigation visible (desktop menu appears at 768px+)
- ✅ Modals appropriately sized

### 2. Manual Testing Checklist

#### Touch Target Verification

- [ ] All buttons ≥44×44px (use DevTools → Elements → Computed → Box Model)
- [ ] Checkboxes have 44×44px touch area (including padding)
- [ ] Modal close button 40×40px (minimum 44px recommended)
- [ ] Navigation links have adequate padding

#### Font Readability

- [ ] Body text in table cards is 14px minimum
- [ ] Headers are 24px on desktop, scale appropriately on mobile
- [ ] No text is cut off or truncated
- [ ] Line height is comfortable (1.5)

#### Table Card Layout

- [ ] Each card has proper border and spacing
- [ ] Labels (data-label) are left-aligned and visible
- [ ] Values are right-aligned
- [ ] Action buttons are left-aligned for thumb reach
- [ ] Buttons have adequate spacing (0.75rem gap)
- [ ] Cards wrap on very small screens (320px)

#### Modal Functionality

- [ ] Modal opens with proper animation
- [ ] Close button (×) visible on mobile
- [ ] Clicking close button closes modal
- [ ] Clicking backdrop closes modal
- [ ] Pressing Escape key closes modal
- [ ] Form inputs have 48px height on mobile
- [ ] Modal buttons are full-width on very small screens

#### Navigation

- [ ] Hamburger menu button is tappable
- [ ] Mobile menu opens/closes smoothly
- [ ] Menu items have adequate padding
- [ ] Active state is clearly visible
- [ ] Menu closes when tapping a link

#### Performance

- [ ] Page loads in <3 seconds on Fast 3G (DevTools throttling)
- [ ] Scrolling is smooth (60fps, no jank)
- [ ] No layout shift (CLS < 0.1)
- [ ] Images load progressively

### 3. Automated Testing with Lighthouse

```bash
# Install Lighthouse CI
npm install -g @lhci/cli

# Run audit on players page
lhci autorun --collect.url="http://localhost:8000/players" --collect.url="http://localhost:8000/teams"

# Or use Chrome DevTools:
# 1. DevTools → Lighthouse tab
# 2. Select "Mobile" device
# 3. Check all categories
# 4. Click "Generate report"
```

**Target Scores:**

- Performance: ≥90
- Accessibility: 100 (touch targets, font sizes)
- Best Practices: ≥90
- SEO: ≥90
- PWA: ≥50 (baseline)

### 4. Specific Test Cases

#### Test Case 1: Add Player on Mobile

1. Navigate to /players on mobile viewport (375px)
2. Tap "+ Add Player" button
3. Verify modal opens with proper spacing
4. Fill in form fields (keyboard should not obscure inputs)
5. Tap "Save" - should close modal and update table
6. Verify new player appears in card layout

#### Test Case 2: Delete Team on Mobile

1. Navigate to /teams on mobile viewport
2. Tap checkbox next to a team (44×44px touch area)
3. Verify "Delete Selected" button becomes enabled
4. Tap "Delete Selected"
5. Confirm deletion in modal
6. Verify team removed from list

#### Test Case 3: Table Scrolling

1. Add 10+ players to create scrollable table
2. On mobile, scroll through cards
3. Verify smooth scrolling (no stuttering)
4. Check that cards don't overlap
5. Verify sticky header stays visible

#### Test Case 4: Orientation Change

1. Open /players on mobile (portrait)
2. Rotate device to landscape
3. Verify layout adjusts properly
4. Cards should still be readable
5. Buttons should remain accessible

#### Test Case 5: Reduced Motion

1. Enable "Reduce Motion" in device settings
2. Refresh page
3. Verify no animations (transitions disabled)
4. All functionality should still work

### 5. Real Device Testing

#### iOS Safari (iPhone)

1. Access site via local network IP (e.g., http://192.168.1.100:8000)
2. Add to Home Screen (PWA)
3. Launch from home screen
4. Test touch interactions
5. Verify safe area insets (notch/status bar)

#### Android Chrome

1. Access via local network IP
2. Test with touch gestures
3. Verify hamburger menu works
4. Check modal animations

### 6. Accessibility Testing

#### Using VoiceOver (iOS) / TalkBack (Android)

1. Enable screen reader
2. Navigate through players table
3. Verify each card is announced properly:
   - "Name: [player name]"
   - "Handicap: [value]"
   - "Actions: Edit button, Delete button"
4. Check that checkboxes are properly labeled
5. Verify modal close button is announced

#### Keyboard Navigation (Desktop)

1. Use Tab key to navigate
2. Verify focus indicators are visible
3. All interactive elements should be reachable
4. Enter/Escape should work for modals

### 7. Network Conditions Testing

#### Fast 3G (1.5 Mbps, 75ms RTT)

- [ ] Page loads in reasonable time
- [ ] Fonts load with swap (no invisible text)
- [ ] Images load progressively
- [ ] No broken layouts during load

#### Offline (Service Worker)

- [ ] PWA manifest loads
- [ ] App can be added to home screen
- [ ] Cached assets serve when offline

### 8. Common Issues to Check

#### Layout Issues

- ❌ Cards overflow screen width
- ❌ Text truncation without ellipsis
- ❌ Buttons too close together
- ❌ Modal exceeds viewport height
- ❌ Checkboxes not aligned

#### Touch Issues

- ❌ Small touch targets (<44px)
- ❌ No visual feedback on tap
- ❌ Buttons unresponsive on first tap
- ❌ Scrolling triggers button clicks

#### Performance Issues

- ❌ Janky scrolling (low FPS)
- ❌ Long load times (>5s)
- ❌ Layout shift during load
- ❌ High memory usage

### 9. Browser Compatibility

Test on:

- ✅ Chrome Mobile (latest)
- ✅ Safari Mobile (iOS 14+)
- ✅ Samsung Internet (Android)
- ✅ Firefox Mobile
- ✅ Edge Mobile

### 10. Regression Testing

After making changes, verify:

- [ ] Desktop layout unchanged
- [ ] All existing functionality works
- [ ] No console errors
- [ ] API calls still function
- [ ] Forms submit correctly

## Quick Validation Script

```javascript
// Run in console on /players or /teams mobile viewport

// 1. Check touch target sizes
const buttons = document.querySelectorAll("button, .action-btn");
let allValid = true;
buttons.forEach((btn) => {
  const rect = btn.getBoundingClientRect();
  if (rect.width < 44 || rect.height < 44) {
    console.warn("Small touch target:", btn, rect);
    allValid = false;
  }
});
console.log(
  allValid ? "✅ All touch targets ≥44px" : "❌ Some targets too small",
);

// 2. Check font sizes
const bodyText = document.querySelectorAll(".glass-table td, .glass-input");
let minFont = Infinity;
bodyText.forEach((el) => {
  const size = parseFloat(getComputedStyle(el).fontSize);
  minFont = Math.min(minFont, size);
});
console.log(
  `Minimum font size: ${minFont}px`,
  minFont >= 14 ? "✅" : "❌ Too small",
);

// 3. Check for horizontal scroll
const hasHorizontalScroll =
  document.documentElement.scrollWidth > window.innerWidth;
console.log(
  hasHorizontalScroll
    ? "❌ Horizontal scroll present"
    : "✅ No horizontal scroll",
);

// 4. Count visible cards on mobile
const cards = document.querySelectorAll(".glass-table tbody tr");
console.log(`📱 Showing ${cards.length} card(s)`);
```

## Performance Benchmarks

Run in DevTools Performance panel:

1. Record page load (cold cache)
2. Check metrics:
   - First Contentful Paint: <1.5s
   - Largest Contentful Paint: <2.5s
   - Cumulative Layout Shift: <0.1
   - First Input Delay: <100ms

## Reporting Issues

When reporting mobile UX issues, include:

1. Device name and screen size
2. Browser and version
3. Screenshot or screen recording
4. Console errors (if any)
5. Steps to reproduce
6. Expected vs actual behavior

---

**Last Updated**: 2025-04-06
**Tested By**: Developer
**Status**: Ready for User Acceptance Testing
