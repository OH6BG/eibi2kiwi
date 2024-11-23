# eibi2kiwi: EiBi Broadcast Schedule Converter for KiwiSDR

## Description
The Python script of eibi2kiwi_online.py converts EiBi broadcast schedules (from www.eibispace.de) into KiwiSDR-compatible broadcast schedules with DX labels. It automatically detects the current broadcast season, downloads the appropriate schedule file, and processes it into a format that can be imported into KiwiSDR receivers as CSV.

## Features
- Automatic season detection (Season A/Season B) based on current date
- Downloads schedule data directly from EiBi website
- Converts location codes to full location names
- Handles various day-of-week formats and ranges
- Generates KiwiSDR-compatible CSV output
- Supports the following transmission modes (DRM, USB, SAS)

## Prerequisites
- Python 3.x
- Required Python packages:
  - requests
  - csv (built-in)
  - pathlib (built-in)

## Required Files
- `eibisites.csv`: A CSV file containing location mappings with the following format:
  ```
  country_code;location_code;location_name
  ```

## Usage
1. Ensure `eibisites.csv` is present in the same directory as the script
2. Run the script:
   ```bash
   python eibi2kiwi_online.py
   ```
3. The script will:
   - Determine the current broadcast season
   - Download the appropriate schedule file
   - Process the data
   - Generate `kiwi.csv` as output

## Output Format
The script generates a CSV file (`kiwi.csv`) with the following columns:
- Freq: Broadcast frequency in kHz
- Mode: Transmission mode (SAS [default], DRM, or USB)
- Ident: Station name
- Notes: Combined information about location, target area, and language
- Type: T3 (with language) or T4 (without language)
- DOW: Days of week in "MTWTFSS" format
- Begin/End: Broadcast time range in UTC

## Technical Notes
1. Season Definitions:
   - Season A: Last Sunday in March to last Sunday in October
   - Season B: Last Sunday in October to last Sunday in March (next year)

2. Special Handling:
   - One-day stations are filtered out
   - Out-of-season broadcasts are skipped
   - Ambiguous day patterns (e.g. 2irr, 4irr, 4u, 5o, 2o) are skipped
   - Special day ranges (MF → Mo-Fr, 2Mo-Sa → Mo-Sa) are properly handled

3. Day Format Conversions:
   - Numeric days (e.g., "1345") are converted to weekday formats
   - Ranges (e.g., "Mo-Th") are expanded
   - Special combinations (e.g., "SaSu") are handled

4. Error Handling:
   - Implements retry logic for file downloads (max 3 attempts)
   - Validates downloaded file existence
   - Handles various date format exceptions

## Limitations
- Requires active internet connection for downloading schedule files
- Cannot process certain ambiguous scheduling patterns
- Limited to formats provided by EiBi broadcast schedules

## License
This program is licensed under GNU General Public License v3.0 or later.

## Notes for Developers
1. The script uses binary write mode for output to ensure proper line endings
2. Location dictionary is case-sensitive
3. The download process includes a timeout of 3 seconds per attempt
4. Default transmission mode is set to "SAS" (pseudo-stereo AM)

## Error Handling
The script implements several error handling mechanisms:
- Download retry logic with 3 attempts
- CSV parsing error detection
- Season detection validation
- File existence checking
