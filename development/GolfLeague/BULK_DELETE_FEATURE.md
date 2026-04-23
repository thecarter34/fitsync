# Bulk Delete Feature - Players and Teams Tabs

## Overview

Added multi-select delete functionality to both the **Players** and **Teams** tabs, matching the improved delete pattern established in the Schedule tab fix.

## Features Added

### Players Tab (`templates/players.html`)

- ✅ Checkbox column in table for selecting players
- ✅ "Select All" checkbox in header
- ✅ "Delete Selected" button (disabled when nothing selected)
- ✅ Individual "Delete" button for each player (existing)
- ✅ Proper confirmation modal using shared `custom-modal` from `base.html`
- ✅ Selection state management with `Set()`
- ✅ Visual feedback with button enable/disable

### Teams Tab (`templates/teams.html`)

- ✅ Checkbox column in table for selecting teams
- ✅ "Select All" checkbox in header
- ✅ "Delete Selected" button (disabled when nothing selected)
- ✅ Individual "Delete" button for each team (existing)
- ✅ Proper confirmation modal using shared `custom-modal` from `base.html`
- ✅ Selection state management with `Set()`
- ✅ Visual feedback with button enable/disable

## Implementation Details

### Common Pattern (from Schedule fix)

All three tabs now use the same consistent pattern:

1. **State Management**: `let selectedItems = new Set();`
2. **Checkbox Rendering**: Dynamically create checkboxes for each row
3. **Selection Handlers**: `handleCheckboxChange(id, isChecked)` updates the Set
4. **Select All**: `toggleSelectAll()` toggles all checkboxes and updates Set
5. **Button State**: `updateDeleteSelectedButton()` enables/disables button based on selection count
6. **Bulk Delete**: `deleteSelectedItems()` uses `showConfirm()` with async delete in callback
7. **Cleanup**: After successful delete, clear selection and refresh data

### HTML Structure

```html
<!-- Header with Delete Selected button -->
<div class="flex items-center space-x-2">
  <button
    onclick="deleteSelectedPlayers()"
    class="bg-orange-600 hover:bg-orange-700 text-white font-bold py-2 px-4 rounded-lg transition-colors text-sm"
    id="delete-selected-players-btn"
    disabled
  >
    Delete Selected
  </button>
  <button onclick="openAddPlayerModal()" class="btn-primary py-3 px-6">
    + Add Player
  </button>
</div>

<!-- Table with checkbox column -->
<table>
  <thead>
    <tr>
      <th>
        <input
          type="checkbox"
          id="select-all-players"
          class="w-4 h-4 accent-electric-green"
          onchange="toggleSelectAllPlayers()"
        />
      </th>
      <!-- other headers -->
    </tr>
  </thead>
  <tbody id="players-tbody">
    <!-- Populated by JavaScript with checkboxes -->
  </tbody>
</table>
```

### JavaScript Pattern

```javascript
let selectedPlayers = new Set();

function renderPlayers() {
  players.forEach((player) => {
    // Create checkbox
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "player-checkbox w-4 h-4 accent-electric-green";
    checkbox.value = player.id;
    checkbox.onchange = () => handleCheckboxChange(player.id, checkbox.checked);

    // Add checkbox to row...
  });
}

function handleCheckboxChange(playerId, isChecked) {
  if (isChecked) {
    selectedPlayers.add(playerId);
  } else {
    selectedPlayers.delete(playerId);
  }
  updateDeleteSelectedButton();
}

function toggleSelectAllPlayers() {
  // Toggle all checkboxes and update Set
  // ...
  updateDeleteSelectedButton();
}

function updateDeleteSelectedButton() {
  const btn = document.getElementById("delete-selected-players-btn");
  btn.disabled = selectedPlayers.size === 0;
}

async function deleteSelectedPlayers() {
  if (selectedPlayers.size === 0) return;

  showConfirm(
    `Delete ${selectedPlayers.size} selected players?`,
    "Delete Players",
    async () => {
      const playerIds = Array.from(selectedPlayers);
      const promises = playerIds.map((id) =>
        fetch(`/api/players/${id}`, { method: "DELETE" }),
      );
      await Promise.all(promises);
      showAlert(`Deleted ${playerIds.length} players`);
      selectedPlayers.clear();
      updateDeleteSelectedButton();
      await loadPlayers();
    },
  );
}
```

## Testing

Created `test_bulk_delete.py` to verify:

- ✅ Single player deletion (existing functionality)
- ✅ Bulk player deletion (new)
- ✅ Single team deletion (existing functionality)
- ✅ Bulk team deletion (new)
- ✅ Correct count updates after deletion
- ✅ Deleted items are properly removed

All existing tests continue to pass:

- `verify_fixes.py` - Season setup and schedule display-only
- `test_dropdown_fix.py` - Week filter dropdown
- `test_schedule_delete.py` - Schedule match deletion

## Benefits

1. **Consistency**: All three main data management tabs (Players, Teams, Schedule) now have the same bulk delete UX
2. **Efficiency**: Users can delete multiple items with a single confirmation
3. **Safety**: Confirmation modal prevents accidental deletions
4. **Feedback**: Clear visual indicators for selection state
5. **Maintainability**: Shared pattern makes future updates easier

## Files Modified

- `templates/players.html` - Added multi-select delete
- `templates/teams.html` - Added multi-select delete

## API Endpoints Used

- `DELETE /api/players/{player_id}` - Delete a player
- `DELETE /api/teams/{team_id}` - Delete a team
- (Schedule already had) `DELETE /api/matches/{match_id}` - Delete a match

All endpoints already existed and work correctly with bulk operations via `Promise.all()`.
