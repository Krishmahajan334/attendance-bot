# Cloud Deployment Guide (Render.com)

This folder contains everything needed to run your Attendance Automation on the cloud (without your PC).

## Prerequisites

1.  A **GitHub** account (free).
2.  A **Render.com** account (free tier available).

## Steps to Deploy

### 1. Upload to GitHub

1.  Create a **new repository** on GitHub (e.g., `attendance-bot`).
2.  Upload ALL files in this `cloud_deploy` folder to that repository.
    - `Dockerfile`
    - `requirements.txt`
    - `app.py`
    - `automation.py`
    - `templates/` folder

### 2. Deploy on Render

1.  Log in to your [Render Dashboard](https://dashboard.render.com).
2.  Click **New +** -> **Web Service**.
3.  Connect your GitHub account and select the `attendance-bot` repository you just created.
4.  Configure the service:

    - **Name**: `attendance-bot` (or anything you like)
    - **Region**: Closest to you (e.g., Singapore or Frankfurt suitable for India).
    - **Runtime**: **Docker** (This is important! Do NOT select Python).
    - **Instance Type**: **Free** (if available) or Starter (~$7/mo).

5.  Click **Create Web Service**.

### 3. Usage

- Render will take a few minutes to build (it installs Chrome, etc.).
- Once it says "Live", you will get a URL like `https://attendance-bot.onrender.com`.
- Open that URL on your phone.
- It will work exactly like the local version, but 24/7!

## Troubleshooting

- **Build Failed**: Check the logs. If it says it ran out of memory, you might need the Starter plan ($7/mo) because Chrome works hard.
- **Timeouts**: The "Background Check" feature we built avoids timeouts, so it should be fine!
