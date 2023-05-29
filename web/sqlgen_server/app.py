from flask import Flask, request
from model_loader import loader
from transformers import AutoTokenizer, T5ForConditionalGeneration
import logging


PATH_TO_TRAINED_MODEL = "pretrained/pretrained1"
# allow only error logs for the datasets module
logging.getLogger('datasets').setLevel(logging.ERROR)

tokenizer = AutoTokenizer.from_pretrained(PATH_TO_TRAINED_MODEL)
model = T5ForConditionalGeneration.from_pretrained(PATH_TO_TRAINED_MODEL)
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        natural_language_query = request.form.get('natural_language_query')
        return loader.translate_to_sql(model, tokenizer, natural_language_query)


if __name__ == '__main__':
    app.run()
