# Metric contract

Net Invoice Value is the signed sum of integer line pence divided by 100. Gross Sales includes positive retained lines; Returns Value is the magnitude of negative retained lines. Return Value Rate divides Returns Value by Gross Sales in the active context; it is not a matched-purchase return probability. Identified Buyers and Repeat Buyer Rate exclude Unknown customer identities. All financial totals retain anonymous lines. Latest Complete Month Value intentionally removes date filters and therefore refers to the final complete month in the source, while preserving other dimensions.

## Filter context

Dimension slicers propagate through active one-to-many, single-direction relationships to the fact table. KPI and chart measures are evaluated in the selected context. A chart selection can further narrow other visuals, subject to native Desktop interaction defaults. Blank ratios mean no valid denominator; they must not be interpreted as an observed zero. Tooltips expose record counts and, for campaign conversion, descriptive interval bounds.

## Snapshot caveats

Invoice amounts include service codes and lack cost, tax-treatment and accounting adjustments. They establish neither profit nor audited revenue. Exact-line duplicate removal is an assumption; the removed rows remain available. Product focus groups use fixed full-period membership.
