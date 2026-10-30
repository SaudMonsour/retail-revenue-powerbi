"""Clean the included raw snapshot without modifying source data."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import hashlib, json, sys, platform
import numpy as np
import pandas as pd

def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=lambda x: x.item() if hasattr(x, 'item') else str(x)) + '\n')

def export(df, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, float_format='%.6f', date_format='%Y-%m-%d', lineterminator='\n')

def profile(df):
    return [{'column': c, 'dtype': str(df[c].dtype), 'missing': int(df[c].isna().sum()), 'distinct': int(df[c].nunique(dropna=True))} for c in df]

def date_dimension(start, end):
    d = pd.DataFrame({'Date': pd.date_range(start, end, freq='D')})
    d['DateKey'] = d.Date.dt.strftime('%Y%m%d').astype(int)
    d['Year'] = d.Date.dt.year
    d['MonthNumber'] = d.Date.dt.month
    d['MonthName'] = d.Date.dt.strftime('%b')
    d['YearMonth'] = d.Date.dt.strftime('%Y-%m')
    d['YearMonthSort'] = d.Date.dt.year * 100 + d.Date.dt.month
    d['Weekday'] = d.Date.dt.day_name()
    d['WeekdayNumber'] = d.Date.dt.dayofweek + 1
    d['IsWeekend'] = (d.Date.dt.dayofweek >= 5).astype(int)
    return d

def retail():
    p = ROOT
    raw = pd.read_excel(p / 'data/raw/Online Retail.xlsx', engine='openpyxl')
    before = profile(raw)
    d = raw.copy()
    d.insert(0, 'SourceRow', np.arange(len(d)) + 2)
    duplicates = raw.duplicated()
    duplicate_rows = d.loc[duplicates].copy()
    d = d.loc[~duplicates].copy()
    for c in ['InvoiceNo', 'StockCode', 'Description', 'Country']:
        d[c] = d[c].astype('string').str.strip().str.replace('\\s+', ' ', regex=True)
    d['Quantity'] = pd.to_numeric(d.Quantity, errors='coerce')
    d['UnitPrice'] = pd.to_numeric(d.UnitPrice, errors='coerce')
    d['InvoiceDate'] = pd.to_datetime(d.InvoiceDate, errors='coerce')
    bad_date = d.InvoiceDate.isna()
    bad_qty = d.Quantity.isna() | d.Quantity.eq(0) | d.Quantity.mod(1).ne(0)
    bad_price = d.UnitPrice.isna() | d.UnitPrice.le(0)
    bad_invoice = ~d.InvoiceNo.str.match('^C?\\d{6}$', na=False)
    reasons = np.select([bad_date, bad_qty, bad_price, bad_invoice], ['Invalid invoice timestamp', 'Invalid or zero quantity', 'Non-positive unit price', 'Non-standard invoice identifier'], default='')
    d['ExclusionReason'] = reasons
    excluded = d.loc[d.ExclusionReason.ne('')].copy()
    clean = d.loc[d.ExclusionReason.eq('')].drop(columns='ExclusionReason').copy()

    def pence(q, v):
        return int((Decimal(str(v)) * Decimal(str(int(q))) * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
    clean['LineAmountPence'] = [pence(q, v) for q, v in zip(clean.Quantity, clean.UnitPrice)]
    clean['CustomerKey'] = clean.CustomerID.map(lambda x: 'Unknown' if pd.isna(x) else str(int(x)))
    clean['DateKey'] = clean.InvoiceDate.dt.strftime('%Y%m%d').astype(int)
    clean['InvoiceDate'] = clean.InvoiceDate.dt.strftime('%Y-%m-%d %H:%M:%S')
    clean['Description'] = clean.Description.fillna('Description not recorded')
    clean['Country'] = clean.Country.fillna('Unknown')
    clean = clean.rename(columns={'InvoiceNo': 'InvoiceKey', 'StockCode': 'ProductKey', 'Country': 'CountryKey'})
    clean['IsReturn'] = clean.Quantity.lt(0).astype(int)
    clean['IsSale'] = clean.Quantity.gt(0).astype(int)
    clean['CancellationFlag'] = clean.InvoiceKey.str.startswith('C').astype(int)
    clean['GrossSalesGBP'] = np.where(clean.IsSale.eq(1), clean.LineAmountPence / 100, 0)
    clean['ReturnsGBP'] = np.where(clean.IsReturn.eq(1), -clean.LineAmountPence / 100, 0)
    clean['NetSalesGBP'] = clean.LineAmountPence / 100
    products = clean.groupby('ProductKey', sort=True).agg(Description=('Description', lambda x: x.mode().iloc[0]), DescriptionVariants=('Description', 'nunique')).reset_index()
    products['LineCategory'] = np.where(products.ProductKey.str.contains('\\d', regex=True), 'Product / mixed code', 'Service / adjustment code')
    customers = pd.DataFrame({'CustomerKey': sorted(clean.CustomerKey.unique())})
    customers['Identified'] = (customers.CustomerKey != 'Unknown').astype(int)
    countries = pd.DataFrame({'CountryKey': sorted(clean.CountryKey.unique())})
    countries['Market'] = np.where(countries.CountryKey.eq('United Kingdom'), 'United Kingdom', 'International')
    top_countries = clean.loc[clean.CountryKey.ne('United Kingdom')].groupby('CountryKey').NetSalesGBP.sum().nlargest(9).index
    countries['CountryGroup'] = countries.CountryKey.where(countries.CountryKey.isin(top_countries) | countries.CountryKey.eq('United Kingdom'), 'Other international')
    customers['CustomerType'] = np.where(customers.CustomerKey.eq('Unknown'), 'Anonymous / not recorded', 'Identified')
    top_products = clean.groupby('ProductKey').NetSalesGBP.sum().nlargest(9).index
    products['ProductFocus'] = [str(k) + ' · ' + str(v)[:28] if k in top_products else 'Other products / services' for k, v in zip(products.ProductKey, products.Description)]
    dates = date_dimension(pd.to_datetime(clean.InvoiceDate).min().normalize(), pd.to_datetime(clean.InvoiceDate).max().normalize())
    dates['IsCompleteMonth'] = (dates.YearMonth != dates.YearMonth.max()).astype(int)
    cols = ['SourceRow', 'InvoiceKey', 'ProductKey', 'CustomerKey', 'CountryKey', 'DateKey', 'Quantity', 'UnitPrice', 'LineAmountPence', 'GrossSalesGBP', 'ReturnsGBP', 'NetSalesGBP', 'IsSale', 'IsReturn', 'CancellationFlag']
    fact = clean[cols].copy()
    fact.Quantity = fact.Quantity.astype(int)
    for name, frame in [('FactSales', fact), ('DimProduct', products), ('DimCustomer', customers), ('DimCountry', countries), ('DimDate', dates)]:
        export(frame, p / 'data/clean' / f'{name}.csv')
    export(duplicate_rows, p / 'data/audit/duplicate_rows.csv')
    export(excluded, p / 'data/audit/excluded_rows.csv')
    sale = clean[clean.IsSale.eq(1)]
    known = sale[sale.CustomerKey != 'Unknown']
    orders = known.groupby('CustomerKey').InvoiceKey.nunique()
    monthly = clean.groupby(pd.to_datetime(clean.InvoiceDate).dt.strftime('%Y-%m')).agg(NetSalesGBP=('NetSalesGBP', 'sum'), GrossSalesGBP=('GrossSalesGBP', 'sum'), ReturnsGBP=('ReturnsGBP', 'sum'), InvoiceCount=('InvoiceKey', 'nunique')).reset_index(names='YearMonth')
    monthly['CompleteMonth'] = (monthly.YearMonth != monthly.YearMonth.max()).astype(int)
    country = clean.groupby('CountryKey').agg(NetSalesGBP=('NetSalesGBP', 'sum'), GrossSalesGBP=('GrossSalesGBP', 'sum'), ReturnsGBP=('ReturnsGBP', 'sum')).sort_values('NetSalesGBP', ascending=False).reset_index()
    product = clean.groupby('ProductKey').agg(NetSalesGBP=('NetSalesGBP', 'sum'), Units=('Quantity', 'sum')).join(products.set_index('ProductKey')[['Description']]).sort_values('NetSalesGBP', ascending=False).reset_index()
    for name, frame in [('monthly', monthly), ('country', country), ('product', product)]:
        export(frame, p / 'analysis' / f'{name}.csv')
    raw_pence = sum((pence(q, v) for q, v in zip(raw.Quantity, raw.UnitPrice)))
    dupe_pence = sum((pence(q, v) for q, v in zip(duplicate_rows.Quantity, duplicate_rows.UnitPrice)))
    excluded_pence = sum((pence(q, v) for q, v in zip(excluded.Quantity, excluded.UnitPrice)))
    clean_pence = int(clean.LineAmountPence.sum())
    summary = {'source_rows': len(raw), 'clean_rows': len(clean), 'exact_duplicates_removed': int(duplicates.sum()), 'excluded_rows': len(excluded), 'missing_customer_rows_source': int(raw.CustomerID.isna().sum()), 'missing_description_rows_source': int(raw.Description.isna().sum()), 'unknown_customer_rows_retained': int(clean.CustomerKey.eq('Unknown').sum()), 'gross_sales_gbp': round(float(clean.GrossSalesGBP.sum()), 2), 'returns_gbp': round(float(clean.ReturnsGBP.sum()), 2), 'net_sales_gbp': round(clean_pence / 100, 2), 'positive_sales_invoices': int(sale.InvoiceKey.nunique()), 'identified_purchasing_customers': int(orders.size), 'repeat_customer_rate': float((orders > 1).mean()), 'return_value_rate': float(clean.ReturnsGBP.sum() / clean.GrossSalesGBP.sum()), 'international_net_sales_share': float(clean.loc[clean.CountryKey != 'United Kingdom', 'NetSalesGBP'].sum() / clean.NetSalesGBP.sum()), 'start': str(pd.to_datetime(clean.InvoiceDate).min()), 'end': str(pd.to_datetime(clean.InvoiceDate).max()), 'incomplete_month': monthly.YearMonth.max(), 'reconciliation_pence': {'raw': raw_pence, 'duplicates': dupe_pence, 'excluded': excluded_pence, 'retained': clean_pence, 'difference': raw_pence - dupe_pence - excluded_pence - clean_pence}, 'duplicate_policy': 'Remove exact duplicates across all eight source columns; these may include indistinguishable real lines, so all removed rows are retained for audit. Do not deduplicate by invoice/product alone.', 'customer_policy': 'Keep missing identifiers as Unknown. Do not impute an identity or discard their invoice value.', 'value_scope': 'Signed invoice-line amount, positive prices only; includes service and mixed product codes. Not audited GAAP revenue, profit, or matched-return cohort rate.'}
    assert summary['reconciliation_pence']['difference'] == 0
    assert len(raw) == len(clean) + len(excluded) + len(duplicate_rows)
    save_json(p / 'analysis/summary.json', summary)
    save_json(p / 'analysis/cleaning_audit.json', {'before': before, 'after': profile(fact), 'exclusions': excluded.ExclusionReason.value_counts().to_dict(), 'duplicate_policy': summary['duplicate_policy'], 'raw_retained': True})
    return summary

ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":
    print(json.dumps(retail(), indent=2, default=str))
