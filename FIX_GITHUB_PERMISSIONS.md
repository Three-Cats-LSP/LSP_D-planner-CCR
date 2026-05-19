# Fix GitHub Actions Permissions for APK Auto-Push

The GitHub Actions workflow needs write permission to push the APK to your repository.

## ✅ Solution: Enable Workflow Permissions

### **Step 1: Go to Repository Settings**
1. Go to your GitHub repository: `https://github.com/Three-Cats-LSP/LSP_D-planner`
2. Click **Settings** tab

### **Step 2: Configure Workflow Permissions**
1. In the left sidebar, scroll down and click **Actions** → **General**
2. Look for section: **"Workflow permissions"**
3. Select: **"Read and write permissions"** (not "Read repository contents permission")
4. Check: ✅ **"Allow GitHub Actions to create and approve pull requests"**
5. Click **Save**

### **Step 3: Verify GITHUB_TOKEN Usage**
Make sure your workflow uses:
```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

And in git commands:
```bash
git remote add origin https://x-access-token:$GITHUB_TOKEN@github.com/${{ github.repository }}.git
git push origin HEAD:main
```

---

## 🔍 Check Repository Settings Path

**Settings → Actions → General → Workflow permissions**

Should show:
- ✅ **Read and write permissions**
- ✅ **Allow GitHub Actions to create and approve pull requests**

---

## 🚀 After Enabling Permissions

1. **Commit and push this workflow** to GitHub
2. **Trigger workflow** (push to main or manual trigger)
3. **APK will build and commit** to your repository ✅

---

## 📋 Troubleshooting

### If still getting 403 error:
1. Check you're logged into correct GitHub account
2. Verify repository settings are saved
3. Try manually triggering workflow after saving settings
4. Check Actions log for exact error message

### If workflow doesn't start:
1. Verify `.github/workflows/build-apk.yml` exists
2. Check workflow file syntax (YAML formatting)
3. Commit and push the workflow file to main branch

---

## 🎯 Expected Result

After fixing permissions and running workflow:

```
GitHub Actions runs:
1. Builds APK ✅
2. Creates APK/ folder ✅
3. Commits APK to repo ✅
4. Pushes to main ✅

Result in main branch:
APK/
└── dive-planner-YYYYMMDD-HHMMSS.apk
```

---

**After following these steps, your APK will auto-commit!** 🎉
