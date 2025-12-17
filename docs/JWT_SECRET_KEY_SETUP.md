# JWT Secret Key Setup

## ✅ Current Status

A secure JWT_SECRET_KEY has been generated and added to your local `.env` file.

**Generated Key:** `e3e2a1556a4d4384c4d226f69e9475f6591f9f309597ad97f4f40fd8197441a0`

## 📍 Where It's Used

- **Code Location:** `backend/auth/security.py` (line 15)
- **Environment Variable:** `JWT_SECRET_KEY`
- **Purpose:** Signing and verifying JWT tokens for authentication

## 🔐 Local Development

The key is already set in your `.env` file. When you run the backend locally, it will automatically use this key.

**Verify it's loaded:**
```bash
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('JWT_SECRET_KEY'))"
```

## ☁️ Production Setup (Render.com)

### Step 1: Get Your Generated Key
The key has been saved to your `.env` file. You can retrieve it with:
```bash
grep JWT_SECRET_KEY .env
```

### Step 2: Add to Render Dashboard
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your backend service (`lawscout-backend-latest`)
3. Click on **Environment** in the left sidebar
4. Click **Add Environment Variable**
5. Add:
   - **Key:** `JWT_SECRET_KEY`
   - **Value:** `e3e2a1556a4d4384c4d226f69e9475f6591f9f309597ad97f4f40fd8197441a0`
6. Click **Save Changes**
7. **Redeploy** your service (Render will auto-redeploy when you save)

### Step 3: Verify in Production
After deployment, test the auth endpoint:
```bash
curl https://lawscout-backend-latest.onrender.com/api/auth/health
```

## 🔄 Generate a New Key (if needed)

If you need to generate a new key:
```bash
openssl rand -hex 32
```

Then update:
1. Your local `.env` file
2. Render dashboard environment variables
3. Any other deployment environments

## ⚠️ Security Notes

- ✅ **Never commit** `.env` to git (already in `.gitignore`)
- ✅ **Use different keys** for dev/staging/production
- ✅ **Rotate keys** if they're ever exposed
- ✅ **Keep keys secret** - don't share in chat, emails, or logs
- ✅ **Minimum 32 bytes** (64 hex characters) - ✅ Your key is 64 characters

## 🧪 Testing

Test that the key is working:
```bash
# Start backend with the key
docker run -e JWT_SECRET_KEY="$(grep JWT_SECRET_KEY .env | cut -d'=' -f2)" ...

# Test registration (should work now)
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test123!", "full_name": "Test User"}'
```

## 📝 Current Configuration

- **Key Length:** 64 hex characters (32 bytes) ✅
- **Algorithm:** HS256
- **Token Expiry:** 7 days
- **Location:** `.env` file (local) + Render dashboard (production)

---

**Last Updated:** December 2024  
**Status:** ✅ Configured and ready to use

