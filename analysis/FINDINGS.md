# Analysis findings

The source contains 541,909 transaction lines. After the stated duplicate assumption and exclusions, 534,128 lines remain.

## Commercial picture

- Gross positive invoice-line value: £10,631,048.74.
- Negative-line return value: £893,979.73.
- Signed net invoice value: £9,737,069.01.
- Positive-sales invoices: 19,959.
- Return value / gross positive value: 8.41%.
- Repeat-purchasing share among identified buyers: 65.58%.
- International share of net value: 16.01%.

November 2011 is the highest complete month, with £1,456,145.80 signed net value. December 2011 ends on the ninth and must not be read as a full-month contraction. The dashboard marks the incomplete period explicitly.

## Cleaning judgment

Missing customer IDs are retained, not guessed or dropped. 132,564 clean lines therefore remain anonymous. Buyer metrics exclude the Unknown identity, while financial metrics retain its value.

5,268 exact duplicate lines are removed as redundant export entries. That is an explicit assumption: indistinguishable genuine repeated lines could exist. Every removed row is retained in the duplicate audit. Another 2,513 rows fail the stated date, quantity, price or invoice-format checks and are preserved with the first applicable reason.

The source has £9,747,747.93 signed value. Subtract duplicate value and signed excluded value to reconcile to the retained amount exactly, with a difference of zero pence. Removing negative adjustments can increase the retained total; the audit records signs rather than claiming all exclusions reduce revenue.

Product and market focus groups use fixed full-period rankings. Their membership does not dynamically change with report slicers. The postage code DOT is the leading net-value code; it is a service, not a merchandise product. Profit, tax treatment and accounting revenue cannot be established from this source.
