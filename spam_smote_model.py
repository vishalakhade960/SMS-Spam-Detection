# Load libraries
import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as imbpipeline
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import GradientBoostingClassifier
import warnings
warnings.filterwarnings("ignore",category=RuntimeWarning)


URL_DATA = '\data\spam.csv'


def read_data(path: str) -> pd.DataFrame:
    """Function to read data"""
    try:
        df = pd.read_csv(path, header=0, index_col=0)
        return df
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return pd.DataFrame()


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Function to clean data"""
    df.drop(['Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4'], axis=1, inplace=True)
    df.rename(columns={'v1': 'Class', 'v2': 'Text'}, inplace=True)
    df['Class'] = df['Class'].map({'ham': 0, 'spam': 1})
    return df


def text_preprocess(text: str)  -> str:
    """Function to remove punctuation, stopwords and apply stemming"""
    # remove punctuation
    words = re.sub("[^a-zA-Z]", " ", text)
    # remove stopwords
    stop_words = stopwords.words('english')
    words = [word.lower() for word in words.split() if word.lower()
             not in stop_words]
    # apply Stemming
    porter = PorterStemmer()
    words = [porter.stem(word) for word in words]
    return " ".join(words)


def splitting_data(df: pd.DataFrame):
    """Function to split data on train and test set"""
    data = clean_data(df)
    data['Text'] = data['Text'].apply(text_preprocess)
    X = data['Text']
    y = data['Class']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,
                                                        random_state=42)
    return X_train, X_test, y_train, y_test


def create_models(X_train, X_test, y_train, y_test) -> pd.DataFrame:
    """Calculating models with score"""
    models = pd.DataFrame()
    classifiers = [
        LogisticRegression(),
        MultinomialNB(),
        RandomForestClassifier(n_estimators=50),
        GradientBoostingClassifier(random_state=100, n_estimators=150,
                               min_samples_split=100, max_depth=6),
        LinearSVC(),
        SGDClassifier()]

    for classifier in classifiers:
        try:
            pipeline = imbpipeline(steps=[
                    ('vect', CountVectorizer(min_df=5, ngram_range=(1, 2))),
                    ('tfidf', TfidfTransformer()),
                    ('smote', SMOTE()),
                    ('classifier', classifier)
            ])
            pipeline.fit(X_train, y_train)
            score = pipeline.score(X_test, y_test)
            param_dict = {
                     'Model': classifier._class.name_,
                     'Score': score
            }
            models = models.append(pd.DataFrame(param_dict, index=[0]))
        except Exception as e:
            print(f"Error occurred while fitting {classifier._class.name_}: {str(e)}")

    models.reset_index(drop=True, inplace=True)
    models_sorted = models.sort_values(by='Score', ascending=False)
    print(models_sorted)
    return models_sorted


if _name_ == '_main_':
    df = read_data(URL_DATA)
    X_train, X_test, y_train, y_test = splitting_data(df)
    create_models(X_train, X_test, y_train, y_test)