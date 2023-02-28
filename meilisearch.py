from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from minio import Minio
import io
import meilisearch
import os

# Set up MinIO and Meilisearch clients
minio_client = Minio(
    os.environ.get('a.b.c.d:9000'),
    access_key=os.environ.get('keys'),
    secret_key=os.environ.get('keys'),
    secure=False
)
meilisearch_client = meilisearch.Client(
    os.environ.get('localhost:7700'),
    os.environ.get('API_key')
)

# Define the search function
def search_files(query):
    # Get all the files from the MinIO bucket
    files = minio_client.list_objects(os.environ.get('miniobucket'))

    # Search for the query in each file and index the results in Meilisearch
    matching_files = []
    for file in files:
        data = minio_client.get_object(
            os.environ.get('miniobucket'), file.object_name)
        contents = io.BytesIO(data.read())
        text = contents.read().decode()
        results = meilisearch_client.index("files").search(text)
        for hit in results["hits"]:
            if query in hit["highlighted"]:
                matching_files.append(hit["document"]["path"])

    if matching_files:
        return "\n".join(matching_files)
    else:
        return "No results found"

# Define the bot commands
def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome to my MinIO file search bot!"
    )

def search(update, context):
    query = " ".join(context.args)
    if query:
        result = search_files(query)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=result
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please provide a query to search for."
        )

# Create the bot and add the commands
bot = telegram.Bot(os.environ.get('6013514526:AAF1b_I6wa2uq0cJrnw7G3qesQNylWENlnM'))
updater = Updater(os.environ.get('6013514526:AAF1b_I6wa2uq0cJrnw7G3qesQNylWENlnM'), use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler("start", start)
search_handler = CommandHandler("search", search)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(search_handler)

# Start the bot
updater.start_polling()
