import pickle

with open("app/ml/tfidf_vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

with open("app/ml/tfidf_model.pkl", "rb") as f:
    clf = pickle.load(f)


def predict_category(text: str):
    X = vectorizer.transform([text])
    probs = clf.predict_proba(X)[0]
    idx = probs.argmax()

    return clf.classes_[idx], float(probs[idx])


if __name__ == "__main__":
    print(predict_category("Поїв у кафе"))
    print(predict_category("метро"))
    print(predict_category("аптека"))
