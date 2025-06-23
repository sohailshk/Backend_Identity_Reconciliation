# 🚀 Complete CI/CD Setup Guide - Step by Step

## Table of Contents
1. [Local Testing & Verification](#1-local-testing--verification)
2. [GitHub Repository Setup](#2-github-repository-setup)
3. [Docker Hub Setup](#3-docker-hub-setup)
4. [GitHub Secrets Configuration](#4-github-secrets-configuration)
5. [Update Documentation Badges](#5-update-documentation-badges)
6. [Push Code and Test Pipeline](#6-push-code-and-test-pipeline)
7. [Monitoring and Maintenance](#7-monitoring-and-maintenance)
8. [Troubleshooting Common Issues](#8-troubleshooting-common-issues)

---

## 1. Local Testing & Verification

### Step 1.1: Test Local Setup First
Before pushing to GitHub, let's make sure everything works locally.

```powershell
# Navigate to your project directory
cd "C:\Users\sohai\Downloads\Moonrider_Assignment"

# Install requests library for verification script
pip install requests

# Run the verification script
python verify-setup.py
```

**Expected Output:**
```
🔍 Contact Reconciliation Service - Setup Verification
============================================================
🔍 Checking requirements...
✅ Docker: Docker version 24.0.7, build afdd53b
✅ Docker Compose: Docker Compose version v2.23.3-desktop.2
🏗️ Testing Docker build...
✅ Docker build successful
🚀 Starting service...
✅ Service started
⏳ Waiting for service to be ready...
✅ Service is ready
🧪 Testing API endpoints...
✅ Health endpoint working
✅ Identify endpoint working
📚 Testing documentation...
✅ Swagger UI accessible
✅ ReDoc accessible
✅ OpenAPI JSON accessible
🧹 Cleaning up...
✅ Cleanup complete
🎉 All tests passed! Your setup is working correctly.
```

### Step 1.2: Manual Testing (Optional)
If you want to test manually:

```powershell
# Start the service
docker-compose up -d

# Wait for service to start (about 30-40 seconds)
# Check health
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET

# Test identify endpoint
$body = @{
    email = "test@example.com"
    phoneNumber = "1234567890"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/identify" -Method POST -Body $body -ContentType "application/json"

# Clean up
docker-compose down
```

---

## 2. GitHub Repository Setup

### Step 2.1: Create GitHub Repository

1. **Go to GitHub**: Navigate to https://github.com
2. **Sign in** to your GitHub account
3. **Create New Repository**:
   - Click the "+" icon in the top right corner
   - Select "New repository"
   - **Repository name**: `contact-reconciliation-service` (or your preferred name)
   - **Description**: `FastAPI backend service for contact reconciliation with advanced merging logic`
   - **Visibility**: Public (recommended for CI/CD)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
   - Click "Create repository"

### Step 2.2: Connect Local Repository to GitHub

```powershell
# Add GitHub remote (replace YOUR_USERNAME and YOUR_REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/contact-reconciliation-service.git

# Rename default branch to main
git branch -M main

# Push code to GitHub
git push -u origin main

# Push the version tag
git push origin v0.1.0
```

**Example with actual values:**
```powershell
# If your GitHub username is "johndoe"
git remote add origin https://github.com/johndoe/contact-reconciliation-service.git
git branch -M main
git push -u origin main
git push origin v0.1.0
```

### Step 2.3: Verify Repository Upload

1. Go to your GitHub repository URL
2. You should see all your files uploaded
3. Check that the tag appears under "Releases" or "Tags"

---

## 3. Docker Hub Setup

### Step 3.1: Create Docker Hub Account

1. **Go to Docker Hub**: Navigate to https://hub.docker.com
2. **Sign Up/Sign In**: Create account or sign in
3. **Verify Email**: Make sure to verify your email address

### Step 3.2: Create Repository

1. **Click "Create Repository"**
2. **Repository Details**:
   - **Name**: `contact-reconciliation-api`
   - **Description**: `FastAPI backend for contact reconciliation with Docker support`
   - **Visibility**: Public (free tier)
3. **Click "Create"**

### Step 3.3: Generate Access Token

1. **Go to Account Settings**:
   - Click your profile picture → "Account Settings"
   - Go to "Security" tab
   - Click "New Access Token"

2. **Create Token**:
   - **Access Token Description**: `GitHub Actions CI/CD`
   - **Permissions**: Select "Read, Write, Delete"
   - Click "Generate"
   - **⚠️ IMPORTANT**: Copy the token immediately and save it securely!

**Example token format**: `dckr_pat_1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p`

---

## 4. GitHub Secrets Configuration

### Step 4.1: Navigate to Repository Secrets

1. **Go to your GitHub repository**
2. **Click "Settings"** tab (top navigation)
3. **In left sidebar**: Click "Secrets and variables" → "Actions"

### Step 4.2: Add Docker Hub Secrets

**Add First Secret - DOCKER_USERNAME:**
1. Click "New repository secret"
2. **Name**: `DOCKER_USERNAME`
3. **Secret**: Your Docker Hub username (e.g., `johndoe`)
4. Click "Add secret"

**Add Second Secret - DOCKER_PASSWORD:**
1. Click "New repository secret"
2. **Name**: `DOCKER_PASSWORD`
3. **Secret**: The access token you generated (e.g., `dckr_pat_1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p`)
4. Click "Add secret"

### Step 4.3: Verify Secrets

You should now see two secrets listed:
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`

---

## 5. Update Documentation Badges

### Step 5.1: Update README.md

Replace the placeholder badges in your README.md file:

```powershell
# Open the README.md file in your preferred editor
code README.md  # If using VS Code
# Or
notepad README.md
```

**Find this section at the top:**
```markdown
[![CI/CD Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/actions/workflows/ci-cd.yml)
[![Docker Image](https://img.shields.io/docker/v/YOUR_DOCKER_USERNAME/contact-reconciliation-api?label=docker&logo=docker)](https://hub.docker.com/r/YOUR_DOCKER_USERNAME/contact-reconciliation-api)
```

**Replace with your actual values:**
```markdown
[![CI/CD Pipeline](https://github.com/johndoe/contact-reconciliation-service/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/johndoe/contact-reconciliation-service/actions/workflows/ci-cd.yml)
[![Docker Image](https://img.shields.io/docker/v/johndoe/contact-reconciliation-api?label=docker&logo=docker)](https://hub.docker.com/r/johndoe/contact-reconciliation-api)
```

### Step 5.2: Update CI/CD Documentation Section

**Find the CI/CD section and update these lines:**
```markdown
# Replace YOUR_USERNAME and YOUR_REPO_NAME with actual values
[![CI/CD Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/actions/workflows/ci-cd.yml/badge.svg)]

# Replace YOUR_DOCKER_USERNAME with your Docker Hub username
[![Docker Image](https://img.shields.io/docker/v/YOUR_DOCKER_USERNAME/contact-reconciliation-api?label=docker&logo=docker)]
```

**With your actual values:**
```markdown
# Replace johndoe/contact-reconciliation-service with your actual values
[![CI/CD Pipeline](https://github.com/johndoe/contact-reconciliation-service/actions/workflows/ci-cd.yml/badge.svg)]

# Replace johndoe with your Docker Hub username
[![Docker Image](https://img.shields.io/docker/v/johndoe/contact-reconciliation-api?label=docker&logo=docker)]
```

### Step 5.3: Update Deployment Section

**Find this section:**
```bash
# Pull the latest version
docker pull YOUR_DOCKER_USERNAME/contact-reconciliation-api:latest

# Or pull a specific version
docker pull YOUR_DOCKER_USERNAME/contact-reconciliation-api:v0.1.0

# Run the container
docker run -p 8000:8000 YOUR_DOCKER_USERNAME/contact-reconciliation-api:latest
```

**Replace with:**
```bash
# Pull the latest version
docker pull johndoe/contact-reconciliation-api:latest

# Or pull a specific version
docker pull johndoe/contact-reconciliation-api:v0.1.0

# Run the container
docker run -p 8000:8000 johndoe/contact-reconciliation-api:latest
```

---

## 6. Push Code and Test Pipeline

### Step 6.1: Commit Documentation Updates

```powershell
# Add the updated README
git add README.md

# Commit the changes
git commit -m "docs: Update badges and documentation with actual repository URLs"

# Push to trigger CI/CD testing
git push origin main
```

### Step 6.2: Monitor GitHub Actions

1. **Go to your GitHub repository**
2. **Click "Actions" tab**
3. **You should see a new workflow run** with the commit message "docs: Update badges..."
4. **Click on the workflow run** to see details
5. **Watch the `build-and-test` job** - it should:
   - ✅ Checkout code
   - ✅ Set up Python 3.11
   - ✅ Install dependencies
   - ✅ Run tests with coverage
   - ✅ Run linting

**Expected GitHub Actions Output:**
```
✅ Checkout code
✅ Set up Python 3.11
✅ Cache pip dependencies
✅ Install dependencies
✅ Run tests with coverage
✅ Lint with flake8
```

### Step 6.3: Test Docker Build Pipeline

Create a new version tag to trigger Docker build:

```powershell
# Create a new tag
git tag v0.1.1
git push origin v0.1.1
```

### Step 6.4: Monitor Docker Build

1. **Go to GitHub Actions** again
2. **You should see a new workflow** triggered by the tag
3. **This run should have TWO jobs**:
   - ✅ `build-and-test` (same as before)
   - ✅ `docker-build-and-push` (new - builds and pushes Docker image)

**Expected Docker Job Output:**
```
✅ Checkout code
✅ Set up Docker Buildx
✅ Log in to Docker Hub
✅ Extract version from tag
✅ Build and push Docker image
✅ Create GitHub Release
```

### Step 6.5: Verify Docker Hub

1. **Go to your Docker Hub repository**: https://hub.docker.com/r/YOUR_USERNAME/contact-reconciliation-api
2. **You should see**:
   - New image with tag `v0.1.1`
   - Image tagged as `latest`
   - Multi-platform support (linux/amd64, linux/arm64)

### Step 6.6: Verify GitHub Release

1. **Go to your GitHub repository**
2. **Click "Releases"** (right sidebar)
3. **You should see**: Release `v0.1.1` automatically created

---

## 7. Monitoring and Maintenance

### Step 7.1: Regular Development Workflow

**For regular development:**
```powershell
# Make changes to your code
# ... edit files ...

# Test locally first
python verify-setup.py

# Commit and push
git add .
git commit -m "feat: Add new feature"
git push origin main

# This triggers testing but NOT Docker build
```

**For releases:**
```powershell
# Update CHANGELOG.md with new version
# ... edit CHANGELOG.md ...

# Commit changes
git add CHANGELOG.md
git commit -m "docs: Update changelog for v0.2.0"

# Create and push new version tag
git tag v0.2.0
git push origin v0.2.0

# This triggers both testing AND Docker build/push
```

### Step 7.2: Monitoring Tools

**GitHub Actions Dashboard:**
- Monitor all workflow runs: https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/actions
- View detailed logs for debugging
- Check success/failure rates

**Docker Hub Dashboard:**
- Monitor image pulls: https://hub.docker.com/r/YOUR_USERNAME/contact-reconciliation-api
- View image sizes and scan results
- Check platform compatibility

### Step 7.3: Badge Status

Your README badges will automatically update:
- **CI/CD Badge**: Shows latest build status (passing/failing)
- **Docker Badge**: Shows latest version number
- **License Badge**: Static (unless you change license)

---

## 8. Troubleshooting Common Issues

### Issue 8.1: GitHub Actions Failing

**Problem**: Tests fail in GitHub Actions but pass locally

**Solution:**
```powershell
# Check Python version compatibility
# Ensure requirements.txt includes all dependencies
pip freeze > requirements.txt

# Test with exact GitHub Actions environment
docker run -it --rm python:3.11-slim bash
# Inside container:
# pip install -r requirements.txt
# python -m pytest tests/
```

### Issue 8.2: Docker Build Failing

**Problem**: Docker build fails in GitHub Actions

**Solution:**
```powershell
# Test Docker build locally first
docker build -t test-build .

# Check Dockerfile for platform-specific issues
# Update Dockerfile if needed
git add Dockerfile
git commit -m "fix: Update Dockerfile for multi-platform builds"
git push origin main
```

### Issue 8.3: Docker Push Authentication Failed

**Problem**: "authentication required" error

**Solution:**
1. **Regenerate Docker Hub token**:
   - Go to Docker Hub → Account Settings → Security
   - Delete old token, create new one
2. **Update GitHub secret**:
   - Go to GitHub repository → Settings → Secrets and variables → Actions
   - Update `DOCKER_PASSWORD` with new token

### Issue 8.4: Badge Not Updating

**Problem**: README badges show "unknown" or don't update

**Solution:**
```markdown
# Check badge URLs are correct:
https://github.com/YOUR_ACTUAL_USERNAME/YOUR_ACTUAL_REPO/actions/workflows/ci-cd.yml/badge.svg

# Force badge refresh by adding ?v=1 to URL temporarily:
![CI/CD](https://github.com/user/repo/actions/workflows/ci-cd.yml/badge.svg?v=1)
```

### Issue 8.5: Local Docker Issues

**Problem**: Local docker-compose fails

**Solution:**
```powershell
# Clean up completely
docker-compose down --volumes --remove-orphans
docker system prune -f

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d

# Check logs
docker-compose logs contact-api
```

---

## 🎉 Final Verification Checklist

After completing all steps, verify:

- [ ] ✅ Local tests pass: `python verify-setup.py`
- [ ] ✅ GitHub repository exists and has all files
- [ ] ✅ GitHub Actions runs automatically on push
- [ ] ✅ Docker Hub repository exists
- [ ] ✅ GitHub secrets are configured correctly
- [ ] ✅ README badges show correct information
- [ ] ✅ Docker images build and push on tags
- [ ] ✅ GitHub releases are created automatically
- [ ] ✅ Can pull and run Docker image: `docker run -p 8000:8000 YOUR_USERNAME/contact-reconciliation-api:latest`

---

## 📞 Need Help?

If you encounter issues:

1. **Check the setup-verification.md** file for troubleshooting
2. **Review GitHub Actions logs** for specific error messages
3. **Test locally first** before pushing to GitHub
4. **Verify all placeholders** are replaced with actual values

**Common Commands for Debugging:**
```powershell
# Check git remotes
git remote -v

# Check git status
git status

# Check Docker
docker --version
docker-compose --version

# Test API locally
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
```

---

## 🚀 Ready to Deploy!

Once all checks pass, your Contact Reconciliation Service is ready for production with:
- ✅ Automated testing on every code change
- ✅ Automated Docker builds on version releases
- ✅ Professional CI/CD pipeline
- ✅ Security scanning and code quality checks
- ✅ Multi-platform Docker support
- ✅ Comprehensive documentation

**Your service is now enterprise-ready!** 🎉
