import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from classifier import EmailClassifier
from gmail_connector import GmailConnector
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Email Classifier",
    page_icon="📧",
    layout="centered"
)

@st.cache_resource
def load_classifier():
    return EmailClassifier()

classifier = load_classifier()

CATEGORY_DESCRIPTIONS = {
    "Customer Support Request": "User needs help with a product or service issue. Requires assistance from support team.",
    "Sales Inquiry": "Potential customer asking about products, pricing, or purchase options. Forward to sales team.",
    "Technical Problem": "System error, bug, or technical malfunction reported. Needs technical team attention.",
    "Billing Question": "Questions about invoices, payments, refunds, or account charges. Route to billing department.",
    "Feature Request": "Suggestion for new functionality or product improvement. Add to product roadmap.",
    "Complaint or Issue": "Customer expressing dissatisfaction or reporting a problem. May need escalation.",
    "Job Application": "Application for employment or inquiry about job opportunities. Forward to HR department.",
    "Marketing or Promotional": "Promotional content, newsletters, or marketing materials. Usually automated messages.",
    "Spam or Unwanted": "Unsolicited commercial email or irrelevant content. Consider filtering or blocking.",
    "Security or Account Notification": "Alerts about account security, password changes, or login activities.",
    "Welcome or Onboarding": "New user welcome messages or getting started guides. Usually automated onboarding.",
    "General Question": "General inquiry that doesn't fit other categories. Needs initial review before routing."
}

st.title("Email Classifier")
st.markdown("Choose how you want to classify emails")
st.divider()

option = st.radio(
    "Select an option:",
    ["Enter Email Manually", "Connect to Gmail"],
    horizontal=True
)

st.divider()

if option == "Enter Email Manually":
    st.subheader("Enter Email Details")
    
    subject = st.text_input(
        "Subject", 
        placeholder="Enter email subject"
    )
    
    email_body = st.text_area(
        "Email Content", 
        height=250,
        placeholder="Enter or paste email content here..."
    )
    
    if st.button("Classify", type="primary", use_container_width=True):
        if email_body.strip():
            with st.spinner("Classifying..."):
                result = classifier.classify(email_body, subject)
                
                st.success("Classification Complete")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Category", result['category'])
                with col2:
                    st.metric("Confidence", f"{result['confidence']}%")
                
                if result['category'] in CATEGORY_DESCRIPTIONS:
                    st.info(CATEGORY_DESCRIPTIONS[result['category']])
                
                st.subheader("Top 5 Category Scores")
                
                sorted_scores = sorted(
                    result['all_scores'].items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:5]
                
                for category, score in sorted_scores:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.progress(score / 100)
                    with col2:
                        st.write(f"{score}%")
                    st.caption(category)
        else:
            st.warning("Please enter email content")

else:
    st.subheader("Connect to Gmail")
    
    with st.form("gmail_form"):
        gmail_email = st.text_input(
            "Gmail Address",
            value=os.getenv("GMAIL_ADDRESS", ""),
            placeholder="your.email@gmail.com"
        )
        
        gmail_password = st.text_input(
            "Gmail App Password",
            value=os.getenv("GMAIL_APP_PASSWORD", ""),
            type="password",
            placeholder="16-character app password",
            help="Use Gmail App Password, not your regular password"
        )
        
        num_emails = st.number_input(
            "Number of emails to fetch",
            min_value=1,
            max_value=20,
            value=5
        )
        
        submitted = st.form_submit_button(
            "Fetch Emails", 
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            if gmail_email and gmail_password:
                try:
                    with st.spinner("Connecting to Gmail and cleaning content..."):
                        gmail = GmailConnector(gmail_email, gmail_password)
                        emails = gmail.get_recent_emails(num_emails=num_emails)
                        gmail.disconnect()
                        
                        st.session_state['fetched_emails'] = emails
                        st.success(f"Successfully fetched {len(emails)} emails")
                        st.rerun()
                except Exception as e:
                    st.error(f"Connection failed: {str(e)}")
                    st.info("Make sure you're using a Gmail App Password")
            else:
                st.warning("Please enter both email and password")
    
    if 'fetched_emails' in st.session_state and st.session_state['fetched_emails']:
        st.divider()
        st.subheader("Recent Emails")
        
        for i, email_data in enumerate(st.session_state['fetched_emails'], 1):
            with st.expander(f"{i}. {email_data['subject']}", expanded=False):
                st.write(f"**From:** {email_data['sender']}")
                st.write(f"**Date:** {email_data['date']}")
                
                st.write("**Cleaned Content (used for classification):**")
                preview = email_data['body'][:400] if len(email_data['body']) > 400 else email_data['body']
                st.text_area("", preview, height=150, key=f"preview_{i}", disabled=True)
                
                if st.button("Classify This Email", key=f"classify_{i}"):
                    with st.spinner("Classifying..."):
                        result = classifier.classify(
                            email_data.get('body_full', email_data['body']), 
                            email_data['subject']
                        )
                        
                        st.success("Classification Complete")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Category", result['category'])
                        with col2:
                            st.metric("Confidence", f"{result['confidence']}%")
                        
                        if result['category'] in CATEGORY_DESCRIPTIONS:
                            st.info(CATEGORY_DESCRIPTIONS[result['category']])
                        
                        st.write("**Top 5 Predictions:**")
                        sorted_scores = sorted(
                            result['all_scores'].items(), 
                            key=lambda x: x[1], 
                            reverse=True
                        )[:5]
                        
                        for cat, score in sorted_scores:
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.progress(score / 100)
                            with col2:
                                st.write(f"{score}%")
                            st.caption(cat)

with st.sidebar:
    st.header("Available Categories")
    
    for i, cat in enumerate(classifier.categories, 1):
        with st.expander(f"{i}. {cat}"):
            st.caption(CATEGORY_DESCRIPTIONS.get(cat, "No description available"))
    
    st.divider()
    st.caption("Model: facebook/bart-large-mnli")

st.divider()
st.caption("Email classification powered by AI transformers")
