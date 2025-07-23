# Forum Data

This folder is reserved for any raw forum data files if needed, but the primary forum data source is the PostgreSQL `forum_analysis` table.

## Current Status

- **Primary Source**: PostgreSQL database `forum_analysis` table
- **Processing**: Via `unified_content_processor.py` forum extractor
- **Data Type**: Processed Q&A pairs from forum discussions

## Note

Raw forum data files are not currently stored here as all forum processing happens directly from the PostgreSQL database connection.