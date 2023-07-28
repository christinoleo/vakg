import os
from dotenv import load_dotenv

load_dotenv()

login = os.environ.get('NEO4J_LOGIN')
url = os.environ.get('NEO4J_URL')
password = os.environ.get('NEO4J_PASSWORD')
print(login, password, url)
