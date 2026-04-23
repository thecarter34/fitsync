# Schedule Delete Functionality Fix

## Problem

The schedule screen had a broken delete functionality due to a **modal ID conflict**. Users were unable to delete individually selected items from the schedule.

### Root Cause

The code was using **two different modal dialogs**:

1. `custom-modal` (from `base.html`) - used by the `showConfirm()` function
2. `delete-modal` (defined in `schedule.html`) - a separate modal

The `deleteMatches()` function called `showConfirm()`, which displayed the `custom-modal`. However, the callback inside `showConfirm()` then tried to show the `delete-modal` by setting its message and making it visible. This created a broken flow where:

- The confirmation modal from `showConfirm()` would appear
- After clicking "Confirm", the code would try to manipulate a different modal (`delete-modal`)
- The delete operation would never execute properly

## Solution

Simplified the delete flow to use **only the single `custom-modal`** from `base.html`:

### Changes Made to `templates/schedule.html`

1. **Removed the duplicate `delete-modal` div** (lines 116-142)

2. **Simplified `deleteMatches()` function**:
   - Removed the intermediate step of setting `deleteTargetIds`
   - Removed the attempt to show a second modal
   - Made the delete operation happen directly in the `showConfirm()` callback
   - Uses `matchIds` parameter directly

3. **Simplified `deleteSelected()` function**:
   - Same pattern: delete happens directly in the callback
   - Clears the selection set after successful delete
   - Updates the Delete Selected button state

4. **Removed unused code**:
   - Deleted `confirmDelete()` function
   - Deleted `closeDeleteModal()` function
   - Removed `deleteTargetIds` global variable

### Before (Broken Flow)

```javascript
function deleteMatches(matchIds) {
  showConfirm(message, title, () => {
    deleteTargetIds = matchIds; // Set global
    document.getElementById("delete-message").textContent = message;
    document.getElementById("delete-modal").classList.remove("hidden"); // Show SECOND modal
  });
}

// User would then need to click Delete again in the second modal
function confirmDelete() {
  closeDeleteModal();
  // Actually perform delete using deleteTargetIds
}
```

### After (Fixed Flow)

```javascript
function deleteMatches(matchIds) {
  showConfirm(
    `Delete ${count} matches? This will also delete any recorded scores.`,
    "Delete Matches",
    async () => {
      // Directly perform the delete in the confirmation callback
      const promises = matchIds.map((id) =>
        fetch(`/api/matches/${id}`, { method: "DELETE" }),
      );
      await Promise.all(promises);
      showAlert(`Deleted ${matchIds.length} matches`);
      loadSchedule();
    },
  );
}
```

## Testing

Created comprehensive tests in `test_schedule_delete.py`:

- ✅ **Single match deletion**: Delete one match and verify it's removed
- ✅ **Batch deletion**: Delete multiple matches at once
- ✅ **Score cleanup**: Verify scores are also deleted (API returns 404 for scores of deleted match)
- ✅ **Count verification**: Match count decreases correctly

All existing tests continue to pass:

- `verify_fixes.py` - Season setup and schedule display-only checks
- `test_dropdown_fix.py` - Week filter dropdown functionality

## Result

The schedule screen now correctly supports:

- ✅ Deleting individual matches via row "Delete" button
- ✅ Deleting multiple selected matches via "Delete Selected" button
- ✅ Deleting all matches via "Clear All" button
- ✅ Proper confirmation modal flow using the single shared modal
- ✅ All delete operations work as expected

The user can now successfully delete individually selected items from the schedule screen.
