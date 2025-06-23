# 🚀 Quick Reference Card - CI/CD Commands

## 📋 Essential Commands

### Local Testing
```powershell
# Test everything locally
python verify-setup.py

# Manual Docker test
docker-compose up -d
Invoke-RestMethod -Uri "http://localhost:8000/health"
docker-compose down
```

### Git Operations
```powershell
# Regular development
git add .
git commit -m "feat: Your feature description"
git push origin main

# Create new release
git tag v0.2.0
git push origin v0.2.0
```

### GitHub Setup (One-time)
```powershell
# Your repository is already set up!
git remote -v  # Shows: sohailshk/Backend_Identity_Reconciliation
git branch -M main
git push -u origin main
git push origin v0.1.0
```

## 🔧 Repository URLs to Update

### In README.md
Replace these placeholders:
- `YOUR_USERNAME` → Your GitHub username
- `YOUR_REPO_NAME` → Your repository name
- `YOUR_DOCKER_USERNAME` → Your Docker Hub username

### GitHub Secrets to Add
- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub access token

## 📊 Monitoring URLs

### GitHub Actions
```
https://github.com/sohailshk/Backend_Identity_Reconciliation/actions
```

### Docker Hub Repository
```
https://hub.docker.com/r/sohailshk/contact-reconciliation-api
```

### API Documentation (Local)
```
http://localhost:8000/docs
http://localhost:8000/redoc
```

## 🔍 Troubleshooting Commands

```powershell
# Check git status
git status
git remote -v

# Check Docker
docker --version
docker-compose --version
docker ps

# View logs
docker-compose logs contact-api
git log --oneline

# Clean Docker
docker-compose down --volumes
docker system prune -f
```

## 🎯 Success Indicators

✅ **Local Test Passes**: `python verify-setup.py` shows all green checkmarks
✅ **GitHub Actions**: Green checkmark on commits in GitHub
✅ **Docker Hub**: New images appear after tagging
✅ **API Works**: `http://localhost:8000/health` returns 200 OK
✅ **Badges**: README badges show "passing" status

## 📞 Quick Help

**Issue**: GitHub Actions failing?
**Fix**: Check GitHub repository → Actions tab → Click failed run → Read logs

**Issue**: Docker push failing?
**Fix**: Regenerate Docker Hub token → Update GitHub secrets

**Issue**: Local tests failing?
**Fix**: Run `python verify-setup.py` → Follow error messages

**Issue**: Can't access API?
**Fix**: Check `docker-compose logs contact-api` → Verify port 8000 is free
