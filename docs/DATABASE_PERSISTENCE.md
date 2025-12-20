# Database Persistence Configuration

## Problem

The user database (`users.db`) is stored at `/app/data/users.db` inside the container. Without a volume mount, this data is **lost every time the container is rebuilt**, causing all users to be logged out.

## Solution

Mount a persistent volume for `/app/data` so the database survives container rebuilds.

## Current Database Location

- **Path inside container**: `/app/data/users.db`
- **Database type**: SQLite
- **Configuration**: `backend/auth/database.py`

## Dokploy Docker Deployment - Adding Volume Mount

Based on the [official Dokploy documentation](https://docs.dokploy.com/docs/core/volume-backups), here are the exact steps:

### Step-by-Step Instructions

1. **Open your backend application in Dokploy**
   - Go to your Dokploy dashboard
   - Click on your backend service (e.g., `lawscout-backend`)

2. **Navigate to Advanced → Mounts**
   - Click on the **"Advanced"** tab or section
   - Look for **"Mounts"** section
   - This is where you configure volume mounts for Applications

3. **Create a New Volume Mount**
   - Click **"Add Mount"** or **"Create Mount"** button
   - Select **"Volume Mount"** option (NOT bind mount)
   - Configure the mount:
     - **Container Path**: `/app/data`
     - **Volume Name**: Dokploy will auto-generate this, or you can specify a name like `backend_data`
   - **Important**: Must be a **Volume Mount** (named volume), not a bind mount, for backups to work

4. **Save and Redeploy**
   - Click **"Save"** or **"Apply"**
   - **Redeploy** the application (volume mounts only apply on new containers)

### Why Volume Mount (Not Bind Mount)?

According to Dokploy docs:
- **Volume Mounts** (named volumes): Can be backed up, managed by Docker, persist across rebuilds
- **Bind Mounts** (like `../files`): Cannot be backed up using Volume Backups feature

For your SQLite database, you need a **Volume Mount** so:
1. Data persists across container rebuilds ✅
2. You can optionally set up automated backups ✅

## Verification

After configuring the volume:

1. **Check volume exists**:
   ```bash
   docker volume ls | grep backend_data
   ```

2. **Check database file**:
   ```bash
   docker exec <backend-container> ls -la /app/data/
   # Should show: users.db
   ```

3. **Test persistence**:
   - Create a test user account
   - Rebuild the backend container
   - Verify the user still exists after rebuild

## Backup Recommendations

Since we're using SQLite, consider:

1. **Regular backups**: Copy `/app/data/users.db` to a backup location
2. **Before major updates**: Always backup the database
3. **Automated backups**: Set up a cron job to backup daily

Example backup script:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/lawscout"
mkdir -p $BACKUP_DIR
docker cp <backend-container>:/app/data/users.db $BACKUP_DIR/users_$(date +%Y%m%d_%H%M%S).db
```

## Migration to PostgreSQL (Future)

For production scale, consider migrating to PostgreSQL:
- Better concurrency
- Better backup/restore
- Better performance at scale
- Native support in Dokploy

## Verification Steps

After adding the volume mount and redeploying:

1. **Check volume exists** (SSH into VPS):
   ```bash
   docker volume ls | grep backend
   # or check for your app name pattern
   docker volume ls
   ```

2. **Check database file exists** (inside container):
   ```bash
   # Get container name
   docker ps | grep backend
   
   # Check database file
   docker exec <container-name> ls -la /app/data/
   # Should show: users.db
   ```

3. **Test persistence**:
   - Create a test user account via the frontend
   - Note the user's email
   - Rebuild/redeploy the backend in Dokploy
   - Try to log in with the same user - it should still exist!

## Optional: Set Up Automated Backups

Once you have the volume mount configured, you can optionally set up automated backups:

1. **Navigate to Volume Backups** section in Dokploy
2. **Create a new volume backup**:
   - **Name**: `backend-database-backup`
   - **Schedule**: `0 0 * * *` (daily at midnight, cron format)
   - **Destination**: Your S3 destination (must be configured first)
   - **Service Name**: Your backend service name
   - **Volume Name**: The volume name created above
   - **Turn off Container**: Recommended (safer, prevents corruption)
   - **Enabled**: ✓

This will automatically backup your SQLite database daily to S3, protecting against data loss.

**Reference**: [Dokploy Volume Backups Documentation](https://docs.dokploy.com/docs/core/volume-backups)

## Current Status

⚠️ **Action Required**: Add volume mount in Dokploy UI
- Container Path: `/app/data`
- Volume Type: Named Volume (Docker managed)
- Then redeploy the backend service

