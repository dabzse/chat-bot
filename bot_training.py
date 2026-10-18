import json
import os
import pickle
import secrets

import nltk
import numpy as np
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import SGD

from chat_logger import ChatLogger, get_timestamp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTENTS_PATH = os.path.join(BASE_DIR, "bot_intents.json")
WORDS_PATH = os.path.join(BASE_DIR, "bot_words.pkl")
CLASSES_PATH = os.path.join(BASE_DIR, "bot_classes.pkl")
MODEL_PATH = os.path.join(BASE_DIR, "bot_chatbot_model.h5")

logger = ChatLogger(__file__)

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)

lemmatizer = WordNetLemmatizer()

with open(INTENTS_PATH, "r", encoding="utf-8") as f:
    intents = json.load(f)

words = []
classes = []
documents = []
ignore_letters = ["?", "!", ".", ","]

for intent in intents["intents"]:
    for pattern in intent["patterns"]:
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)
        documents.append((word_list, intent["tag"]))
        if intent["tag"] not in classes:
            classes.append(intent["tag"])

words = [
    lemmatizer.lemmatize(word.lower()) for word in words if word not in ignore_letters
]
words = sorted(set(words))
classes = sorted(set(classes))

with open(WORDS_PATH, "wb") as f:
    pickle.dump(words, f)
with open(CLASSES_PATH, "wb") as f:
    pickle.dump(classes, f)

training = []
output_empty = [0] * len(classes)

for document in documents:
    bag = []
    word_patterns = document[0]
    word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]
    for word in words:
        bag.append(1 if word in word_patterns else 0)

    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1
    training.append([bag, output_row])

# Fisher-Yates shuffle using cryptographically secure secrets.randbelow
for i in range(len(training) - 1, 0, -1):
    j = secrets.randbelow(i + 1)
    training[i], training[j] = training[j], training[i]

train_x = np.array([item[0] for item in training])
train_y = np.array([item[1] for item in training])

model = Sequential()
model.add(Input(shape=(len(train_x[0]),)))
model.add(Dense(128, activation="relu"))
model.add(Dropout(0.5))
model.add(Dense(64, activation="relu"))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation="softmax"))

sgd = SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
model.compile(loss="categorical_crossentropy", optimizer=sgd, metrics=["accuracy"])

logger.log(f"[{get_timestamp()}] Training chatbot model...")
hist = model.fit(train_x, train_y, epochs=200, batch_size=5, verbose=1)
model.save(MODEL_PATH)
logger.log(
    f"[{get_timestamp()}] Training complete! Model saved to {os.path.basename(MODEL_PATH)}"
)
