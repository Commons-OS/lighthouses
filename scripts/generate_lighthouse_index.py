#!/usr/bin/env python3
"""
Generate a lighthouse index JSON file from all lighthouse markdown files.
This index is used by the Commons Suit GPT to discover and reference lighthouses.
"""

import json
import os
import re
import yaml
from pathlib import Path
from datetime import datetime

def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                return yaml.safe_load(parts[1]), parts[2]
            except yaml.YAMLError:
                return {}, content
    return {}, content

def extract_patterns_section(content):
    """Extract the Commons Patterns in Action section."""
    match = re.search(r'## Commons Patterns in Action\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    if match:
        # Extract pattern names from headers
        patterns = re.findall(r'### ([^\n]+)', match.group(1))
        return patterns
    return []

def generate_slug(filepath):
    """Generate URL slug from filepath."""
    filename = os.path.basename(filepath)
    return filename.replace('.md', '')

def process_lighthouse(filepath):
    """Process a single lighthouse file and extract metadata."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    frontmatter, body = extract_frontmatter(content)
    
    # Extract key metadata from frontmatter
    return {
        'slug': generate_slug(filepath),
        'title': frontmatter.get('title', generate_slug(filepath).title()),
        'tagline': frontmatter.get('tagline', ''),
        'description': frontmatter.get('description', ''),
        'type': frontmatter.get('type', 'organization'),
        'country': frontmatter.get('country', ''),
        'sector': frontmatter.get('sector', ''),
        'founded': frontmatter.get('founded', ''),
        'employees': frontmatter.get('employees', ''),
        'patterns_used': frontmatter.get('patterns_used', []),
        'tags': frontmatter.get('tags', []),
        'file': os.path.basename(filepath)
    }

def main():
    # Find lighthouses directory
    script_dir = Path(__file__).parent
    lighthouses_dir = script_dir.parent / '_lighthouses'
    
    if not lighthouses_dir.exists():
        print(f"Error: Lighthouses directory not found at {lighthouses_dir}")
        return
    
    # Process all lighthouse files
    lighthouses = []
    for filepath in sorted(lighthouses_dir.glob('*.md')):
        try:
            lighthouse = process_lighthouse(filepath)
            lighthouses.append(lighthouse)
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
    
    # Generate index
    index = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'total_lighthouses': len(lighthouses),
        'by_type': {},
        'by_sector': {},
        'lighthouses': lighthouses
    }
    
    # Calculate distributions
    for lh in lighthouses:
        lh_type = lh.get('type', 'unknown')
        sector = lh.get('sector', 'unknown')
        index['by_type'][lh_type] = index['by_type'].get(lh_type, 0) + 1
        index['by_sector'][sector] = index['by_sector'].get(sector, 0) + 1
    
    # Write index file
    output_path = script_dir.parent / '_data' / 'lighthouse_index.json'
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"Generated lighthouse index with {len(lighthouses)} lighthouses")
    print(f"Output: {output_path}")
    print(f"By type: {index['by_type']}")
    print(f"By sector: {index['by_sector']}")

if __name__ == '__main__':
    main()
