# IMDB Werstreamt.es Comparison Tool

A Python application that compares IMDB and Werstreamt.es movie databases to find movies that are in IMDB but not available on Werstreamt.es.

## Features

- **Smart Comparison**: Compares movies using both original titles and localized titles
- **Web Verification**: Verifies missing entries by checking Werstreamt.es search results
- **Modern GUI**: Clean and intuitive interface with progress tracking
- **Click-to-Copy**: Click any cell in the results to copy its content
- **Export**: Save results to CSV for further analysis

## Requirements

- Python 3.x
- Required packages (install via `pip install -r requirements.txt`):
  - pandas
  - requests
  - beautifulsoup4

## Installation

1. Clone or download this repository
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python Werstreamtes.py
   ```

2. Select your input files:
   - IMDB Database (CSV format with 'Original Title' and 'Title' columns)
   - Werstreamt.es Database (CSV format with 'OriginalTitle' and 'Title' columns)

3. Click "Load & Compare Files" to start the comparison

4. The application will:
   - Compare the databases to find potential missing entries
   - Verify each missing entry by checking Werstreamt.es search results
   - Display confirmed missing entries in the results table

5. Working with Results:
   - Click any cell in the results to copy its content
   - Use the export button to save results as CSV
   - Results include: IMDB ID, Title, Original Title, Year, Rating, and more

## File Format Requirements

### IMDB CSV
Required columns:
- Original Title
- Title
- Year
- URL (containing IMDB ID)

### Werstreamt.es CSV
Required columns:
- OriginalTitle
- Title

## Notes

- The application automatically loads IMDB.csv and Werstreamtes.csv if they exist in the same directory
- Progress bar shows verification status for each entry
- The tool includes a delay between web requests to avoid overwhelming the Werstreamt.es server
- Entries are only considered missing after verification through the Werstreamt.es website
