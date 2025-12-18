# OAuth Setup Guide - Google Sign In

This guide explains how to set up Google OAuth for LawScout AI.

## Prerequisites

1. Google Cloud Platform account
2. Access to Google Cloud Console
3. Backend and frontend deployed

## Step 1: Create Google OAuth Credentials

### 1.1 Go to Google Cloud Console

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Select or create a project
3. Enable the **Google+ API** (or **Google Identity Services**)

### 1.2 Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - **User Type:** External (for public use)
   - **App name:** LawScout AI
   - **User support email:** Your email
   - **Developer contact:** Your email
   - **Scopes:** email, profile, openid
   - **Test users:** Add your email for testing

4. Create OAuth Client ID:
   - **Application type:** Web application
   - **Name:** LawScout AI Web Client
   - **Authorized JavaScript origins:**
     - `https://lawscoutai.com`
     - `https://www.lawscoutai.com`
     - `http://localhost:3000` (for local development)
   - **Authorized redirect URIs:**
     - `https://api.lawscoutai.com/api/auth/google/callback`
     - `http://localhost:8000/api/auth/google/callback` (for local development)

5. Click **Create**
6. Copy the **Client ID** and **Client Secret**

## Step 2: Configure Backend Environment Variables

In Dokploy → Backend Service → Environment, add:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=https://api.lawscoutai.com/api/auth/google/callback

# Frontend URL (for OAuth callback redirect)
FRONTEND_URL=https://lawscoutai.com

# Session secret (can use same as JWT_SECRET_KEY)
SESSION_SECRET=your_session_secret_here
```

## Step 3: Database Migration

The User model has been updated to support OAuth. If you have existing users, the new fields will be `NULL` for them (which is fine).

For new deployments, the database will automatically include the new fields.

For existing deployments, you may need to run a migration:

```python
# This is handled automatically by SQLAlchemy's create_all
# The new columns will be added when the app starts
```

## Step 4: Test OAuth Flow

1. **Start backend** (should see OAuth routes registered)
2. **Visit:** `https://api.lawscoutai.com/api/auth/google/login`
3. **Should redirect to Google** for authentication
4. **After Google auth**, should redirect back to frontend with token

## Step 5: Frontend Integration

The frontend needs to:
1. Add "Sign in with Google" button
2. Handle OAuth callback (`/auth/callback?token=...`)
3. Store token and update auth context

See frontend implementation in the next section.

## Security Considerations

✅ **CSRF Protection:** State parameter is used to prevent CSRF attacks
✅ **HTTPS Only:** OAuth redirects only work over HTTPS in production
✅ **Secure Storage:** OAuth secrets stored in environment variables
✅ **Token Validation:** JWT tokens are validated on every request

## Troubleshooting

### "OAuth not configured" error
- Check that `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set
- Restart backend after adding environment variables

### "Invalid redirect URI" error
- Verify redirect URI in Google Console matches exactly
- Check for trailing slashes or http vs https

### "State mismatch" error
- This is CSRF protection working
- Make sure session middleware is configured
- Check that `SESSION_SECRET` is set

### Redirect not working
- Verify `FRONTEND_URL` is set correctly
- Check CORS settings allow the frontend domain

## Next Steps

After Google OAuth is working, you can add:
- GitHub OAuth
- Microsoft OAuth
- Apple Sign In
- Account linking (link OAuth to existing email/password accounts)

