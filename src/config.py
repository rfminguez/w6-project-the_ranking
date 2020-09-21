import os
import dotenv

dotenv.load_dotenv()

PORT = os.getenv("PORT")
DB_URL = os.getenv("DB_URL")
