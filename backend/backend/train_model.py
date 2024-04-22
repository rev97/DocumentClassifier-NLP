import re
import nltk
from nltk.corpus import stopwords
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn import metrics

# Download NLTK resources
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

# Initialize NLTK's English stopwords
stop_words = set(stopwords.words('english'))



class TextClassifier:

    def __init__(self, dataset_df):
        self.dataset_df = dataset_df
        self.stop_words = set(nltk.corpus.stopwords.words('english'))

    def preprocess_text(self, text):
        cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        cleaned_text = ' '.join(cleaned_text.split())
        lemmatizer = nltk.stem.WordNetLemmatizer()
        lemmatized_text = ' '.join(
            [lemmatizer.lemmatize(word) for word in cleaned_text.split() if word not in self.stop_words])
        return lemmatized_text

    def extract_keywords_nltk(self, text, user_keywords):
        keywords = [word.lower() for word in nltk.word_tokenize(text) if word.lower() in user_keywords]
        return " ".join(keywords)

    def train_model(self, user_keywords):
        X = [self.preprocess_text(text) for text in self.dataset_df['text']]
        X_keywords = [self.extract_keywords_nltk(text, user_keywords) for text in X]
        y = self.dataset_df['Label']

        X_train, X_test, y_train, y_test = train_test_split(X_keywords, y, test_size=0.2, random_state=42)

        model = make_pipeline(
            TfidfVectorizer(sublinear_tf=True, encoding='utf-8', decode_error='ignore', stop_words='english',
                            analyzer='word', norm='l2', lowercase=True), MultinomialNB())

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        accuracy = metrics.accuracy_score(y_test, y_pred)
        print(f"Accuracy: {accuracy}")

        return model, y_pred


