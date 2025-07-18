#!/usr/bin/env python3
"""
Analyze TrainerDay Onboarding Email Funnel
Calculates real read rates and drop-off between emails
"""

import json
import glob
from datetime import datetime

def load_latest_data():
    """Load the most recent email data files"""
    # Find the latest main emails file
    email_files = glob.glob("data/mautic_emails_*.json")
    if not email_files:
        print("No email data files found. Run mautic_email_fetcher.py first.")
        return None
    
    latest_file = sorted(email_files)[-1]
    with open(latest_file, 'r') as f:
        return json.load(f)

def calculate_metrics(emails):
    """Calculate read rates and funnel metrics"""
    # Onboarding sequence IDs and names
    onboarding = [
        {"id": "11", "name": "Welcome", "order": 1},
        {"id": "7", "name": "Quick Tour", "order": 2},
        {"id": "8", "name": "App Settings", "order": 3},
        {"id": "9", "name": "Checking In", "order": 4}
    ]
    
    print("\n=== TRAINERDAY ONBOARDING EMAIL FUNNEL ANALYSIS ===\n")
    
    metrics = []
    for email in onboarding:
        email_id = email["id"]
        if email_id in emails["emails"]:
            data = emails["emails"][email_id]
            sent = data.get("sentCount", 0)
            read = data.get("readCount", 0)
            read_rate = (read / sent * 100) if sent > 0 else 0
            
            metric = {
                "order": email["order"],
                "name": email["name"],
                "subject": data.get("subject", ""),
                "sent": sent,
                "read": read,
                "read_rate": read_rate
            }
            metrics.append(metric)
            
            print(f"Email {email['order']}: {email['name']}")
            print(f"Subject: {data.get('subject', '')}")
            print(f"Sent: {sent:,}")
            print(f"Read: {read:,}")
            print(f"Read Rate: {read_rate:.1f}%")
            print("-" * 60)
    
    # Calculate funnel drop-off
    print("\n=== FUNNEL DROP-OFF ANALYSIS ===\n")
    
    if len(metrics) > 0:
        initial_sent = metrics[0]["sent"]
        print(f"Starting Audience: {initial_sent:,} users\n")
        
        for i, metric in enumerate(metrics):
            retention_rate = (metric["sent"] / initial_sent * 100) if initial_sent > 0 else 0
            
            print(f"Step {i+1}: {metric['name']}")
            print(f"  Sent: {metric['sent']:,} ({retention_rate:.1f}% of initial)")
            print(f"  Read: {metric['read']:,} ({metric['read_rate']:.1f}% open rate)")
            
            if i > 0:
                drop_off = metrics[i-1]["sent"] - metric["sent"]
                drop_rate = (drop_off / metrics[i-1]["sent"] * 100) if metrics[i-1]["sent"] > 0 else 0
                print(f"  Drop-off from previous: {drop_off:,} users ({drop_rate:.1f}%)")
            print()
    
    # Calculate overall engagement
    print("\n=== OVERALL ENGAGEMENT METRICS ===\n")
    
    total_sent = sum(m["sent"] for m in metrics)
    total_read = sum(m["read"] for m in metrics)
    avg_read_rate = (total_read / total_sent * 100) if total_sent > 0 else 0
    
    print(f"Total Emails Sent: {total_sent:,}")
    print(f"Total Emails Read: {total_read:,}")
    print(f"Average Read Rate: {avg_read_rate:.1f}%")
    
    # Weighted average read rate
    weighted_sum = sum(m["sent"] * m["read_rate"] for m in metrics)
    weighted_avg = weighted_sum / total_sent if total_sent > 0 else 0
    print(f"Weighted Average Read Rate: {weighted_avg:.1f}%")
    
    # Save analysis
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    analysis = {
        "timestamp": timestamp,
        "funnel_metrics": metrics,
        "summary": {
            "total_sent": total_sent,
            "total_read": total_read,
            "average_read_rate": avg_read_rate,
            "weighted_average_read_rate": weighted_avg,
            "initial_audience": initial_sent if metrics else 0,
            "final_retention": metrics[-1]["sent"] / initial_sent * 100 if metrics and initial_sent > 0 else 0
        }
    }
    
    import os
    os.makedirs('data', exist_ok=True)
    
    with open(f"data/onboarding_analysis_{timestamp}.json", 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\nAnalysis saved to data/onboarding_analysis_{timestamp}.json")

def main():
    data = load_latest_data()
    if data:
        calculate_metrics(data)

if __name__ == "__main__":
    main()