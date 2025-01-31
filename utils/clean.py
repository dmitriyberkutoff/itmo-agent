import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def clean_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    words = word_tokenize(text)
    stop_words = set(stopwords.words("russian"))
    filtered_words = [word for word in words if word not in stop_words]
    res = " ".join(filtered_words)
    return res