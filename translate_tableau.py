#!/usr/bin/env python3
"""
Tableau Workbook (.twb) Translator
Uses Claude API to translate user-facing text while preserving XML structure
Supports translation to any language (default: English)
"""

import re
import os
import sys
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime
from anthropic import Anthropic

# Configuration
INPUT_FILE = "Viljandimaa ÜTK.twb"
TARGET_LANGUAGE = "English"  # Default target language
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")  # Set your API key as environment variable

if not ANTHROPIC_API_KEY:
    raise ValueError("Please set ANTHROPIC_API_KEY environment variable")

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def get_language_code(language):
    """Convert language name to ISO code for file naming"""
    language_codes = {
        'english': 'EN',
        'french': 'FR',
        'german': 'DE',
        'spanish': 'ES',
        'italian': 'IT',
        'portuguese': 'PT',
        'russian': 'RU',
        'chinese': 'ZH',
        'japanese': 'JP',
        'korean': 'KR',
        'dutch': 'NL',
        'polish': 'PL',
        'swedish': 'SE',
        'finnish': 'FI',
        'norwegian': 'NO',
        'danish': 'DK',
    }
    return language_codes.get(language.lower(), language[:2].upper())


def create_backup(file_path):
    """Create a backup of the original file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.replace('.twb', f'_backup_{timestamp}.twb')

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ Backup created: {os.path.basename(backup_path)}")
    return backup_path


def validate_xml(content):
    """Validate that the content is well-formed XML"""
    try:
        # Try to parse the XML
        ET.fromstring(content)
        return True, "XML is well-formed"
    except ET.ParseError as e:
        return False, f"XML parse error: {e}"


def translate_with_claude(text_items, target_language="English", context=""):
    """
    Translate a list of text items to target language using Claude API
    Returns a dictionary mapping original text to translated text
    """
    if not text_items:
        return {}

    # Create prompt for Claude
    prompt = f"""Translate the following texts to {target_language}.

IMPORTANT RULES:
1. Keep place names and company names as they are (e.g., "Viljandimaa", "Tartu", "TK", "ÜTK")
2. Preserve Tableau technical terminology exactly as it should be in {target_language}
3. Only translate the user-facing labels and descriptions
4. Do NOT include any special characters that need XML escaping (use plain quotes, not &quot;)
5. Return ONLY a numbered list with translations, one per line
6. Keep the same order as the input

Context: {context}

Texts to translate:
{chr(10).join(f"{i+1}. {text}" for i, text in enumerate(text_items))}

Return format (plain text only, no special XML characters):
1. [translation of first item]
2. [translation of second item]
etc.
"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Parse response
        response_text = response.content[0].text
        translations = {}

        # Extract translations from numbered list
        lines = response_text.strip().split('\n')
        for i, line in enumerate(lines):
            # Remove numbering (e.g., "1. ", "2. ", etc.)
            match = re.match(r'^\d+\.\s*(.*)', line)
            if match and i < len(text_items):
                translated = match.group(1).strip()
                # Clean up any accidentally included quotes
                translated = translated.strip('"').strip("'")
                translations[text_items[i]] = translated

        return translations

    except Exception as e:
        print(f"Error translating batch: {e}")
        return {}


def extract_translatable_texts(content):
    """
    Extract all Estonian texts that need translation from the Tableau workbook
    Returns a dictionary of {pattern_type: [(original, context)]} for batch translation
    """
    texts_to_translate = {
        'worksheet_names': [],
        'dashboard_names': [],
        'captions': [],
        'aliases': [],
        'descriptions': [],
        'members': []
    }

    # Extract worksheet names
    worksheet_pattern = r"<worksheet name='([^']+)'>"
    texts_to_translate['worksheet_names'] = list(set(re.findall(worksheet_pattern, content)))

    # Extract dashboard names
    dashboard_pattern = r"<dashboard name='([^']+)'>"
    texts_to_translate['dashboard_names'] = list(set(re.findall(dashboard_pattern, content)))

    # Extract captions (avoiding technical field names and those with special chars)
    caption_pattern = r"caption='([^']+)'"
    captions = re.findall(caption_pattern, content)
    # Filter out technical names and those with XML entities
    texts_to_translate['captions'] = list(set([c for c in captions
                                                if not re.match(r'^[a-z_]+$', c)
                                                and '[' not in c
                                                and not c.startswith('.')
                                                and '&' not in c]))

    # Extract alias values from <alias> tags
    alias_pattern = r"<alias key='[^']+' value='([^']+)' />"
    aliases = re.findall(alias_pattern, content)
    texts_to_translate['aliases'] = list(set([a for a in aliases if '&' not in a]))

    # Extract member aliases
    member_pattern = r"<member alias='([^']+)'"
    members = re.findall(member_pattern, content)
    texts_to_translate['members'] = list(set([m for m in members if '&' not in m]))

    # Extract text from <run> tags (rich text descriptions) - including those with attributes
    run_pattern = r"<run[^>]*>([^<]+)</run>"
    descriptions = re.findall(run_pattern, content)
    # Filter out very short texts and those with XML entities
    texts_to_translate['descriptions'] = list(set([d.strip() for d in descriptions
                                                     if '&' not in d
                                                     and len(d.strip()) > 0]))

    return texts_to_translate


def escape_xml_attr(text):
    """
    Escape special characters for XML attributes
    """
    # Escape XML special characters
    text = text.replace('&', '&amp;')  # Must be first
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace("'", '&apos;')
    text = text.replace('"', '&quot;')
    return text


def safe_replace(content, original, translated):
    """
    Safely replace text in specific XML attribute contexts without breaking entities
    """
    if not original or not translated or original == translated:
        return content, 0

    replacements = 0

    # Escape special regex characters in original text
    escaped_original = re.escape(original)

    # Escape XML special characters in translated text
    xml_safe_translated = escape_xml_attr(translated)

    # Replace in specific attribute contexts only
    # 1. Worksheet/Dashboard name definitions
    pattern1 = f"(<(?:worksheet|dashboard) name=')({escaped_original})(')"
    content, count1 = re.subn(pattern1, f"\\1{xml_safe_translated}\\3", content)
    replacements += count1

    # 1b. Dashboard references (in source elements)
    pattern1b = f"(dashboard=')({escaped_original})(')"
    content, count1b = re.subn(pattern1b, f"\\1{xml_safe_translated}\\3", content)
    replacements += count1b

    # 1c. Worksheet references (in source and other elements)
    pattern1c = f"(worksheet=')({escaped_original})(')"
    content, count1c = re.subn(pattern1c, f"\\1{xml_safe_translated}\\3", content)
    replacements += count1c

    # 1d. Zone name references (worksheets in dashboard zones)
    pattern1d = f"(<zone[^>]*name=')({escaped_original})(')"
    content, count1d = re.subn(pattern1d, f"\\1{xml_safe_translated}\\3", content)
    replacements += count1d

    # 1e. Action target values (ONLY in param elements with name='target')
    pattern1e = f"(<param name='target' value=')({escaped_original})(')"
    content, count1e = re.subn(pattern1e, f"\\1{xml_safe_translated}\\3", content)
    replacements += count1e

    # 1f. Window names (for worksheets and dashboards)
    pattern1f = f"(<window class='(?:worksheet|dashboard)'[^>]*name=')({escaped_original})(')"
    content, count1f = re.subn(pattern1f, f"\\1{xml_safe_translated}\\3", content)
    replacements += count1f

    # 1g. Thumbnail names (for worksheets and dashboards)
    pattern1g = f"(<thumbnail[^>]*name=')({escaped_original})(')"
    content, count1g = re.subn(pattern1g, f"\\1{xml_safe_translated}\\3", content)
    replacements += count1g

    # 1h. Viewpoint names (saved views)
    pattern1h = f"(<viewpoint[^>]*name=')({escaped_original})(')"
    content, count1h = re.subn(pattern1h, f"\\1{xml_safe_translated}\\3", content)
    replacements += count1h

    # 2. Captions
    pattern2 = f"(caption=')({escaped_original})(')"
    content, count2 = re.subn(pattern2, f"\\1{xml_safe_translated}\\3", content)
    replacements += count2

    # 3. Alias values
    pattern3 = f"(<alias key='[^']+' value=')({escaped_original})(' />)"
    content, count3 = re.subn(pattern3, f"\\1{xml_safe_translated}\\3", content)
    replacements += count3

    # 4. Member aliases
    pattern4 = f"(<member alias=')({escaped_original})(')"
    content, count4 = re.subn(pattern4, f"\\1{xml_safe_translated}\\3", content)
    replacements += count4

    # 5. Run tags (text content) - including those with attributes
    pattern5 = f"(<run[^>]*>)({escaped_original})(</run>)"
    content, count5 = re.subn(pattern5, f"\\1{xml_safe_translated}\\3", content)
    replacements += count5

    # Also handle run tags with leading/trailing whitespace
    pattern5b = f"(<run[^>]*>)\\s*({escaped_original})\\s*(</run>)"
    content, count5b = re.subn(pattern5b, f"\\1{xml_safe_translated}\\3", content)
    replacements += count5b

    return content, replacements


def translate_file(input_path, output_path, target_language="English"):
    """
    Main function to translate the Tableau workbook file
    """
    print(f"Reading file: {input_path}")
    print(f"Target language: {target_language}")

    # Create backup
    backup_path = create_backup(input_path)

    # Read the entire file
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Validate original XML
    print("\nValidating original XML...")
    is_valid, message = validate_xml(content)
    if not is_valid:
        print(f"✗ Warning: Original file has XML issues: {message}")
        print("  Proceeding anyway, but review the results carefully.")
    else:
        print("✓ Original XML is well-formed")

    print("\nExtracting translatable texts...")
    texts_by_type = extract_translatable_texts(content)

    # Show what we found
    total_items = sum(len(items) for items in texts_by_type.values())
    print(f"\nFound {total_items} unique texts to translate:")
    for text_type, items in texts_by_type.items():
        if items:
            print(f"  - {text_type}: {len(items)} items")

    # Translate each category
    all_translations = {}
    batch_size = 20  # Translate in batches to avoid token limits

    for text_type, items in texts_by_type.items():
        if not items:
            continue

        print(f"\nTranslating {text_type} to {target_language}...")

        # Process in batches
        for i in range(0, len(items), batch_size):
            batch = items[i:i+batch_size]
            print(f"  Batch {i//batch_size + 1}: {len(batch)} items")

            translations = translate_with_claude(batch, target_language=target_language, context=text_type)
            all_translations.update(translations)

            # Show some examples
            for orig, trans in list(translations.items())[:3]:
                print(f"    '{orig}' → '{trans}'")

    print(f"\nTotal translations: {len(all_translations)}")

    # Apply translations to content
    print("\nApplying translations...")
    translated_content = content
    total_replacements = 0

    # Sort by length (longest first) to avoid partial replacements
    sorted_translations = sorted(all_translations.items(), key=lambda x: len(x[0]), reverse=True)

    for original, translated in sorted_translations:
        translated_content, count = safe_replace(translated_content, original, translated)
        total_replacements += count
        if count > 0:
            print(f"  Replaced '{original}' ({count} occurrences)")

    print(f"\nTotal replacements made: {total_replacements}")

    # Validate translated XML
    print("\nValidating translated XML...")
    is_valid, message = validate_xml(translated_content)
    if not is_valid:
        print(f"✗ ERROR: Translated XML is not well-formed: {message}")
        print(f"  The translation may have introduced errors.")
        print(f"  Backup file preserved at: {backup_path}")
        print(f"  Attempting to save anyway for inspection...")
    else:
        print("✓ Translated XML is well-formed")

    # Write translated content
    print(f"\nWriting translated file: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(translated_content)

    print(f"\n{'='*60}")
    print(f"✓ Translation complete!")
    print(f"{'='*60}")
    print(f"  Input:        {os.path.basename(input_path)}")
    print(f"  Output:       {os.path.basename(output_path)}")
    print(f"  Backup:       {os.path.basename(backup_path)}")
    print(f"  Translations: {len(all_translations)}")
    print(f"  Replacements: {total_replacements}")
    print(f"  XML Valid:    {'Yes' if is_valid else 'No - Check file!'}")
    print(f"{'='*60}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Translate Tableau workbook (.twb) files to any language using Claude API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Translate to English (default)
  python translate_tableau.py input.twb

  # Translate to French
  python translate_tableau.py input.twb -l French

  # Translate to German with custom output file
  python translate_tableau.py input.twb -l German -o output_DE.twb
        """
    )

    parser.add_argument('input_file', nargs='?', default=INPUT_FILE,
                        help=f'Input Tableau workbook file (default: {INPUT_FILE})')
    parser.add_argument('-l', '--language', default=TARGET_LANGUAGE,
                        help=f'Target language for translation (default: {TARGET_LANGUAGE})')
    parser.add_argument('-o', '--output', default=None,
                        help='Output file path (default: auto-generated based on input file and language)')

    args = parser.parse_args()

    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Input file path
    if os.path.isabs(args.input_file):
        input_path = args.input_file
    else:
        input_path = os.path.join(script_dir, args.input_file)

    # Output file path
    if args.output:
        if os.path.isabs(args.output):
            output_path = args.output
        else:
            output_path = os.path.join(script_dir, args.output)
    else:
        # Auto-generate output filename based on language
        lang_code = get_language_code(args.language)
        base_name = os.path.splitext(args.input_file)[0]
        output_path = os.path.join(script_dir, f"{base_name}_{lang_code}.twb")

    # Validate input file
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    # Show configuration
    print(f"{'='*60}")
    print(f"Tableau Workbook Translator")
    print(f"{'='*60}")
    print(f"Input:    {os.path.basename(input_path)}")
    print(f"Output:   {os.path.basename(output_path)}")
    print(f"Language: {args.language}")
    print(f"{'='*60}\n")

    try:
        translate_file(input_path, output_path, target_language=args.language)
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"Error during translation: {e}")
        print(f"{'='*60}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
