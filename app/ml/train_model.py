import pickle

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

df = pd.read_csv("app/ml/train.csv")

texts = df["text"].astype(str).tolist()
labels = df["category"].astype(str).tolist()

vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1)
X = vectorizer.fit_transform(texts)

clf = LogisticRegression(max_iter=2000, solver="lbfgs")
clf.fit(X, labels)

with open("app/ml/tfidf_vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

with open("app/ml/tfidf_model.pkl", "wb") as f:
    pickle.dump(clf, f)

print("✔ TF-IDF модель обучения завершено")
