from grc_utils import count_dichrona_in_open_syllables, DICHRONA, is_open_syllable_in_word_in_synapheia, normalize_word, macrons_map, syllabifier, VOWELS, word_with_real_dichrona
import re
from collections import defaultdict

# List to store marked words
output_list = []

with open('adjust_syllabification/hypotactic_all_shuffled_cleaned.txt', 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        
        # Extract plain text by removing [] and {}
        plain_text = re.sub(r'[\[\]{}]', '', line)
        words = plain_text.split()
        print(f"Line {line_num}: Words: {words}")
        
        # Compute concatenated text without spaces
        concatenated_text = ''.join(words)
        normalized_concatenated = normalize_word(concatenated_text)
        print(f"Line {line_num}: Concatenated text: {concatenated_text}")
        
        # Compute starting positions of each word in concatenated text
        start_pos = [0]
        for word in words:
            start_pos.append(start_pos[-1] + len(word))
        print(f"Line {line_num}: Word start positions: {start_pos}")
        
        # Extract syllables with their types and content
        syllables = []
        for match in re.finditer(r'(\[[^\]]+\]|\{[^\}]+\})', line):
            s = match.group(0)
            type_ = 'heavy' if s[0] == '[' else 'light'
            content = s[1:-1]
            sequence = ''.join(content.split())
            normalized_sequence = normalize_word(sequence)
            print(f"Line {line_num}: Processing syllable '{s}' (type: {type_}, sequence: {sequence}, normalized: {normalized_sequence})")
            try:
                pos = normalized_concatenated.index(normalized_sequence)
                pos = concatenated_text.index(sequence)
            except ValueError:
                print(f"Line {line_num}: Warning: Sequence '{sequence}' not found in concatenated text")
                continue
            for j, char in enumerate(sequence):
                if char in VOWELS:
                    vowel_pos = pos + j
                    print(f"Line {line_num}: Vowel '{char}' found at pos {vowel_pos} in '{sequence}'")
                    break
            else:
                print(f"Line {line_num}: Warning: No vowel in syllable '{s}'")
                continue
            for i in range(len(words)):
                if start_pos[i] <= vowel_pos < start_pos[i+1]:
                    w = words[i]
                    a = start_pos[i]
                    b = start_pos[i+1] - 1
                    p = pos
                    q = pos + len(sequence) - 1
                    start_pos_in_w = max(p, a)
                    end_pos_in_w = min(q, b)
                    start_idx = start_pos_in_w - a
                    end_idx = end_pos_in_w - a
                    syllables.append({
                        'type': type_,
                        'content': content,
                        'sequence': sequence,
                        'pos': pos,
                        'w': w,
                        'start_idx': start_idx,
                        'end_idx': end_idx
                    })
                    print(f"Line {line_num}: Assigned syllable '{sequence}' to word '{w}' (indices: {start_idx}-{end_idx})")
                    break
        
        # Group syllables by word
        syllables_by_word = defaultdict(list)
        for s in syllables:
            syllables_by_word[s['w']].append(s)
        print(f"Line {line_num}: Syllables by word: {dict(syllables_by_word)}")
        
        # Process each word
        for i, w in enumerate(words):
            # Get next word (empty string if last word)
            next_word = words[i+1] if i < len(words)-1 else ''
            print(f"Line {line_num}: Processing word '{w}' with next_word '{next_word}'")
            
            # Get syllabification
            syllabification = syllabifier(w)
            print(f"Line {line_num}: Syllabifier output for '{w}': {syllabification}")
            
            # Debug dichrona count
            dichrona_count = count_dichrona_in_open_syllables(w)
            dichrona_details = [(syl, [c for c in syl if c in DICHRONA], is_open_syllable_in_word_in_synapheia(syl, syllabification, next_word)) 
                               for syl in syllabification]
            print(f"Line {line_num}: Dichrona details for '{w}': {dichrona_details}")
            
            # Handle empty syllabification
            if not syllabification:
                print(f"Line {line_num}: Warning: Empty syllabification for '{w}', assuming no open syllables or dichrona")
                has_open_syll = False
                dichrona_count = 0
            else:
                # Check if any syllable is open
                has_open_syll = any(is_open_syllable_in_word_in_synapheia(syl, syllabification, next_word) for syl in syllabification)
                if has_open_syll is None:
                    print(f"Line {line_num}: Warning: is_open_syllable_in_word_in_synapheia returned None for some syllables in '{w}', assuming False")
                    has_open_syll = False
            
            print(f"Line {line_num}: Checking word '{w}': dichrona_count={dichrona_count}, has_open_syll={has_open_syll}")
            
            if dichrona_count > 0 and has_open_syll:
                print(f"Line {line_num}: Word '{w}' passed checks")
                sylls = syllables_by_word.get(w, [])
                if not sylls:
                    print(f"Line {line_num}: No syllables assigned to '{w}'")
                    continue
                print(f"Line {line_num}: Syllables for '{w}': {[s['sequence'] for s in sylls]}")
                insertion_dict = {}
                
                for s in sylls:
                    normalized_w = normalize_word(w)
                    for syl in syllabification:
                        normalized_syl = normalize_word(syl)
                        try:
                            syl_start = normalized_w.index(normalized_syl)
                            syl_end = syl_start + len(syl) - 1
                            print(f"Line {line_num}: Matching syllable '{syl}' (normalized: '{normalized_syl}') in '{w}' at {syl_start}-{syl_end}")
                            if syl_start <= s['start_idx'] <= syl_end:
                                corresponding_syl = syl
                                print(f"Line {line_num}: Matched syllable '{s['sequence']}' to '{syl}' in '{w}'")
                                break
                        except ValueError:
                            print(f"Line {line_num}: Warning: Syllable '{syl}' not found in normalized word '{normalized_w}'")
                            continue
                    else:
                        print(f"Line {line_num}: Warning: No matching syllable for '{s['sequence']}' in '{w}'")
                        continue
                    
                    segment = w[s['start_idx']:s['end_idx'] + 1]
                    print(f"Line {line_num}: Segment for '{s['sequence']}': '{segment}'")
                    candidates = [i for i in range(s['start_idx'], s['end_idx'] + 1) 
                                 if w[i] in DICHRONA]
                    if candidates and word_with_real_dichrona(segment):
                        print(f"Line {line_num}: Dichrona candidates in '{segment}' at indices {candidates} (chars: {[w[i] for i in candidates]}), word_with_real_dichrona={word_with_real_dichrona(segment)}")
                        i_max = max(candidates)
                        if (s['type'] == 'heavy' and 
                            is_open_syllable_in_word_in_synapheia(corresponding_syl, syllabification, next_word)):
                            insertion_dict[i_max] = '_'
                            print(f"Line {line_num}: Inserting '_' at index {i_max} for heavy syllable")
                        elif s['type'] == 'light':
                            insertion_dict[i_max] = '^'
                            print(f"Line {line_num}: Inserting '^' at index {i_max} for light syllable")
                    else:
                        print(f"Line {line_num}: No valid dichrona candidates in '{segment}' (candidates: {candidates}, word_with_real_dichrona={word_with_real_dichrona(segment)})")
                
                if insertion_dict:
                    marked_w = ''
                    for j in range(len(w)):
                        marked_w += w[j]
                        if j in insertion_dict:
                            marked_w += insertion_dict[j]
                    print(f"Line {line_num}: Marked word: '{marked_w}'")
                    output_list.append(marked_w)
            else:
                print(f"Line {line_num}: Word '{w}' failed checks (dichrona={dichrona_count}, open_syll={has_open_syll})")

output_dict = {i: word for i, word in enumerate(output_list)}

print(f"Number of entries written: {len(output_dict)}")

with open('adjust_syllabification/hypotactic_macrons.py', 'w', encoding='utf-8') as f:
    f.write("hypotactic = {\n")
    for i, word in output_dict.items():
        f.write(f'''    "{word.replace("^", "").replace("_", "")}": "{word}",\n''')
    f.write("}\n")