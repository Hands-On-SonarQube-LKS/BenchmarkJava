#!/usr/bin/env python3
"""
Script to fix PreparedStatement resources that are not being closed properly.
Converts regular try blocks to try-with-resources blocks.
"""

import os
import re
import glob

def fix_preparedstatement_in_file(filepath):
    """Fix PreparedStatement resource management in a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern to match try { Connection; PreparedStatement; ... } catch
    # We need to find the entire try block and convert it to try-with-resources
    pattern = re.compile(
        r'try\s*\{\s*\n'  # try {
        r'(\s+)(java\.sql\.Connection\s+connection\s*=\s*[^;]+;)\s*\n'  # Connection line
        r'(\s+)(java\.sql\.PreparedStatement\s+statement\s*=[^;]+;\s*\n)'  # PreparedStatement (might be multiline)
        r'((?:(?!\s*\} catch).)*?)'  # Capture everything until } catch (non-greedy)
        r'(\s*)\}\s*catch',  # } catch
        re.MULTILINE | re.DOTALL
    )
    
    def replace_try_block(match):
        indent = match.group(1)
        connection_line = match.group(2)
        stmt_indent = match.group(3)
        statement_lines = match.group(4)
        body_content = match.group(5)
        closing_indent = match.group(6)
        
        # Remove the statement_lines ending newline/spaces to process it better
        statement_clean = statement_lines.rstrip()
        
        # Build the try-with-resources block
        result = f'try ({connection_line}\n'
        result += f'{stmt_indent}{statement_clean}) {{\n'
        result += body_content
        result += f'{closing_indent}}} catch'
        
        return result
    
    content = pattern.sub(replace_try_block, content)
    
    # If content changed, write it back
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Main function to fix all Java files in the testcode directory."""
    testcode_dir = '/home/adrian/devops_lks/hands-on-sonar-bilbao/BenchmarkJava/src/main/java/org/owasp/benchmark/testcode'
    
    java_files = glob.glob(os.path.join(testcode_dir, '*.java'))
    
    fixed_count = 0
    for filepath in java_files:
        try:
            if fix_preparedstatement_in_file(filepath):
                fixed_count += 1
                print(f'Fixed: {os.path.basename(filepath)}')
        except Exception as e:
            print(f'Error fixing {os.path.basename(filepath)}: {e}')
    
    print(f'\nTotal files fixed: {fixed_count} out of {len(java_files)}')

if __name__ == '__main__':
    main()
