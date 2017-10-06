#!/usr/bin/python3
import time
import os
from run import PokeBot
from os.path import join, dirname
from dotenv import load_dotenv

while True:
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    NUMBER = os.environ.get("NUMBER")
    PASS = os.environ.get("PASS")

    credentials = (NUMBER, PASS)
    pbb = PokeBot(credentials)
    
    # try:
    #     print("========================================================================================")
    #     print("tentando novamente")
    pbb.start()
    # except:
    #     print("bugou, 10s para reestabelecer")
    #     time.sleep(10)
    #     continue