# Tableau Workbook Translation Script

This script translates Estonian text in Tableau workbook (.twb) files to English using Claude API.

## Features

- ✓ Translates worksheet and dashboard names
- ✓ Translates captions, aliases, and labels
- ✓ Translates text in descriptions and rich text boxes
- ✓ Preserves place names and company names (e.g., "Viljandimaa", "Tartu")
- ✓ Maintains Tableau technical terminology correctly
- ✓ Keeps all XML structure and tags intact
- ✓ Creates a new file (doesn't modify the original)

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your Anthropic API key:**

   **Option A - Environment variable (recommended):**
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

   **Option B - In the script:**
   Edit `translate_tableau.py` and replace:
   ```python
   ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
   ```
   with:
   ```python
   ANTHROPIC_API_KEY = "your-api-key-here"
   ```

3. **Verify the input file name:**
   - Default: `Viljandimaa ÜTK.twb`
   - If your file has a different name, edit the `INPUT_FILE` variable in the script

## Usage

Run the script:
```bash
python translate_tableau.py
```

The script will:
1. Read `Viljandimaa ÜTK.twb`
2. Extract all Estonian texts
3. Translate them using Claude API (in batches)
4. Create a new file: `Viljandimaa ÜTK_EN.twb`

## Output

The translated file will be created in the same directory:
- **Input:** `Viljandimaa ÜTK.twb`
- **Output:** `Viljandimaa ÜTK_EN.twb`

## What Gets Translated

- Worksheet names (e.g., "Aasta muutus" → "Year Change")
- Dashboard names (e.g., "Detailne ülevaade" → "Detailed Overview")
- Field captions and labels
- Parameter names and values
- Aliases for fields and members
- Text in descriptions and rich text boxes

## What Stays the Same

- All XML structure and tags
- Place names (Viljandimaa, Tartu, etc.)
- Company names
- Database field names
- Technical Tableau terminology

## Troubleshooting

**Error: "Please set ANTHROPIC_API_KEY environment variable"**
- Make sure you've set your API key (see Setup step 2)

**Error: "Input file not found"**
- Check that the file name in `INPUT_FILE` matches your actual file name
- Make sure the script is in the same directory as the .twb file

**Translations seem incorrect:**
- The script uses Claude Sonnet 4.5 for high-quality translations
- Place names and technical terms are preserved by design
- Review the console output to see example translations

## Cost Estimate

- The script processes text in batches
- Typical cost: $0.10-0.50 per file (depending on file size)
- Uses Claude Sonnet 4.5 model

## Notes

- The original file is never modified
- The script preserves exact XML formatting to maintain Tableau references
- Translation happens in batches of 20 items to optimize API usage
- Progress is shown in the console during translation
