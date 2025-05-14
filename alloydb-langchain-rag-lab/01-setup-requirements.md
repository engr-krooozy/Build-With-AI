# Setup and Requirements

This section outlines the necessary accounts, tools, and configurations required to complete this codelab.

## Google Cloud Platform (GCP)

*   **Google Cloud Account and Project:** You will need a Google Cloud account and a Google Cloud Project. If you don't have one, you can sign up at [console.cloud.google.com](https://console.cloud.google.com).
    *   **Project ID:** Take note of your Project ID. It's a unique identifier for your project and will be referred to as `PROJECT_ID` throughout this codelab.
    *   **Billing:** Ensure that [billing is enabled](https://cloud.google.com/billing/docs/how-to/modify-project) for your Google Cloud project. While this codelab is designed to minimize costs, some services used may incur charges. New users might be eligible for a [free trial](http://cloud.google.com/free).

## Software and Tools

*   **Web Browser:** A modern web browser like [Google Chrome](https://www.google.com/chrome/) is recommended.
*   **Google Cloud Shell:** This codelab is designed to be run primarily from [Google Cloud Shell](https://cloud.google.com/shell/docs/using-cloud-shell). Cloud Shell is a browser-based command-line environment that comes pre-loaded with many development tools, including:
    *   `gcloud` (Google Cloud SDK)
    *   `git`
    *   `python` (this lab will use Python 3.11 or later)
    *   `pip` (Python package installer)
*   **LangChain:** The Python library for LangChain will be installed during the lab.
*   **AlloyDB AI specific Python libraries:** Libraries required to interact with AlloyDB AI, such as `google-cloud-alloydb-connector` and `pgvector`, will be installed during the lab.

## Self-Paced Environment Setup

1.  **Sign in to Google Cloud Console:** Access the [Google Cloud Console](http://console.cloud.google.com/) and select or create your project.
    *   If you are using a Gmail account, you can leave the default location as "No organization."
    *   If you are using a Google Workspace account, choose a location appropriate for your organization.
2.  **Start Cloud Shell:**
    *   From the Google Cloud Console, click the Cloud Shell icon on the top right toolbar.
    *   This will provision a virtual machine with a persistent 5GB home directory and common development tools.

All commands in this codelab should be executed within Google Cloud Shell unless specified otherwise. Ensure your Cloud Shell session is active and connected to your chosen project. You can set your project using the command:
```bash
gcloud config set project YOUR_PROJECT_ID
```
Replace `YOUR_PROJECT_ID` with your actual Project ID.
