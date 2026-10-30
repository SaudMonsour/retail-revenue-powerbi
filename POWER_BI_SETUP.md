# Open the Power BI project

1. Extract or clone the complete **retail-revenue-powerbi** folder on Windows.
2. Right-click **configure-path.ps1** and run it with PowerShell from the repository root. If Windows policy blocks scripts, do not weaken system policy: instead open powerbi/Dashboard.SemanticModel/model.bim in a text editor and set the DataRoot expression to the full path of data/clean, including a trailing backslash. Python users can run scripts/configure_paths.py instead.
3. Open **powerbi/Dashboard.pbip** with a recent Power BI Desktop version supporting Power BI Projects and PBIR. Enable the relevant project/report-format preview options if your Desktop build still requires them.
4. Choose Refresh. CSV tables import from the local clean-data folder; no remote data credentials or cloud subscription are required for this local report.
5. Verify that all three pages render, each slicer filters the cards/charts, totals match analysis/summary.json, and the measures behave correctly for an empty or zero-denominator selection. Save as PBIX in Desktop if you need that compiled format.

## What has been verified

- Microsoft JSON-Schema structures used by the supplied PBIP/PBIR files.
- All report field references resolve to actual model columns/measures.
- Every fact foreign key resolves to exactly one dimension key.
- Source and cleaned-row accounting, including retail signed-value reconciliation.
- Visual bounds fit the 1360 × 880 canvas.
- Design previews were computed from the actual clean tables.

## What still needs Desktop

Actual M refresh, DAX-engine execution, native visual rendering, interactions and save/reopen were not run here. A schema-valid report is not a claim that Desktop validation has occurred. See analysis/validation_report.json for the precise checks.

The local schema validator covers the documented schema keywords used by these files. Some Power BI formatting properties have unrestricted schemas; only Desktop can confirm every visual-formatting option is honored. Desktop may substitute fonts or reflow table columns; check those details before publishing.

## Regenerating data and reports

The raw selected source snapshot is included. scripts/clean_analyze.py rebuilds clean tables and summary analyses. scripts/build_powerbi.py rebuilds the model/report definitions; it resets the sample DataRoot value, so configure the path again afterward. scripts/validate_project.py repeats structural and relationship checks using the bundled versioned Microsoft schema references. The notebook or pipeline does not replace manual verification in Power BI.

The charts shown in figures/ are presentation previews and are not used as background screenshots in the Power BI report; all report charts remain native editable visuals.


## Retail snapshot packaging

The large cleaned fact table is stored losslessly as `data/clean/FactSales.csv.gz`. Run either supplied path-configuration helper before opening Power BI; it also expands the CSV used by the M imports. The decompressed bytes were checked against the complete cleaned table. The cleaning script can also regenerate the CSV from the raw snapshot. No records were sampled or removed for upload.

The unmodified Excel source is transported in three binary parts under `data/raw/` to fit upload limits. Either configuration helper reassembles it and verifies the original SHA-256. The parts were compared byte-for-byte with the complete source; no source content was altered.
