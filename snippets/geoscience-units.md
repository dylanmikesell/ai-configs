# Geoscience Units Logic

## usage
- **Units:** Use `pint` for physical quantities. Default to SI units unless the specific domain requires otherwise (e.g., decibels in acoustics). Ensure unit consistency across calculations.
- **Data Formats:** Use **NetCDF** (via `xarray` or `netCDF4`) for large, multi-dimensional datasets. Prioritize metadata richness (attributes, units, coordinates).
