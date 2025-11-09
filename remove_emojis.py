#!/usr/bin/env python3
"""
Script to remove all emojis from Python files and documentation
"""
import os
import re

def remove_emojis_from_file(filepath):
    """Remove common emojis from a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Define emoji replacements (more comprehensive)
        emoji_replacements = {
            '🔍': '[DEBUG]',
            '✅': '[SUCCESS]',
            '❌': '[ERROR]',
            '⚠️': '[WARNING]',
            'ℹ️': '[INFO]', 
            '🔄': '[PROCESSING]',
            '📧': '[EMAIL]',
            '🚨': '[ALERT]',
            '✨': '',
            '📊': '[STATS]'
        }
        
        # Replace emojis one by one
        for emoji, replacement in emoji_replacements.items():
            if emoji in content:
                print(f"  Replacing {emoji} with '{replacement}' in {filepath}")
                content = content.replace(emoji, replacement)
        
        # Clean up any double spaces that might result from empty replacements
        content = re.sub(r'  +', ' ', content)
        content = re.sub(r'\n\n\n+', '\n\n', content)
        
        # Write back if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {filepath}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    # Get all Python files and markdown files in the current directory
    files_to_process = []
    
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        if any(skip_dir in root for skip_dir in ['.git', '__pycache__', 'node_modules', 'venv', '.env']):
            continue
            
        for file in files:
            if file.endswith(('.py', '.md', '.html')) and not file.startswith('remove_emojis'):
                files_to_process.append(os.path.join(root, file))
    
    print(f"Found {len(files_to_process)} files to process...")
    
    updated_count = 0
    for filepath in files_to_process:
        if remove_emojis_from_file(filepath):
            updated_count += 1
    
    print(f"\nCompleted! Updated {updated_count} files.")
    
    # Run a final check for any remaining emojis
    print("\nChecking for any remaining emojis...")
    remaining_emojis = []
    for filepath in files_to_process:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if any(emoji in content for emoji in ['🔍', '✅', '❌', '⚠️', 'ℹ️', '🔄', '📧', '🚨', '✨', '📊']):
                    remaining_emojis.append(filepath)
        except:
            pass
    
    if remaining_emojis:
        print(f"WARNING: Found emojis still remaining in {len(remaining_emojis)} files:")
        for file in remaining_emojis:
            print(f"  - {file}")
    else:
        print("SUCCESS: No emojis found in any files!")

if __name__ == "__main__":
    main()