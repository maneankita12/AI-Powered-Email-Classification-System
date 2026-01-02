from transformers import pipeline
import torch

class EmailClassifier:
    def __init__(self):
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=0 if torch.cuda.is_available() else -1
        )
        
        self.categories = [
            "Customer Support Request",
            "Sales Inquiry", 
            "Technical Problem",
            "Billing Question",
            "Feature Request",
            "Complaint or Issue",
            "Job Application",
            "Marketing or Promotional",
            "Spam or Unwanted",
            "Security or Account Notification",
            "Welcome or Onboarding",
            "General Question"
        ]
    
    def classify(self, email_text, subject=""):
        full_text = f"Subject: {subject}\n\n{email_text}" if subject else email_text
        
        if len(full_text.strip()) < 10:
            return {
                "category": "Unable to classify",
                "confidence": 0,
                "all_scores": {}
            }
        
        result = self.classifier(full_text, self.categories)
        
        return {
            "category": result["labels"][0],
            "confidence": round(result["scores"][0] * 100, 2),
            "all_scores": {
                label: round(score * 100, 2) 
                for label, score in zip(result["labels"], result["scores"])
            }
        }
    
    def add_custom_categories(self, new_categories):
        self.categories.extend(new_categories)
        self.categories = list(set(self.categories))

if __name__ == "__main__":
    classifier = EmailClassifier()
    
    test_email = """
    Hi,
    
    I'm having trouble logging into my account. I keep getting an error 
    message saying my password is incorrect, but I'm sure it's right.
    Can you help me reset it?
    
    Thanks
    """
    
    result = classifier.classify(test_email, subject="Login Problem")
    print(f"Category: {result['category']}")
    print(f"Confidence: {result['confidence']}%")
    print(f"\nAll scores: {result['all_scores']}")
