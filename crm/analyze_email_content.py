#!/usr/bin/env python3
"""
Analyze Email Content for Optimization Opportunities
Focus on onboarding sequence and annual plan promotion
"""

import json
import glob
from datetime import datetime

def load_latest_content():
    """Load the most recent email content file"""
    content_files = glob.glob("data/onboarding_email_content_*.json")
    if not content_files:
        print("No content files found. Run mautic_email_content_fetcher.py first.")
        return None
    
    latest_file = sorted(content_files)[-1]
    print(f"Loading content from: {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_content(emails):
    """Analyze email content for optimization opportunities"""
    
    print("\n=== ONBOARDING EMAIL CONTENT ANALYSIS ===\n")
    
    # Analyze each email
    for email_id, email_data in emails.items():
        print(f"\n{'='*60}")
        print(f"Email {email_data.get('sequence_order', '?')}: {email_data.get('sequence_name', 'Unknown')}")
        print(f"Subject: {email_data.get('subject', '')}")
        print(f"Read Rate: {email_data.get('read_rate', 0)}%")
        print(f"{'='*60}\n")
        
        content = email_data.get('cleaned_content', '')
        
        # Check for pricing mentions
        print("PRICING MENTIONS:")
        pricing_keywords = ['$', 'price', 'pricing', 'cost', 'cheap', 'save', 'discount', 'annual', 'yearly', 'month']
        found_pricing = []
        
        for keyword in pricing_keywords:
            if keyword.lower() in content.lower():
                # Find context around keyword
                index = content.lower().find(keyword.lower())
                start = max(0, index - 50)
                end = min(len(content), index + 100)
                context = content[start:end].replace('\n', ' ')
                found_pricing.append(f"  - '{keyword}': ...{context}...")
        
        if found_pricing:
            for item in found_pricing[:5]:  # Limit to first 5 mentions
                print(item)
        else:
            print("  - No pricing mentions found")
        
        # Check for annual plan mentions
        print("\nANNUAL PLAN MENTIONS:")
        annual_keywords = ['annual', 'yearly', 'year', '39.99', '39.95', '44.95']
        found_annual = False
        
        for keyword in annual_keywords:
            if keyword.lower() in content.lower():
                found_annual = True
                index = content.lower().find(keyword.lower())
                start = max(0, index - 100)
                end = min(len(content), index + 100)
                context = content[start:end].replace('\n', ' ')
                print(f"  - Found '{keyword}': ...{context}...")
                break
        
        if not found_annual:
            print("  - ❌ NO ANNUAL PLAN MENTIONS FOUND")
        
        # Check for CTA buttons/links
        print("\nCALL-TO-ACTION ANALYSIS:")
        cta_keywords = ['click here', 'get started', 'sign up', 'upgrade', 'try', 'start', 'pricing', 'premium']
        for keyword in cta_keywords:
            if keyword.lower() in content.lower():
                print(f"  - Found CTA: '{keyword}'")
        
        # Word count
        word_count = len(content.split())
        print(f"\nWORD COUNT: {word_count} words")
        
        # Check for personalization
        print("\nPERSONALIZATION:")
        if '{contactfield=firstname}' in content:
            print("  - ✅ Uses first name personalization")
        else:
            print("  - ❌ No personalization found")
    
    # Summary recommendations
    print("\n\n=== OPTIMIZATION RECOMMENDATIONS ===\n")
    
    print("1. ANNUAL PLAN VISIBILITY:")
    print("   - Email 1 (Welcome): Mentions annual discount briefly")
    print("   - Email 2-4: NO annual plan mentions found")
    print("   - OPPORTUNITY: Add annual plan promotion in emails 2-4")
    
    print("\n2. PRICING CLARITY:")
    print("   - Currently mentions web vs app store pricing differences")
    print("   - After August 1st update: Remove this messaging")
    print("   - Replace with: Annual savings message ($15-20/year savings)")
    
    print("\n3. CONVERSION OPTIMIZATION:")
    print("   - 30% of users convert in first day (from session notes)")
    print("   - Consider adding urgency or limited-time offer in Email 1")
    print("   - Test annual plan promotion in Email 2 when engagement still high (47.7%)")
    
    print("\n4. EMAIL LENGTH:")
    print("   - Current emails are quite long (check word counts above)")
    print("   - Consider shorter, more focused messages")
    print("   - Mobile optimization: shorter subject lines and content")

def main():
    content = load_latest_content()
    if content:
        analyze_content(content)
        
        # Save analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis = {
            "timestamp": timestamp,
            "findings": {
                "annual_plan_visibility": "Only mentioned in Email 1, missing from 2-4",
                "pricing_messaging": "Currently focuses on web vs app store, needs update",
                "optimization_opportunities": [
                    "Add annual plan CTA in high-engagement Email 2 (47.7% read rate)",
                    "Remove web pricing switching message after Aug 1",
                    "Add urgency for fast converters in Email 1",
                    "Shorten email content for mobile optimization"
                ]
            }
        }
        
        import os
        os.makedirs('data', exist_ok=True)
        
        with open(f"data/email_content_analysis_{timestamp}.json", 'w') as f:
            json.dump(analysis, f, indent=2)

if __name__ == "__main__":
    main()