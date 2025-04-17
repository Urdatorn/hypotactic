'''
Updating human scanned Ancient Greek verse to use my machine syllabification,
by reshuffling coda and onset characters between syllables (without changing their weight).

[ὦ] [παῖ,] {τέ}[λος] [μὲν] [Ζεὺς] {ἔ}[χει] {βα}[ρύ]{κτυ}[πος]
[πάν][των] {ὅσ᾽} [ἔ]{στι,} [καὶ] {τί}[θησ᾽] {ὅ}[κῃ] {θέ}[λει·]
[ᾗ] [δὴ] {βο}[τὰ] {ζό}[ω]{μεν,} [οὐ]{δὲν} [εἰ]{δό}[τες]
{ὅ}[κως] {ἕ}[κα]{στον} [ἐ]{κτε}[λευ][τή][σει] {θε}[ός.]


should become:

[ὦ] [παῖ,] {τέ}[λος] [μὲν] [Ζεὺ]{ς ἔ}[χει] {βα}[ρύκ]{τυ}[πος]
[πάν][των] {ὅσ᾽} [ἔσ]{τι,} [καὶ] {τί}[θη]{σ᾽ ὅ}[κῃ] {θέ}[λει·]
[ᾗ] [δὴ] {βο}[τὰ ζ]{ό}[ω]{με}[ν, οὐ]{δὲ}[ν εἰ]{δό}[τες]
{ὅ}[κως] {ἕ}[κασ]{τον} [ἐκ]{τε}[λευ][τή][σει] {θε}[ός.]
'''

import re
from grc_utils import syllabifier

input_file = 'hypotactic_all_raw.txt'
output_file = 'hypotactic_all_shuffled.txt'

# input_file = 'hypotactic_all_raw_test.txt'
# output_file = 'hypotactic_all_shuffled_test.txt'

length_errors = 0
updated = 0
unchanged = 0

'''
>>> re.findall(segment_pattern, "[ὦ] [παῖ,] {τέ}[λος] [μὲν] [Ζεὺς] {ἔ}[χει] {βα}[ρύ]{κτυ}[πος]")
[('[', 'ὦ', ']', ' '), ('[', 'παῖ,', ']', ' '), ('{', 'τέ', '}', ''), ('[', 'λος', ']', ' '), ('[', 'μὲν', ']', ' '), ('[', 'Ζεὺς', ']', ' '), ('{', 'ἔ', '}', ''), ('[', 'χει', ']', ' '), ('{', 'βα', '}', ''), ('[', 'ρύ', ']', ''), ('{', 'κτυ', '}', ''), ('[', 'πος', ']', '')]
'''

scanned_pattern = re.compile(r"([\[{].*?[\]}]\s*)")
greek_punctuation_except_scansion = r'[\t·\u0387\u037e\u00b7\.,!?;:ʼ’᾽\"()<>\-—…†]'
greek_punctuation = r'[\xa0\t·\u0387\u037e\u00b7\.,!?;:ʼ’᾽\"()\[\]{}<>\-—…†]'

with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(output_file, 'w', encoding='utf-8') as out:
    for hypotactic in lines:
        
        hypotactic = hypotactic.strip()
        hypotactic = re.sub(greek_punctuation_except_scansion, '', hypotactic)
        hypotactic = hypotactic.replace("\xa0", " ") # non-breaking space
        if not hypotactic:
            out.write("\n")
            continue
        
        # Build scansion list
        hypotactic_sylls = re.findall(scanned_pattern, hypotactic)
        print(f"hypotactic: {hypotactic_sylls}")

        # Build scriptio continua
        cleaned_line = re.sub(greek_punctuation, '', hypotactic)
        cleaned_line = cleaned_line.replace(" ", "")
        syllabifier_sylls = syllabifier(cleaned_line)
        print(f'syllabifier: {syllabifier_sylls}')

        if len(hypotactic_sylls) != len(syllabifier_sylls):
            length_errors += 1
            print(f"[length mismatch] {len(hypotactic_sylls)} ≠ {len(syllabifier_sylls)}\n→ {hypotactic}")
            continue

        if hypotactic_sylls == syllabifier_sylls:
            unchanged += 1
            out.write(hypotactic + '\n')
            continue

        updated += 1
        surplus_coda = ''

        move_space = False
        closing_bracket = ''
        
        hypotactic_shuffled = []
        for i, (hypotactic_syll, syllabifier_syll) in enumerate(zip(hypotactic_sylls, syllabifier_sylls)):
            
            if hypotactic_syll.replace(' ', '').replace('[', '').replace(']', '').replace('{', '').replace('}', '') == syllabifier_syll:
                hypotactic_shuffled.append(hypotactic_syll)
                print(f"Unchanged syllable: |{hypotactic_syll}|")
                continue
            
            print(f"\nConsidering syllable: |{hypotactic_syll}| and {syllabifier_syll}")

            len_syllabifier_syll = len(syllabifier_syll)
            print(f"Len syllabifier_syll: {len(syllabifier_syll)}")

            new_hypotactic_syll = hypotactic_syll

            if surplus_coda:
                print(f'Surplus coda: |{surplus_coda}|')

            if not move_space:
                new_hypotactic_syll = hypotactic_syll[0] + surplus_coda + hypotactic_syll[1:]
                surplus_coda = ''

                print(f"New hypotactic syllable (no moved space): |{new_hypotactic_syll}|")

            elif move_space:
                new_hypotactic_syll = hypotactic_syll[0] + surplus_coda + ' ' + hypotactic_syll[1:]
                surplus_coda = ''
                move_space = False

                print(f"New hypotactic syllable (moved space): |{new_hypotactic_syll}|")

            new_hypotactic_syll_comparable = new_hypotactic_syll.replace(' ', '').replace('[', '').replace(']', '').replace('{', '').replace('}', '')
            if new_hypotactic_syll_comparable < syllabifier_syll:
                print(f"\thypotactic_syll < syllabifier_syll!")
                
                next_syll = hypotactic_sylls[i + 1] if i + 1 < len(hypotactic_sylls) else ''
                length_diff = len(syllabifier_syll) - len(new_hypotactic_syll_comparable)
                print(f"\tLength difference: {length_diff}")
                deficit_coda = syllabifier_syll[-length_diff:]
                print(f"\tDeficit coda: |{deficit_coda}|")

                if new_hypotactic_syll[-1] == ' ':
                    new_hypotactic_syll = new_hypotactic_syll[:-2] + ' ' + deficit_coda + new_hypotactic_syll[-2]

                else:
                    new_hypotactic_syll = new_hypotactic_syll[:-1] + deficit_coda + new_hypotactic_syll[-1]

                if next_syll:
                    print(f"\tNext syllable: |{next_syll}|")
                    hypotactic_sylls[i + 1] = next_syll[0] + hypotactic_sylls[i + 1][length_diff + 1:]
                    print(f"\tShortened next syllable to |{hypotactic_sylls[i + 1]}|")

                print(f"\tShuffled hypotactic syllable: |{new_hypotactic_syll}|")
                hypotactic_shuffled.append(new_hypotactic_syll)
                
                continue
            
            temporary_new_hypotactic_syll = new_hypotactic_syll[:-1].replace(' ', '') + new_hypotactic_syll[-1] # removing onset spaces from indexing
            for i, hypotactic_char in enumerate(temporary_new_hypotactic_syll):
                
                if hypotactic_char == '[':
                    closing_bracket = ']'

                elif hypotactic_char == '{':
                    closing_bracket = '}'

                if hypotactic_char in ['[', ']', '{', '}']:
                    continue

                print(f"i = {i}: {hypotactic_char}|")

                if hypotactic_char == ' ' and surplus_coda:
                    move_space = True
                    print(f"Move space: {move_space}")
                    continue

                elif hypotactic_char == ' ':
                    continue

                elif i > len_syllabifier_syll:
                    print(f"{i} > {len(syllabifier_syll)}")
                    surplus_coda += hypotactic_char
                    print(f"Updated surplus coda: |{surplus_coda}|")

            if surplus_coda and move_space:
                end_index = -len(surplus_coda) - 2
                print(f"End index: {end_index}")
                new_hypotactic_syll = new_hypotactic_syll[:end_index] + closing_bracket

            elif surplus_coda and not move_space:
                end_index = -len(surplus_coda) - 1
                print(f"End index: {end_index}")
                new_hypotactic_syll = new_hypotactic_syll[:end_index] + closing_bracket

            print(f"Shuffled hypotactic syllable: |{new_hypotactic_syll}|")
            hypotactic_shuffled.append(new_hypotactic_syll)
        
        print(f"\033[32mShuffled line: {hypotactic_shuffled}\033[0m\n")
        
        out.write("".join(hypotactic_shuffled) + "\n")

print(f"Done!\nLength errors: {length_errors}\nUnchanged lines: {unchanged}\nUpdated lines: {updated}")


def test():
    print("\n\nTesting for mismatches...")
    with open('hypotactic_all_check_test.txt', 'r', encoding='utf-8') as f1:
        lines_check = f1.readlines()
        with open('hypotactic_all_shuffled_test.txt', 'r', encoding='utf-8') as f2:
            lines_shuffled = f2.readlines()
            for line_check, line_shuffled in zip(lines_check, lines_shuffled):
                if line_check != line_shuffled:
                    print(f"Mismatch:\n{line_check}(should be)\n{line_shuffled}(is)")
                else:
                    print("Match!")
#test()
            