import pandas as pd
import pickle
import re
import os
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z ]', '', text)
    words = [w for w in text.split() if w not in stop_words]
    return " ".join(words)

print("📂 Loading Resume.csv...")
df = pd.read_csv("Resume.csv")
df.dropna(subset=["Resume_str", "Category"], inplace=True)
df["cleaned"] = df["Resume_str"].apply(clean_text)

print(f"✅ Total Resumes : {len(df)}")
print(f"✅ Categories    : {df['Category'].nunique()}")
print(f"   {list(df['Category'].unique())}\n")

X_train, X_test, y_train, y_test = train_test_split(
    df["cleaned"], df["Category"],
    test_size=0.2, random_state=42, stratify=df["Category"]
)

print("🔧 Training TF-IDF + Logistic Regression...")
vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec  = vectorizer.transform(X_test)

model = LogisticRegression(max_iter=1000, C=5)
model.fit(X_train_vec, y_train)

y_pred = model.predict(X_test_vec)
acc = accuracy_score(y_test, y_pred)
print(f"\n📊 Model Accuracy: {acc * 100:.2f}%")
print("\n📋 Classification Report:")
print(classification_report(y_test, y_pred))

os.makedirs("model", exist_ok=True)
pickle.dump(vectorizer, open("model/resume_vectorizer.pkl", "wb"))
pickle.dump(model,      open("model/resume_classifier.pkl", "wb"))
print("\n✅ Resume classifier saved to model/")