# AI-Powered Email Classification System

An intelligent email classifier that uses transformer models to automatically categorize emails into predefined categories.

## Features

- Manual email entry for classification
- Gmail integration to fetch and classify recent emails
- 12 predefined categories
- Real-time classification with confidence scores
- Clean, modern UI

## Categories

1. Customer Support Request
2. Sales Inquiry
3. Technical Problem
4. Billing Question
5. Feature Request
6. Complaint or Issue
7. Job Application
8. Marketing or Promotional
9. Spam or Unwanted
10. Security or Account Notification
11. Welcome or Onboarding
12. General Question

## Technology Stack

- Streamlit for the web interface
- Hugging Face Transformers (BART model)
- Gmail IMAP for email fetching
- Zero-shot classification approach

## Local Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `streamlit run src/app.py`

## Deployment

Deployed on Streamlit Community Cloud
