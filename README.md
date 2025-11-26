# Tableau Workbook Translator

This script translates Tableau workbook (.twb) files to any language using Claude API.

## Features

- ✓ Translates worksheet and dashboard names
- ✓ Translates captions, aliases, and labels
- ✓ Translates text in descriptions and rich text boxes
- ✓ **Supports translation to any language** (default: English)
- ✓ Preserves place names and company names
- ✓ Maintains Tableau technical terminology correctly
- ✓ Keeps all XML structure and tags intact
- ✓ Creates automatic backups
- ✓ Validates XML before and after translation

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install anthropic
   ```

2. **Set your Anthropic API key:**
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

## Usage

### Basic Usage (translate to English)

```bash
python translate_tableau.py "Viljandimaa ÜTK.twb"
```

This will create `Viljandimaa ÜTK_EN.twb` in English.

### Translate to Other Languages

```bash
# Translate to French
python translate_tableau.py "Viljandimaa ÜTK.twb" --language French

# Translate to German
python translate_tableau.py "Viljandimaa ÜTK.twb" -l German

# Translate to Spanish
python translate_tableau.py "Viljandimaa ÜTK.twb" -l Spanish
```

### Custom Output File

```bash
# Specify custom output filename
python translate_tableau.py input.twb -l French -o my_french_version.twb
```

### Command-Line Options

```
usage: translate_tableau.py [-h] [-l LANGUAGE] [-o OUTPUT] [input_file]

Translate Tableau workbook (.twb) files to any language using Claude API

positional arguments:
  input_file            Input Tableau workbook file

optional arguments:
  -h, --help            show this help message and exit
  -l LANGUAGE, --language LANGUAGE
                        Target language for translation (default: English)
  -o OUTPUT, --output OUTPUT
                        Output file path (default: auto-generated)
```

## Supported Languages

The script supports translation to any language. Common examples:

- English (default) → creates `*_EN.twb`
- French → creates `*_FR.twb`
- German → creates `*_DE.twb`
- Spanish → creates `*_ES.twb`
- Italian → creates `*_IT.twb`
- Portuguese → creates `*_PT.twb`
- Russian → creates `*_RU.twb`
- Chinese → creates `*_ZH.twb`
- Japanese → creates `*_JP.twb`
- Korean → creates `*_KR.twb`
- Dutch → creates `*_NL.twb`
- Polish → creates `*_PL.twb`
- Swedish → creates `*_SE.twb`
- Finnish → creates `*_FI.twb`
- Norwegian → creates `*_NO.twb`
- Danish → creates `*_DK.twb`

## What Gets Translated

- Worksheet names (e.g., "Aasta muutus" → "Year Change")
- Dashboard names (e.g., "Detailne ülevaade" → "Detailed Overview")
- Field captions and labels
- Parameter names and values
- Aliases for fields and members
- Text in descriptions and rich text boxes
- Zone names and references
- Window and thumbnail names

## What Stays the Same

- All XML structure and tags
- Place names (Viljandimaa, Tartu, etc.)
- Company names
- Database field names
- Technical Tableau terminology
- Data values and calculations

## Output

The script automatically:
1. Creates a timestamped backup of the original file
2. Generates output filename based on language code
3. Validates XML before and after translation
4. Shows detailed progress during translation

Example output:
```
============================================================
Tableau Workbook Translator
============================================================
Input:    Viljandimaa ÜTK.twb
Output:   Viljandimaa ÜTK_FR.twb
Language: French
============================================================

Reading file: /path/to/Viljandimaa ÜTK.twb
Target language: French
✓ Backup created: Viljandimaa ÜTK_backup_20250126_143022.twb

Validating original XML...
✓ Original XML is well-formed

Extracting translatable texts...
Found 245 unique texts to translate:
  - worksheet_names: 20 items
  - dashboard_names: 2 items
  - captions: 85 items
  - aliases: 45 items
  - descriptions: 93 items

...
```

## Troubleshooting

**Error: "Please set ANTHROPIC_API_KEY environment variable"**
- Make sure you've set your API key: `export ANTHROPIC_API_KEY="your-key"`

**Error: "Input file not found"**
- Check the file path is correct
- Use quotes around filenames with spaces

**XML Validation Failed**
- Check the console output for specific XML errors
- The script creates a backup - you can restore from it
- Review which translations may have caused issues

## Cost Estimate

- Typical cost: $0.10-0.50 per file (depending on file size and language)
- Uses Claude Sonnet 4.5 model for high-quality translations

## Examples

```bash
# Translate Estonian workbook to English
python translate_tableau.py "Viljandimaa ÜTK.twb"

# Translate to French with API key inline
ANTHROPIC_API_KEY="sk-..." python translate_tableau.py input.twb -l French

# Translate to multiple languages
python translate_tableau.py input.twb -l German
python translate_tableau.py input.twb -l French
python translate_tableau.py input.twb -l Spanish

# Use absolute path
python translate_tableau.py "/full/path/to/file.twb" -l Italian
```

## Notes

- The original file is never modified
- Backups are created automatically with timestamps
- The script preserves exact XML formatting to maintain Tableau references
- Translation happens in batches of 20 items to optimize API usage
- Progress is shown in the console during translation
- All worksheet/dashboard references are synchronized
