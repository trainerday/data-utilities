# Clicky API Python Client

A Python client for interacting with the Clicky Analytics API.

## Installation

```bash
pip install -r requirements.txt
```

Or install as a package:

```bash
pip install -e .
```

## Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Clicky credentials:
   ```
   CLICKY_SITE_ID=101125465
   CLICKY_SITEKEY=your_actual_sitekey_here
   ```

   You can find your sitekey in your Clicky account settings.

## Quick Start

```python
from clicky_api import ClickyAPIClient, Config

# Load configuration
config = Config()
client = ClickyAPIClient(config.site_id, config.sitekey)

# Get today's visitors
visitors = client.get_visitors()
print(visitors)

# Get top pages
pages = client.get_pages(limit=10)
for page in pages:
    print(f"{page['title']}: {page['value']} views")
```

## Examples

The `examples/` directory contains several usage examples:

- `basic_usage.py` - Basic API usage and data retrieval
- `weekly_report.py` - Generate weekly analytics reports with visualizations
- `real_time_monitor.py` - Real-time monitoring dashboard

Run an example:
```bash
cd examples
python basic_usage.py
```

## API Methods

### Basic Statistics

- `get_visitors()` - Get visitor statistics
- `get_actions()` - Get action statistics
- `get_pages()` - Get page statistics
- `get_referrers()` - Get referrer statistics
- `get_searches()` - Get search keyword statistics
- `get_countries()` - Get country statistics
- `get_browsers()` - Get browser statistics
- `get_operating_systems()` - Get OS statistics

### Advanced Usage

- `get_multiple_stats()` - Get multiple statistics in one request
- `get_custom_date_range()` - Get statistics for custom date ranges

### Date Ranges

Common date range values:
- `today`
- `yesterday`
- `last-7-days`
- `last-30-days`
- `this-month`
- `last-month`
- Custom range: `2024-01-01,2024-01-31`

## Output Formats

The client supports multiple output formats:
- `json` (default)
- `xml`
- `csv`
- `php`

## Error Handling

The client will raise exceptions for:
- Missing configuration (ValueError)
- HTTP errors (requests.exceptions.RequestException)
- Invalid API responses

## License

MIT License