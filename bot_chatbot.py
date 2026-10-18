import json
import os
import pickle
import secrets
import sys

import nltk
import numpy as np
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model

from chat_logger import ChatLogger, get_timestamp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTENTS_PATH = os.path.join(BASE_DIR, 'bot_intents.json')
WORDS_PATH = os.path.join(BASE_DIR, 'bot_words.pkl')
CLASSES_PATH = os.path.join(BASE_DIR, 'bot_classes.pkl')
MODEL_PATH = os.path.join(BASE_DIR, 'bot_chatbot_model.h5')

logger = ChatLogger(__file__)

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

lemmatizer = WordNetLemmatizer()

if not (os.path.exists(MODEL_PATH) and os.path.exists(WORDS_PATH) and os.path.exists(CLASSES_PATH)):
    logger.log(f"[{get_timestamp()}] Model or data files missing! Please run 'python bot_training.py' first.")
    sys.exit(1)

with open(INTENTS_PATH, 'r', encoding='utf-8') as f:
    intents = json.load(f)

with open(WORDS_PATH, 'rb') as f:
    words = pickle.load(f)

with open(CLASSES_PATH, 'rb') as f:
    classes = pickle.load(f)

model = load_model(MODEL_PATH)


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)


def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]), verbose=0)[0]
    error_threshold = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > error_threshold]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list


def get_response(intents_list, intents_json):
    if not intents_list:
        return "I didn't quite understand that. Could you rephrase?"
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            return secrets.choice(i['responses'])
    return "I didn't quite understand that. Could you rephrase?"


if __name__ == '__main__':
    logger.log(f"[{get_timestamp()}] Chatbot is running! (Type '/quit' or '!q' to exit)")
    while True:
        try:
            message = input("You: ")
        except (EOFError, KeyboardInterrupt):
            logger.log(f"[{get_timestamp()}] You left the conversation.")
            logger.log(f"[{get_timestamp()}] Bot: Goodbye!")
            break

        if not message.strip():
            continue

        if message.strip().lower() in ['/quit', '!q', 'quit', 'exit']:
            logger.log(f"[{get_timestamp()}] You: {message}")
            logger.log(f"[{get_timestamp()}] You left the conversation.")
            logger.log(f"[{get_timestamp()}] Bot: Goodbye!")
            break

        timestamp = get_timestamp()
        logger.log(f"[{timestamp}] You: {message}")
        ints = predict_class(message)
        res = get_response(ints, intents)
        logger.log(f"[{get_timestamp()}] Bot: {res}")
