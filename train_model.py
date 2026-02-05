import os
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sentence_transformers import SentenceTransformer

# 1. Define Synthetic Dataset
# Scams: Urgent, Lottery, Bank, Verify
scam_messages = [
    "URGENT: Your bank account has been locked. Verify immediately at http://bit.ly/fake",
    "Congratulations! You won the lottery. Click here to claim your prize.",
    "Verify your KYC details to avoid account suspension.",
    "Your credit card has been charged $500. Call +1-800-FAKE to dispute.",
    "Immediate action required! Your package delivery failed.",
    "You have a refund pending using UPI. Click to receive.",
    "Dear customer, your electricity will be cut off tonight. Pay now.",
    "Job offer: Work from home and earn $500/day. WhatsApp +91-9999999999",
    "Your PAN card needs to be linked to Aadhaar. Updates required.",
    "Netflix payment failed. Update payment details to continue watching.",
    "Final notice before legal action. Pay your tax dues immediately.",
    "Suspicious activity detected on your account. Login to verify.",
    "You are eligible for a low-interest loan. Apply now.",
    "Free iPhone 15 giveaway! Just pay shipping.",
    "Your WhatsApp code is 123456. Do not share.",
    "Investment opportunity! Double your money in 7 days.",
    "Your account will be deactivated in 24 hours.",
    "Click to see who viewed your profile.",
    "Tech support: Your computer has a virus. Call now.",
    "Amazon gift card winner! Claim now."
]

# Safe: Casual, Work, Family
safe_messages = [
    "Hey, are we still on for dinner tonight?",
    "Can you send me the report by EOD?",
    "Happy Birthday! Hope you have a great day.",
    "The meeting has been rescheduled to 3 PM.",
    "What time are you coming home?",
    "Did you see that movie yesterday?",
    "Let's catch up sometime this weekend.",
    "Please find the attached invoice.",
    "On my way, running 5 mins late.",
    "Don't forget to buy milk.",
    "Good morning! Have a nice day.",
    "Can you review this code PR?",
    "Thanks for your help with the project.",
    "Where should we go for lunch?",
    "I'll be out of office tomorrow.",
    "Call me when you're free.",
    "Just checking in, how are things?",
    "Sent you the photos from the trip.",
    "Are you available for a quick call?",
    "Confirmation: Your appointment is booked."
]

# Labels: 1 = Scam, 0 = Safe
dataset = scam_messages + safe_messages
labels = [1] * len(scam_messages) + [0] * len(safe_messages)

# 2. Vectorize Text
print("Loading SentenceTransformer model...")
encoder = SentenceTransformer('all-MiniLM-L6-v2')
X = encoder.encode(dataset)
y = np.array(labels)

# 3. Train Classifier
print("Training LogisticRegression classifier...")
clf = LogisticRegression(random_state=42)
clf.fit(X, y)

# 4. Save Artifacts
output_dir = "backend/ml_assets"
os.makedirs(output_dir, exist_ok=True)

print(f"Saving artifacts to {output_dir}...")
joblib.dump(encoder, os.path.join(output_dir, 'vector_brain.pkl'))
joblib.dump(clf, os.path.join(output_dir, 'scam_model.pkl'))

print("Success! Model trained and saved.")
