import sys
import os
from dotenv import load_dotenv

from bot.client import Client

if len(sys.argv) > 1 and sys.argv[1] == "prod":
    environment = "prod"
else:
    environment = "dev"

# Load the appropriate .env file
if environment == "dev":
    print("using dev env")
    load_dotenv(".env.local")
else:
    load_dotenv(".env.prod")

My_Bot = Client()

if __name__ == "__main__":
    if environment == "dev":
        print("Dev mode launched running ...")
        My_Bot.run(os.getenv("TOKEN"))
    elif environment == "prod":
        print("Prod mode launched running ...")
        My_Bot.run(os.getenv("TOKEN"))
    else:
        print("Invalid environment")
