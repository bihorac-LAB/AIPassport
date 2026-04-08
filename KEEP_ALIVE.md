# Streamlit Keep-Alive Automation

This repository includes a **GitHub Action** that periodically visits your Streamlit app's URL to prevent it from going into hibernation (which typically happens after a period of inactivity on the free tier).

## How it Works
The automation is defined in [`.github/workflows/keep_alive.yml`](file:///Users/chanakyavasantha/ic3/AIP-Guide/AIPassport/.github/workflows/keep_alive.yml). It uses a lightweight request (without following redirects) to hit the Streamlit Cloud front door every 6 hours, ensuring the instance stays "warm" even without user traffic.

## Managing the Action
1.  **Change the URL**: If your Streamlit app's URL changes, update it in the [`.github/workflows/keep_alive.yml`](file:///Users/chanakyavasantha/ic3/AIP-Guide/AIPassport/.github/workflows/keep_alive.yml) file.
2.  **Manual Trigger**: You can run the keep-alive task manually by going to your GitHub repository -> **Actions** -> **Streamlit Keep-Alive** -> **Run workflow**.

## Disabling the Action
To stop the pings, either:
- Delete the [`.github/workflows/keep_alive.yml`](file:///Users/chanakyavasantha/ic3/AIP-Guide/AIPassport/.github/workflows/keep_alive.yml) file.
- Or disable it in the GitHub Actions dashboard.
