# TrainerDay Data Warehouse Analysis Session

**Date:** July 3, 2025  
**Analysis Period:** June 3 - July 3, 2025 (Last 30 days)

## Summary

Analysis of subscription data from PostgreSQL data warehouse and comparison with Telegram notification data for June 2025.

## Database Connection Details

- **Host:** postgress-dw-do-user-979029-0.b.db.ondigitalocean.com
- **Port:** 25060
- **Database:** defaultdb
- **Connection:** Successful with SSL certificate authentication

## Database Structure

### Events Table
- **Total Records:** Large dataset (2019-2025)
- **Date Range:** 2019-02-10 to 2025-07-03
- **Key Columns:**
  - `user_id` (integer, nullable)
  - `name` (character varying, nullable)
  - `value` (character varying, nullable)
  - `json_data` (json, nullable)
  - `created_at` (timestamp with time zone, nullable)

### Subscriptions Table
- **Date Range:** 2020-01-30 to 2022-09-14 (Historical data only)
- **Key Columns:**
  - `membership_id`, `user_id`, `level_id`, `level_name`
  - `created_date`, `expiration_date`, `status`
  - `gateway`, `customer_id`, `subscription_id`

## Subscription Analysis Results

### Database Events (June 3 - July 3, 2025)

#### Overall Subscription Events
- **Total subscription-related events:** 1,825
- **New subscriptions (status changed to active):** 368
- **Canceled subscriptions:** 341
- **Net new subscriptions:** 27

#### Subscription Event Types Found
- `billing: cancel subscription`
- `billing: reactivation of subscription`
- `billing: upgrade a subscription`
- `Subscribe Page Visited`
- `subscription status changed to active`
- `subscription status changed to canceled`
- `subscription status changed to cancelled`
- `subscription status changed to expired`
- `subscription status changed to pending`
- `subscription status changed to suspended`

#### Recent Activity Examples
```
2025-07-03 07:43:05: subscription status changed to canceled
2025-07-03 07:42:44: Subscribe Page Visited
2025-07-03 07:42:19: subscription status changed to canceled
2025-07-03 06:01:31: subscription status changed to active
2025-07-03 05:46:20: subscription status changed to active
2025-07-03 05:25:58: subscription status changed to active
```

### Telegram Notifications (June 2025)

#### Subscription Types and Counts
- **Premium:** 153
- **Premium App:** 142
- **Premium Yearly:** 45
- **Premium - 4 months:** 8
- **Metodo Pit:** 4
- **Premium Vasa SwimERG:** 1
- **Total:** 353

### Current Active Subscriptions (Snapshot)

From subscriptions table (historical baseline):
- **Premium:** 576
- **Premium Yearly:** 328
- **Premium App:** 231
- **The Green Plan:** 55
- **Yearly for Special Offers:** 37
- **Premium - 4 months:** 30
- **TotalCyclist:** 3
- **Monthly for Special Offers:** 1
- **Premium Vasa SwimERG:** 1

## Data Comparison & Analysis

### Key Findings

1. **Database vs Telegram Discrepancy:**
   - Database events: 368 new subscriptions
   - Telegram notifications: 353 new subscriptions
   - Difference: 15 subscriptions (4.2%)

2. **Date Range Differences:**
   - Database: 30-day rolling window (June 3 - July 3)
   - Telegram: Calendar month (June 1-30)
   - The 3-day difference likely accounts for the 15-subscription variance

3. **Data Granularity:**
   - **Database:** Tracks status changes but NOT subscription types
   - **Telegram:** Provides detailed subscription type breakdowns
   - **Subscriptions table:** Contains historical data only (up to 2022)

### Data Quality Issues

1. **Missing Subscription Type Data:**
   - Events table `json_data` only contains status transitions: `{'from': 'pending', 'to': 'active'}`
   - No subscription type information (Premium, Premium Yearly, etc.) in events
   - Billing events have empty json_data: `{}`

2. **Outdated Subscriptions Table:**
   - Last updated: September 14, 2022
   - No current subscription creation data
   - Historical baseline only

## Recommendations

1. **Data Source Priority:**
   - Use Telegram notifications for subscription type analysis
   - Use database events for overall subscription volume tracking

2. **Data Pipeline Improvements:**
   - Update subscriptions table with current data
   - Include subscription type information in events table
   - Enhance billing event data capture

3. **Reporting Strategy:**
   - Combine both sources for comprehensive analysis
   - Account for date range differences in comparisons
   - Monitor the ~4% variance as baseline difference

## Files Created

- `dbtest.py` - Database connection test script
- `subscription_analysis.py` - Detailed subscription event analysis
- `subscription_count.py` - Subscription counting with date range analysis
- `simple_subscription_count.py` - Simplified subscription counting
- `.env` - Database connection configuration
- `session_info.md` - This comprehensive analysis report

## SQL Queries Used

### New Subscriptions Count
```sql
SELECT COUNT(*) FROM events 
WHERE created_at >= '2025-06-03' 
AND name = 'subscription status changed to active';
```

### Subscription Events by Type
```sql
SELECT DISTINCT name FROM events 
WHERE (name ILIKE '%subscription%' OR name ILIKE '%subscribe%') 
ORDER BY name;
```

### Current Active Subscriptions
```sql
SELECT level_name, COUNT(*) as count
FROM subscriptions 
WHERE status = 'active'
GROUP BY level_name
ORDER BY count DESC;
```

---

*Analysis completed on July 3, 2025*