def check_unclosed_parentheses(file_path, output_file=None):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            # Stack to track opening brackets and their line numbers
            stack = []
            # List to collect all errors
            errors = []
            # Set to track lines with errors
            error_lines = set()
            # Dictionary to map closing brackets to their corresponding opening brackets
            brackets = {')': '(', ']': '[', '}': '{'}
            # Valid opening brackets
            opening = set(['(', '[', '{'])
            
            for line_num, line in enumerate(lines, 1):  # 1-based line numbering
                for char in line:
                    if char in opening:
                        stack.append((char, line_num))
                    elif char in brackets:
                        if not stack:
                            errors.append(f"Unmatched closing bracket '{char}' found at line {line_num}:")
                            errors.append(f"  {line.strip()}")
                            error_lines.add(line_num)
                        elif stack[-1][0] != brackets[char]:
                            errors.append(f"Mismatched bracket at line {line_num}: Expected closing for '{stack[-1][0]}' (opened at line {stack[-1][1]}) but found '{char}':")
                            errors.append(f"  {line.strip()}")
                            error_lines.add(line_num)
                            stack.pop()  # Remove the mismatched opening bracket
                        else:
                            stack.pop()  # Valid match, remove the opening bracket
            
            # Check for unclosed opening brackets
            if stack:
                errors.append("Unclosed opening bracket(s) found:")
                for bracket, line_num in stack:
                    errors.append(f" '{bracket}' at line {line_num}:")
                    errors.append(f"  {lines[line_num-1].strip()}")
                    error_lines.add(line_num)
            
            # Print errors
            if errors:
                for error in errors:
                    print(error)
            else:
                print("All brackets are properly closed.")
            
            # Remove lines with errors and save to output file
            removed_count = len(error_lines)
            if removed_count > 0:
                # Create new content excluding error lines
                new_lines = [line for i, line in enumerate(lines, 1) if i not in error_lines]
                
                # If no output file specified, create one with '_cleaned' suffix
                if output_file is None:
                    output_file = file_path.rsplit('.', 1)[0] + '_cleaned.txt'
                
                with open(output_file, 'w', encoding='utf-8') as file:
                    file.writelines(new_lines)
                
                print(f"Removed {removed_count} line(s) with bracket errors.")
                print(f"Cleaned file saved as '{output_file}'.")
            else:
                print("No lines were removed.")
            
            return not errors  # Return True if no errors, False otherwise
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

input_file = 'hypotactic_all_raw.txt'
output_file = 'hypotactic_all_shuffled.txt'
check_unclosed_parentheses(output_file)