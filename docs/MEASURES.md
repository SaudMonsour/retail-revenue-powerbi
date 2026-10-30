# Measure definitions

All measures are stored in the fact table and recalculate under active report filters.

## Net Invoice Value

```dax
SUM(FactSales[LineAmountPence]) / 100
```

Display format: `£#,0.00;(£#,0.00)`.

## Gross Sales

```dax
SUM(FactSales[GrossSalesGBP])
```

Display format: `£#,0.00;(£#,0.00)`.

## Returns Value

```dax
SUM(FactSales[ReturnsGBP])
```

Display format: `£#,0.00;(£#,0.00)`.

## Return Value Rate

```dax
DIVIDE([Returns Value], [Gross Sales])
```

Display format: `0.0%`.

## Sales Invoices

```dax
CALCULATE(DISTINCTCOUNT(FactSales[InvoiceKey]), FactSales[IsSale] = 1)
```

Display format: `#,0`.

## Average Sales Invoice

```dax
DIVIDE([Gross Sales], [Sales Invoices])
```

Display format: `£#,0.00`.

## Identified Buyers

```dax
CALCULATE(DISTINCTCOUNT(FactSales[CustomerKey]), FactSales[IsSale] = 1, FactSales[CustomerKey] <> "Unknown")
```

Display format: `#,0`.

## Net Units

```dax
SUM(FactSales[Quantity])
```

Display format: `#,0`.

## Unknown Customer Value

```dax
CALCULATE([Net Invoice Value], FactSales[CustomerKey] = "Unknown")
```

Display format: `£#,0.00`.

## Unknown Customer Share

```dax
DIVIDE([Unknown Customer Value], [Net Invoice Value])
```

Display format: `0.0%`.

## International Invoice Value

```dax
CALCULATE([Net Invoice Value], KEEPFILTERS(DimCountry[Market] = "International"))
```

Display format: `£#,0.00`.

## Repeat Buyer Rate

```dax
VAR Buyers = FILTER(VALUES(FactSales[CustomerKey]), FactSales[CustomerKey] <> "Unknown" && CALCULATE([Sales Invoices]) > 0) VAR RepeatBuyers = FILTER(Buyers, CALCULATE([Sales Invoices]) > 1) RETURN DIVIDE(COUNTROWS(RepeatBuyers), COUNTROWS(Buyers))
```

Display format: `0.0%`.

## Invoice Lines

```dax
COUNTROWS(FactSales)
```

Display format: `#,0`.

## Latest Complete Month Value

```dax
VAR LastMonth = CALCULATE(MAX(DimDate[YearMonthSort]), REMOVEFILTERS(DimDate), DimDate[IsCompleteMonth] = 1) RETURN CALCULATE([Net Invoice Value], REMOVEFILTERS(DimDate), DimDate[YearMonthSort] = LastMonth)
```

Display format: `£#,0.00`.

