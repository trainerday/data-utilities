#!/usr/bin/env python3
"""
Fix remaining link issues in TD-Business project
Focus on links that weren't fixed in the first pass
"""

import os
import re
from pathlib import Path
import json

def build_comprehensive_file_map(root_dir):
    """Build a comprehensive map of all files and their correct permalinks"""
    root_path = Path(root_dir)
    file_map = {}
    
    # Build map of ALL files
    for md_file in root_path.rglob('*.md'):
        relative_path = md_file.relative_to(root_path)
        permalink = str(relative_path.with_suffix(''))
        permalink = permalink.replace('\\', '/')
        
        # Add multiple possible references
        # 1. Just the filename without extension
        file_map[md_file.stem] = permalink
        
        # 2. Filename with extension
        file_map[md_file.name] = permalink
        
        # 3. Full relative path
        file_map[str(relative_path)] = permalink
        
        # 4. Relative path without extension
        file_map[permalink] = permalink
        
        # 5. Special handling for files with spaces
        if ' ' in permalink:
            # Also map the slugified version
            slugified = permalink.replace(' ', '-').lower()
            file_map[slugified] = permalink
        
        # 6. Handle common broken patterns
        if permalink.startswith('company-structure/roles/agents/'):
            # Map the agent name patterns
            agent_name = md_file.stem
            if ' - ' in agent_name:
                parts = agent_name.split(' - ')
                file_map[parts[0].lower() + '-' + parts[1].lower()] = permalink
                file_map['agents/' + parts[0].lower() + '-' + parts[1].lower()] = permalink
    
    # Add specific mappings for known issues
    specific_mappings = {
        # Role mappings
        'strategy-decision-maker': 'company-structure/roles/strategy-decision-maker',
        'strategy-vision-creator': 'company-structure/roles/strategy-vision-creator',
        'strategy-analyst': 'company-structure/roles/strategy-analyst',
        'strategy-finance': 'company-structure/roles/strategy-finance',
        'product-manager': 'company-structure/roles/product-manager',
        'product-developer': 'company-structure/roles/product-developer',
        'product-ux-ui-designer': 'company-structure/roles/product-ux-ui-designer',
        'product-tester': 'company-structure/roles/product-tester',
        'marketing-director': 'company-structure/roles/marketing-director',
        'marketing-content-creator': 'company-structure/roles/marketing-content-creator',
        'marketing-brand-strategist': 'company-structure/roles/marketing-brand-strategist',
        'marketing-seo-growth-specialist': 'company-structure/roles/marketing-seo-growth-specialist',
        'customer-support-agent': 'company-structure/roles/customer-support-agent',
        'customer-community-manager': 'company-structure/roles/customer-community-manager',
        'customer-retention-specialist': 'company-structure/roles/customer-retention-specialist',
        'customer-onboarding-expert': 'company-structure/roles/customer-onboarding-expert',
        
        # Agent mappings
        'zenith-decision-maker': 'company-structure/roles/agents/Zenith - Decision Maker',
        'prism-strategic-vision-creator': 'company-structure/roles/agents/Prism - Strategic Vision Creator',
        'cipher-analyst': 'company-structure/roles/agents/Cipher - Analyst',
        'ledger-finance': 'company-structure/roles/agents/ledger-finance',
        'nexus-product-manager': 'company-structure/roles/agents/Nexus - Product Manager',
        'flux-developer': 'company-structure/roles/agents/Flux - Developer',
        'muse-ux-ui-designer': 'company-structure/roles/agents/Muse - UX UI Designer',
        'hawk-tester': 'company-structure/roles/agents/Hawk - Tester',
        'spark-marketing-director': 'company-structure/roles/agents/Spark - Marketing Director',
        'echo-content-creator': 'company-structure/roles/agents/Echo - Content Creator',
        'mosaic-brand-strategist': 'company-structure/roles/agents/Mosaic - Brand Strategist',
        'tide-seo-growth-specialist': 'company-structure/roles/agents/Tide - SEO Growth Specialist',
        'haven-support-agent': 'company-structure/roles/agents/Haven - Support Agent',
        'ripple-community-manager': 'company-structure/roles/agents/Ripple - Community Manager',
        'compass-retention-specialist': 'company-structure/roles/agents/Compass - Retention Specialist',
        'bridge-onboarding-expert': 'company-structure/roles/agents/Bridge - Onboarding Expert',
        
        # Other common patterns
        'core-user-segmentation-discovery': 'research-findings/Core User Segmentation Discovery',
        'user-strategy-framework': 'marketing/User Strategy Framework',
        'company-overview': 'company-structure/company-overview',
        'conversion-step-2-onboarding-drip-campaign-optimization': 'priority-board-tasks/Conversion Step 2 - Onboarding Drip Campaign Optimization',
        'generate-ideas-improve-retention': 'priority-board-tasks/generate-ideas-improve-retention',
    }
    
    file_map.update(specific_mappings)
    
    return file_map

def fix_link_comprehensive(url, file_map, current_file_path, root_path):
    """More comprehensive link fixing"""
    # Skip external links
    if url.startswith(('http://', 'https://', '#', 'mailto:')):
        return url, False
    
    # Handle image links with spaces
    if ' ' in url and url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
        return url.replace(' ', '%20'), True
    
    # Clean up the URL
    clean_url = url.strip()
    if clean_url.endswith('.md'):
        clean_url = clean_url[:-3]
    
    # Direct match
    if clean_url in file_map:
        return file_map[clean_url], True
    
    # Try with company-structure prefix removed
    if clean_url.startswith('company-structure/'):
        without_prefix = clean_url[18:]  # Remove 'company-structure/'
        if without_prefix in file_map:
            return file_map[without_prefix], True
    
    # Try adding company-structure prefix
    with_prefix = 'company-structure/' + clean_url
    if with_prefix in file_map:
        return file_map[with_prefix], True
    
    # Handle special cases
    # Links ending with / (directory links)
    if clean_url.endswith('/'):
        # These are probably index/readme links
        return clean_url.rstrip('/'), True
    
    # Try to find by partial match
    parts = clean_url.split('/')
    if parts:
        filename = parts[-1]
        # Try exact filename match
        if filename in file_map:
            return file_map[filename], True
        
        # Try slugified version
        slugified = filename.replace(' ', '-').lower()
        if slugified in file_map:
            return file_map[slugified], True
    
    # If still not found, check if it's a broken path pattern
    if 'company-structure/priority-board-tasks/' in clean_url:
        # Extract the task name
        task_name = clean_url.split('/')[-1]
        if task_name in file_map:
            return file_map[task_name], True
        
        # Try in priority-board-tasks directly
        direct_path = 'priority-board-tasks/' + task_name
        if direct_path in file_map:
            return file_map[direct_path], True
    
    # For role/agent patterns
    if '/roles/' in clean_url:
        role_parts = clean_url.split('/')
        if role_parts:
            role_name = role_parts[-1]
            if role_name in file_map:
                return file_map[role_name], True
    
    # Can't fix - return original
    return url, False

def fix_all_remaining_links(root_dir, dry_run=True):
    """Fix all remaining link issues"""
    root_path = Path(root_dir)
    if not root_path.exists():
        print(f"Error: Directory {root_dir} does not exist!")
        return
    
    print(f"{'DRY RUN: ' if dry_run else ''}Building comprehensive file map...")
    file_map = build_comprehensive_file_map(root_dir)
    print(f"Built map with {len(file_map)} entries")
    
    all_fixes = []
    files_fixed = []
    
    print(f"\n{'DRY RUN: ' if dry_run else ''}Fixing remaining links...")
    print("-" * 80)
    
    for md_file in root_path.rglob('*.md'):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            content = original_content
            fixes = []
            
            # Pattern for markdown links
            md_link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
            
            def replace_link(match):
                text = match.group(1)
                url = match.group(2)
                
                fixed_url, was_fixed = fix_link_comprehensive(url, file_map, md_file, root_path)
                
                if was_fixed and fixed_url != url:
                    fixes.append({
                        'original': url,
                        'fixed': fixed_url,
                        'text': text
                    })
                    return f'[{text}]({fixed_url})'
                
                return match.group(0)
            
            # Fix markdown links
            content = md_link_pattern.sub(replace_link, content)
            
            # Pattern for wikilinks
            wiki_pattern = re.compile(r'\[\[([^\]]+)\]\]')
            
            def replace_wikilink(match):
                url = match.group(1)
                
                fixed_url, was_fixed = fix_link_comprehensive(url, file_map, md_file, root_path)
                
                if was_fixed and fixed_url != url:
                    fixes.append({
                        'original': url,
                        'fixed': fixed_url,
                        'type': 'wikilink'
                    })
                    return f'[[{fixed_url}]]'
                
                return match.group(0)
            
            # Fix wikilinks
            content = wiki_pattern.sub(replace_wikilink, content)
            
            # Save if changed
            if content != original_content:
                relative_path = str(md_file.relative_to(root_path))
                files_fixed.append(relative_path)
                all_fixes.extend([{**fix, 'file': relative_path} for fix in fixes])
                
                if not dry_run:
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                if fixes:
                    print(f"\n{'Would fix' if dry_run else 'Fixed'} {len(fixes)} links in: {relative_path}")
                    for fix in fixes[:3]:
                        print(f"  {fix['original']} → {fix['fixed']}")
                    if len(fixes) > 3:
                        print(f"  ... and {len(fixes) - 3} more")
        
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    return all_fixes, files_fixed

def main():
    project_root = "/Users/alex/Documents/bm-projects/TD-Business"
    
    print("TD-Business Remaining Link Fix Tool")
    print("=" * 80)
    
    # First do a dry run
    fixes, files = fix_all_remaining_links(project_root, dry_run=True)
    
    print("\n" + "=" * 80)
    print("SUMMARY (Dry Run):")
    print(f"Files with links to fix: {len(files)}")
    print(f"Total links to fix: {len(fixes)}")
    
    if fixes:
        print("\n" + "=" * 80)
        response = input("Do you want to apply these fixes? (yes/no): ")
        
        if response.lower() == 'yes':
            print("\nApplying fixes...")
            print("-" * 80)
            fixes, files = fix_all_remaining_links(project_root, dry_run=False)
            
            # Save summary
            summary = {
                'fixed_files': files,
                'total_fixes': len(fixes),
                'fixes': fixes
            }
            
            with open('td_business_remaining_link_fixes.json', 'w') as f:
                json.dump(summary, f, indent=2)
            
            print("\n✅ All remaining links have been fixed!")
            print(f"📄 Fix summary saved to: td_business_remaining_link_fixes.json")
        else:
            print("\n❌ No changes made.")
    else:
        print("\n✅ No more links to fix!")

if __name__ == "__main__":
    main()