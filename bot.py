from pyrogram import Client, filters
import requests
import json

# Telegram bot API token, API ID, API Hash, and ImgBB API key
TELEGRAM_BOT_TOKEN = "7920468776:AAEdU_0VNzCvVVT8U96oC1qoV89IGz2Q6qE" 
API_ID = 1814711  # Replace with your API ID from my.telegram.org
API_HASH = "a14491784f65c3bc76afad00c5f280ba"  # Replace with your API Hash from my.telegram.org
IMGBB_API_KEY = "74157fe6d0b0c78d075681b17bef9564"

# Initialize the bot
app = Client(
    "image_caption_bot",
    bot_token=TELEGRAM_BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

# Temporary storage for user data (use a database for production)
user_data = {}
MOVIE_FILE = "movie.txt"

# Function to clean the name (strip and remove unwanted characters)
def clean_name(name):
    return name.replace("[", "- ").replace("]", "")

@app.on_message(filters.command("start"))
async def start_command(client, message):
    """Handle the /start command."""
    await message.reply_text(
        "Welcome to the Movie two json Bot!\n\n"
        "Send me the image with caption, and I'll get its url and gives as json."
    )

# Step 1: Handle receiving an image with a caption
@app.on_message(filters.photo & filters.caption)
def handle_image(client, message):
    caption = message.caption.strip()

    try:
        # Check caption format: {NAME\nID}
        if "\n" not in caption:
            message.reply("Invalid caption format. Please use: {NAME\nID}")
            return

        name, id_part = caption.split("\n", 1)
        name = clean_name(name.strip())  # Clean the name before storing
        id_part = id_part.strip()

        # Step 2: Upload image to ImgBB
        photo = message.photo
        file_path = message.download()

        with open(file_path, "rb") as image_file:
            imgbb_url = f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}"
            response = requests.post(imgbb_url, files={"image": image_file})
            response_data = response.json()

        if response_data["success"]:
            image_url = response_data["data"]["url"]
        else:
            message.reply("Failed to upload image to ImgBB.")
            return

        # Ask user for tags
        message.reply("Image uploaded successfully!\nPlease send tag(s) for the image. Separate multiple tags with spaces.")

        # Save the image details temporarily (use a persistent solution for production)
        user_data[message.chat.id] = {
            "id": id_part,
            "name": name,
            "image_url": image_url
        }

    except Exception as e:
        message.reply(f"An error occurred: {str(e)}")

# Step 2: Handle receiving tags
@app.on_message(filters.text & ~filters.command(["file"]))
def handle_tags(client, message):
    data = user_data.get(message.chat.id)

    if not data:
        message.reply("Please send an image with a valid caption first.")
        return

    tags = message.text.strip().split()

    # Prepare the response
    result = {
        "id": int(data["id"]),
        "name": data["name"],
        "image": data["image_url"],
        "tag": tags
    }

    # Format the result using json.dumps to serialize the tags
    formatted_result = (
        f'{{ "id": {result["id"]}, "name": "{result["name"]}", "image": "{result["image"]}", "tag": {json.dumps(result["tag"])} }}'
    )

    # Send the formatted result back to the user
    message.reply(f"{formatted_result}")

    # Append the result to the movie.txt file
    with open(MOVIE_FILE, "a") as file:
        file.write(formatted_result + ",\n")

    # Clear temporary data
    user_data.pop(message.chat.id, None)

# Step 3: Handle /file command to send the stored file
@app.on_message(filters.command("file"))
def send_file(client, message):
    try:
        with open(MOVIE_FILE, "rb") as file:
            message.reply_document(file, caption="Here is your movie.txt file.")
    except FileNotFoundError:
        message.reply("No data found yet. Please add some entries first.")

# Start the bot
if __name__ == "__main__":
    print("Bot is running...")
    app.run()
