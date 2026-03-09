# Environment Separation and Migration Mechanism

## Overview
This track implements a clear separation between **Production** and **Development** database environments. This prevents the development agent (Gemini) from accidentally modifying or deleting the user's live data.

## Configuration
- **Environment Variable**: `APP_ENV`
- **Options**: `production` (default), `development`, `test`

### Database Files
- **Production**: `gtd.db`
- **Development**: `gtd_dev.db`
- **Test**: `test_gtd.db`

## Usage for Agent
The agent MUST always run with `export APP_ENV=development` to ensure it only touches the development database.

## Migration to Production
When schema changes are verified in development, they can be safely applied to production using the migration script:

```bash
python scripts/migrate.py --confirm
```

**Note**: This script automatically creates a timestamped backup of the production database before applying any changes.
