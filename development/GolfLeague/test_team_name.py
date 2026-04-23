#!/usr/bin/env python
"""Test script for team name generation."""

from golf_league import generate_team_name

# Test cases
test_cases = [
    ('John Smith', 'Jane Doe', 'Smith-Doe'),
    ('Bill Blackburn', 'Dave Degrasse', 'Blackburn-Degrasse'),
    ('Craig Fladten', 'Matt Fladten', 'Fladten-Fladten'),
    ('SingleName', 'AnotherName', 'SingleName-AnotherName'),
    ('', 'Smith', 'Smith'),
    ('John', '', 'John'),
    ('', '', 'Team')
]

print('Testing generate_team_name function:')
all_passed = True
for p1, p2, expected in test_cases:
    result = generate_team_name(p1, p2)
    status = 'PASS' if result == expected else 'FAIL'
    if result != expected:
        all_passed = False
    print(f'{status}: {p1!r} + {p2!r} -> {result!r} (expected: {expected!r})')

print()
if all_passed:
    print('All tests passed!')
else:
    print('Some tests failed!')
