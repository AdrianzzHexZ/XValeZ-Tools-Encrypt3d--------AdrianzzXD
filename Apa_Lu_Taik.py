import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JS_FILE = os.path.join(BASE_DIR, "pair_enc.js")

os.system("clear")
os.execvp("node", ["node", JS_FILE])
