# Generated Specification

## Requirement 1: Calculate tip amount
- **AC 1.1** — GIVEN A bill total and a tip percentage WHEN The tip calculator is invoked THEN It returns the tip amount = bill_total * tip_percentage / 100, rounded to 2 decimal places

## Requirement 2: Calculate total with tip
- **AC 2.1** — GIVEN A bill total and a tip percentage WHEN The tip calculator is invoked THEN It returns total_with_tip = bill_total + tip_amount, rounded to 2 decimal places

## Requirement 3: Calculate per-person amount
- **AC 3.1** — GIVEN A total with tip and a number of people >= 1 WHEN The tip calculator is invoked THEN It returns per_person = total_with_tip / number_of_people, rounded to 2 decimal places

## Requirement 4: Handle zero tip
- **AC 4.1** — GIVEN A bill total and a tip percentage of 0 WHEN The tip calculator is invoked THEN It returns tip_amount = 0.00 and total_with_tip = bill_total

## Requirement 5: Reject invalid number of people
- **AC 5.1** — GIVEN A number of people less than 1 or not an integer WHEN The tip calculator is invoked THEN It raises a ValueError with a message indicating people must be >= 1

## Requirement 6: Reject negative bill or tip
- **AC 6.1** — GIVEN A bill total < 0 or a tip percentage < 0 WHEN The tip calculator is invoked THEN It raises a ValueError with a message indicating the value is out of range

## Edge Cases
- Bill total of 0.00 with any valid tip percentage
- Tip percentage of exactly 100 (doubling the bill)
- Very large bill (999,999,999.99) to test overflow
- Single person (no splitting needed)
- Fractional per-person amounts that require rounding
- Tip percentage of 0 with multiple people