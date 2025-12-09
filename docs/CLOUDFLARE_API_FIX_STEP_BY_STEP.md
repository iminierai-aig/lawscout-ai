# Cloudflare Fix: Step-by-Step Instructions

## Problem
- ✅ `https://lawscout-frontend-latest.onrender.com` - **WORKS**
- ❌ `https://lawscoutai.com` - **FAILS** (Network error)

**Confirmed:** Backend and CORS work correctly. Cloudflare is blocking browser requests.

---

## Solution 1: Check Cloudflare Security Events (Start Here)

### Step 1: Log into Cloudflare
1. Go to https://dash.cloudflare.com
2. Log in with your account
3. Select your domain: **lawscoutai.com**

### Step 2: Navigate to Security Events
1. In the left sidebar, click **"Security"**
2. Click **"Events"** (or "Security Events")
3. You should see a list of security events

### Step 3: Look for Blocked Requests
1. Look for entries with:
   - **Action:** "Block" or "Challenge"
   - **Host:** `lawscoutai.com`
   - **Path:** Contains `/api/` or requests to `lawscout-backend-latest.onrender.com`
2. If you see blocked requests, note the **Rule ID** or **Reason**

### Step 4: Create WAF Exception (If Requests Are Blocked)

**If you found blocked requests:**

1. In the left sidebar, click **"Security"**
2. Click **"WAF"** (Web Application Firewall)
3. Click **"Custom rules"** tab (or "Firewall rules")
4. Click **"Create rule"** button
5. Fill in:
   - **Rule name:** `Allow API requests from lawscoutai.com`
   - **When incoming requests match:**
     - **Field:** `URI Path`
     - **Operator:** `contains`
     - **Value:** `/api/`
   - **AND**
     - **Field:** `Hostname`
     - **Operator:** `equals`
     - **Value:** `lawscoutai.com`
   - **Then:** Select **"Skip"** (or "Bypass")
6. Click **"Deploy"** or **"Save"**

---

## Solution 2: Adjust Security Level (If Solution 1 Doesn't Work)

### Step 1: Navigate to Security Settings
1. In Cloudflare dashboard, select **lawscoutai.com**
2. In the left sidebar, click **"Security"**
3. Click **"Settings"** (or look for "Security Level" section)

### Step 2: Find Security Level Setting
**Option A: If you see "Security Level" slider:**
1. You'll see a slider with options: **Off, Essentially Off, Low, Medium, High, I'm Under Attack!**
2. Change it to **"Medium"** or **"Low"** (to test)
3. Click **"Save"** if there's a save button

**Option B: If you see "Security" tab with different options:**
1. Look for a section called **"Security Level"**
2. It might be a dropdown menu instead of a slider
3. Select **"Medium"** from the dropdown
4. Save changes

**Option C: If you can't find it:**
- The Security Level might be under **"Overview"** → **"Quick Actions"**
- Or under **"Security"** → **"WAF"** → **"Managed rules"**

---

## Solution 3: Create Page Rule (Alternative Method)

### Step 1: Navigate to Page Rules
1. In Cloudflare dashboard, select **lawscoutai.com**
2. In the left sidebar, click **"Rules"**
3. Click **"Page Rules"** (or it might be under "Transform Rules")

### Step 2: Create New Page Rule
1. Click **"Create Page Rule"** button (usually at the top right)
2. In the **"URL"** field, enter: `*lawscoutai.com/api/*`
   - This matches any URL starting with `lawscoutai.com/api/`
3. Click **"Add a Setting"** button
4. Select **"Cache Level"** → Choose **"Bypass"**
5. Click **"Add a Setting"** again
6. Select **"Security Level"** → Choose **"Medium"** or **"Low"**
7. Click **"Save and Deploy"** (or just "Save")

**Note:** Free Cloudflare accounts have 3 Page Rules. Make sure you have one available.

---

## Solution 4: Check Browser Console for Exact Error

### Step 1: Open Browser Developer Tools
1. Go to `https://lawscoutai.com` in your browser
2. Press **F12** (or right-click → "Inspect")
3. Click the **"Console"** tab
4. Click the **"Network"** tab

### Step 2: Try a Search
1. Enter a search query and click "Search"
2. In the **Network** tab, look for the failed request:
   - It will be red (failed)
   - URL will be something like: `https://lawscout-backend-latest.onrender.com/api/v1/search`
3. Click on the failed request
4. Look at:
   - **Status Code:** (e.g., 403, 502, CORS error)
   - **Response Headers:** Look for `cf-ray` header (confirms Cloudflare is involved)
   - **Request Headers:** Check `Origin` header

### Step 3: Check Console Tab
1. Look for error messages in red
2. Common errors:
   - **CORS error:** "Access to fetch at ... has been blocked by CORS policy"
   - **403 Forbidden:** Cloudflare blocked the request
   - **Network Error:** Request never reached the server

**Take a screenshot of the error** - this will help identify the exact issue.

---

## Solution 5: Disable Specific Security Features (Temporary Test)

### Step 1: Navigate to Security Settings
1. In Cloudflare dashboard, select **lawscoutai.com**
2. Go to **"Security"** → **"Settings"**

### Step 2: Temporarily Disable Features
Try disabling these one at a time (to identify which one is blocking):

1. **Browser Integrity Check:**
   - Find "Browser Integrity Check" toggle
   - Turn it **OFF** temporarily
   - Save and test

2. **Challenge Passage:**
   - Find "Challenge Passage" setting
   - Set to a longer time (e.g., 30 minutes) or disable

3. **Always Use HTTPS:**
   - This shouldn't block, but check if it's set correctly

**After testing, re-enable features one by one** to find the culprit.

---

## Verification Steps

After applying any solution:

1. **Clear browser cache:**
   - Press `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
   - Select "Cached images and files"
   - Click "Clear data"

2. **Test the site:**
   - Go to `https://lawscoutai.com`
   - Open browser console (F12)
   - Try a search
   - Check if it works

3. **Check browser console:**
   - Look for: `🔍 Frontend API URL: https://lawscout-backend-latest.onrender.com`
   - No red errors
   - Network tab shows successful request (status 200)

---

## Still Not Working?

If none of the above work, please provide:

1. **Screenshot of Cloudflare Security Events** (showing blocked requests)
2. **Screenshot of browser console error** (F12 → Console tab)
3. **Screenshot of Network tab** (showing the failed request details)
4. **Your Cloudflare plan** (Free, Pro, Business, etc.)

This will help identify the exact issue.

---

## Quick Reference: Cloudflare Navigation

**Main sections:**
- **Overview:** Dashboard home
- **Analytics:** Traffic stats
- **Security:** Security settings, WAF, Events
- **Rules:** Page Rules, Transform Rules
- **Speed:** Caching, optimization
- **Caching:** Cache settings
- **Network:** Network settings

**Common locations:**
- Security Level: **Security** → **Settings** → **Security Level**
- WAF Rules: **Security** → **WAF** → **Custom rules**
- Page Rules: **Rules** → **Page Rules**
- Security Events: **Security** → **Events**

