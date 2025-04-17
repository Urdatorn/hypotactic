from bs4 import BeautifulSoup
from pathlib import Path

def format_meter_line(line_div):
    formatted_line = []
    for word in line_div.select('span.word'):
        formatted_word = ''
        for syll in word.select('span.syll'):
            text = syll.get_text()
            if 'long' in syll['class']:
                formatted_word += f'[{text}]'
            elif 'short' in syll['class']:
                formatted_word += f'{{{text}}}'
        if formatted_word:
            formatted_line.append(formatted_word)
    return ' '.join(formatted_line)

# === Main script ===
input_dir = Path('hypotactic_htmls_greek')
output_file = Path('hypotactic_all_raw.txt')

all_formatted_lines = []

for html_file in input_dir.glob('*.html'):
    print(f"Processing {html_file.name}")
    with open(html_file, encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    for line_div in soup.select('div.line'):
        formatted = format_meter_line(line_div)
        if formatted.strip():
            all_formatted_lines.append(formatted)

# Write to output
with open(output_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(all_formatted_lines))

print(f"✅ Done. Output saved to {output_file}")