LiveTranslate
=============
LiveTranslate detects foreign language text from a video feed, and displays the text's English translation in real-time.

Setup
=====
1. Install Python 2.7x 
    * https://www.python.org/downloads/
2. Install Numpy 1.7
    * http://www.numpy.org/
3. Install OpenCV 2.4.10
    * http://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv
4. Install tesseract-ocr (including desired language packs) and the Python libraries
    * https://code.google.com/p/tesseract-ocr/downloads/list
5. Install python-tesseract
    * https://code.google.com/p/python-tesseract/downloads/list
6. Follow this guide to get your Microsoft Translator credentials
    * http://blogs.msdn.com/b/translation/p/gettingstarted1.aspx
7. Grab azure_translate_api.py
    * Place in the same directory as main.py
    * https://github.com/neerajcse/python_azure_translate_api
8. Install the Requests Python package
  * "pip install requests" (Use Google if you need to learn how to use pip)

Usage
=====
1. Run main.py
2. (Optional) Change the source and target translation languages 
3. Hold up (highly-contrasting) text and have it translated!
4. ESC to quit.
