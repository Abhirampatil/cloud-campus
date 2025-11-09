aws configurations

<!-- 1. Go to AWS Console: https://console.aws.amazon.com
2. Search "S3" in the top search bar → Click S3
3. Click "Create bucket" (orange button)

4. Bucket Settings:
   ┌─────────────────────────────────────────┐
   │ Bucket name: cloudcampus-notes-2025     │ (must be unique globally)
   │ AWS Region: US East (N. Virginia)       │ (us-east-1)
   └─────────────────────────────────────────┘

5. Object Ownership:
   ✓ ACLs disabled (recommended)

6. Block Public Access settings:
   ⚠️ UNCHECK "Block all public access"
   ✓ Check "I acknowledge that the current settings..."

7. Bucket Versioning:
   ○ Disable

8. Default encryption:
   ✓ Enable
   ○ Server-side encryption with Amazon S3 managed keys (SSE-S3)

9. Click "Create bucket" (bottom right)
```

✅ **Bucket created!** Note your bucket name.

---

### Step 3: Create IAM User (10 min)
```
1. Go to IAM: https://console.aws.amazon.com/iam
2. Left sidebar → Users → Click "Create user"

3. User details:
   ┌─────────────────────────────────────────┐
   │ User name: cloudcampus-s3-access        │
   └─────────────────────────────────────────┘
   
4. Click "Next"

5. Set permissions:
   ○ Attach policies directly (select this)
   
6. Search for: AmazonS3FullAccess
   ✓ Check the box next to "AmazonS3FullAccess"

7. Click "Next" → Click "Create user"

8. ⚠️ IMPORTANT: Create Access Keys
   - Click on the user you just created
   - Go to "Security credentials" tab
   - Scroll to "Access keys"
   - Click "Create access key"
   
9. Use case:
   ○ Application running outside AWS (select this)
   ✓ Check "I understand..."
   Click "Next"

10. Description (optional): CloudCampus App Access
    Click "Create access key"

11. ⚠️⚠️ CRITICAL - SAVE THESE NOW:
    ┌─────────────────────────────────────────────────────┐
    │ Access key ID: AKIAXXXXXXXXXXXXXXXX                 │
    │ Secret access key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx │
    └─────────────────────────────────────────────────────┘
    
    Click "Download .csv file" to be safe!
    
    ⚠️ You won't see the secret key again! -->