# Forum Scraper & Categorization System

An automated system that scrapes cycling-related forum posts from Reddit and TrainerRoad, categorizes them using OpenAI, and sends Telegram notifications for performance-related content.

## Features

- 🔄 **Automated Scraping**: Fetches posts from r/cycling, r/Velo, and TrainerRoad forum every 15 minutes
- 🤖 **AI Categorization**: Uses OpenAI GPT-3.5-turbo to categorize posts into 4 categories:
  - **Performance**: Training, FTP, power, climbing, speed, coaching
  - **Indoor Cycling**: Trainers, Zwift, indoor setups, trainer accessories
  - **TrainerRoad**: Posts from TrainerRoad forum (auto-categorized)
  - **Other**: Everything else with AI-generated descriptions (e.g., "Other: Bike maintenance")
- 📱 **Telegram Notifications**: Sends notifications for new Performance and Indoor Cycling posts
- 🌐 **Web Interface**: View and filter posts by category with interactive UI
- 💰 **Cost Optimized**: Only sends truly new posts to OpenAI (major cost savings)

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Reddit API    │    │   TrainerRoad    │    │   PostgreSQL    │
│   (r/cycling,   │────│      Forum       │────│    Database     │
│    r/Velo)      │    │     (Discourse)  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                       │
         └────────────────────────┼───────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     Forum Scraper        │
                    │    (Node.js/Express)     │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     OpenAI Categorizer   │
                    │    (GPT-3.5-turbo)       │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │   Telegram Notifier      │
                    │    (Bot API)             │
                    └──────────────────────────┘
```

## Database Schema

### forum-posts table
- `id`: Unique post identifier
- `title`: Post title
- `author`: Post author
- `created_utc`: Post creation timestamp
- `score`: Post score/upvotes
- `num_comments`: Number of comments
- `url`: Original post URL
- `selftext`: Post content
- `subreddit`: Source (cycling, Velo, trainerroad)
- `category`: AI-generated category
- `notified`: Whether notifications were sent
- `responded`: Manual tracking for responses

## Installation & Setup

### Prerequisites
- Node.js 18+
- PostgreSQL database
- OpenAI API key
- Telegram bot token

### Environment Variables
Create a `.env` file:

```env
# Database Configuration
DB_HOST=your_postgres_host
DB_PORT=25060
DB_DATABASE=your_database
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_SSL_CERT=-----BEGIN CERTIFICATE-----
...certificate content...
-----END CERTIFICATE-----

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-openai-key-here

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### Installation
```bash
npm install
npm start
```

### Telegram Bot Setup
1. Create a bot with @BotFather on Telegram
2. Get your bot token
3. Add bot to your group or get your chat ID
4. Follow `TELEGRAM-SETUP.md` for detailed instructions

## Usage

### Web Interface
- **Main view**: `https://your-domain.com/reddit`
- **Filtered views**: 
  - `https://your-domain.com/forums/Performance`
  - `https://your-domain.com/forums/Indoor%20Cycling`
  - `https://your-domain.com/forums/TrainerRoad`

### Manual Operations
```bash
# Force refresh posts
curl -X GET https://your-domain.com/reddit/refresh

# Trigger scraping via API
curl -X POST https://your-domain.com/api/scrape

# View logs
curl -X GET https://your-domain.com/logs
```

## Automated Workflow

### Every 15 minutes:
1. **Fetch Posts**: Scrape latest posts from all sources
2. **Detect New Posts**: Save to database, identify truly new posts
3. **AI Categorization**: Send only new posts to OpenAI for categorization
4. **Update Database**: Store categories for new posts
5. **Send Notifications**: Telegram alerts for Performance/Indoor posts
6. **Mark as Notified**: Prevent duplicate notifications

### Smart Comment Processing:
- **Hot Posts** (15+ comments, 15-60 min old): Priority comment fetching
- **Regular Posts** (1+ hours old): Standard comment fetching
- **Rate Limiting**: 500ms delays between requests

## Testing

### Test Scripts (in `script-testing/`)
- `test_openai_categorization.js`: Test AI categorization
- `test_telegram.js`: Test Telegram notifications
- `test_notification_logic.js`: Test duplicate prevention
- `test_optimized_flow.js`: Test cost optimization
- `categorize_existing_posts.js`: Categorize existing posts

```bash
# Run tests
node script-testing/test_openai_categorization.js
node script-testing/test_telegram.js
```

## Cost Optimization

The system is designed to minimize OpenAI API costs:

- ✅ **Only new posts** are sent to OpenAI
- ✅ **Existing posts** are skipped (no API calls)
- ✅ **Batch processing** with rate limiting
- ✅ **Smart caching** prevents duplicate categorization

**Typical savings**: 80-90% reduction in API costs compared to categorizing all posts every run.

## Deployment

### Dokku Deployment
```bash
# Deploy to UAT
git subtree push --prefix=forum-scraper forum-scraper master

# Check deployment
curl https://forum-scraper.uat.trainerday.com/reddit
```

### Environment Setup
The system automatically:
- Initializes PostgreSQL tables
- Adds missing columns (category, notified)
- Creates indexes for performance
- Handles SSL certificates

## Troubleshooting

### Common Issues

**1. Database Connection Issues**
- Check SSL certificate in environment variables
- Verify database credentials
- Ensure PostgreSQL is accessible

**2. OpenAI API Issues**
- Verify API key is correct and has credits
- Check for rate limiting (system has built-in delays)
- Monitor OpenAI usage dashboard

**3. Telegram Issues**
- Ensure bot token is correct
- Verify chat ID (use getUpdates to find)
- Check bot permissions in groups

**4. No New Posts Detected**
- Check if posts are being fetched successfully
- Verify database uniqueness constraints
- Check logs for scraping errors

### Logs
- **Application logs**: Check console output
- **Request logs**: Visit `/logs` endpoint
- **Database logs**: Check PostgreSQL logs

## API Endpoints

- `GET /reddit` - Main forum view
- `GET /forums/:category` - Filtered category view
- `POST /api/scrape` - Trigger manual scrape
- `GET /reddit/refresh` - Force refresh posts
- `GET /logs` - View request logs
- `POST /api/update-response-status` - Update response tracking

## Contributing

1. All test files go in `script-testing/` folder
2. Follow existing code patterns
3. Test thoroughly before deployment
4. Update documentation for new features

## License

Internal TrainerDay project - not for public distribution.