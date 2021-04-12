from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from flask import Flask, request, jsonify


# Default error message
errorMsg = """
      <p>Couldn't complete request.</p>\n
      \n
      <p>- Check if summerization URL is correct / valid</p>\n
      \n
      <p>- Try lowering your sentences parameter (e.g change from 15 sentences to 5)</p>\n
      \n
      <p>- Check if language is properly spelled and valid\n
      (Reminder: language is NOT your language per say, but the language the selected site uses.)</p>\n
      \n
      <p>- Check if website is protected from GET requests from bots\n
      (Cloudflare, Amazon CloudFront, etc.) If this is true, add "cached" to True in your request (uses google cached save).</p>\n
      \n
      <p>- Or your request may be rate limited.</p>
      """

app = Flask(__name__)
@app.route("/sum", methods=["POST"])
def summerize():

  # Non-Post method error
  if request.method != "POST" : return "Only accepting POST method", 400 

  # Checking for POST method
  if request.method == "POST":

    # Checking for parameters, see if they are filled in.
    if request.form.get('site-language', None) is None or str(request.form.get('site-language')) == '':
      return "site-language parameter returned null. Make sure it is are filled in.", 400

    elif request.form.get('url', None) is None or str(request.form.get('url')) == '':
      return "url parameter returned null. Make sure it is filled in.", 400

    try:

      LANGUAGE = request.form.get('site-language')

      # Sentences parameter optional, defaults to 10
      SENTENCES_COUNT = int(request.form.get('sentences'))

      if request.form.get("sentences", None) == None : SENTENCES_COUNT = 10 
        
      # Optional google cached parameter, helps avoid anti-bot pages
      if str(request.form.get('cached')).lower() == "true" and request.form.get('cached', None) != None:

        url = "http://webcache.googleusercontent.com/search?q=cache:" + str(request.form.get('url'))

      else:
        url = str(request.form.get('url'))
        
      # Testing for valid URL / Checking if bot can access it
      try:

        parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))

      except:
        return "URL provided is not valid (or cant reach) try enabling cached. " + url, 400
        
      # or for plain text files
      # parser = PlaintextParser.from_file("document.txt", Tokenizer(LANGUAGE))
      stemmer = Stemmer(LANGUAGE)

      summarizer = Summarizer(stemmer)
      summarizer.stop_words = get_stop_words(LANGUAGE)
      sums = ""
      fax = False
      c = 0

      for sentence in summarizer(parser.document, SENTENCES_COUNT):
            c += 1
            sums += str(sentence)
            sums += "\n"
            if c == SENTENCES_COUNT:
              fax = True

      while True:
        if fax == True:
          return jsonify(str(sums)), 200

    except Exception as e : return errorMsg + " Error: " + str(e), 400

@app.route("/")
def index():
  return "Use a POST on /sum to summerize text."


if __name__ == "__main__":

  # Installing punkt
  import os
  os.system("""python -c "import nltk; nltk.download('punkt')"
  """)

  # Starting local server
  app.run(
  threaded = True,
  host="0.0.0.0"
  )
