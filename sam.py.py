import os
import telebot
import logging
import time
import asyncio
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from threading import Thread

TOKEN = '7905527454:AAFU6FfZUXKYzShaiUAxAo1_ZNHGHTqzjww'  # Replace with your Telegram bot token
CHANNEL_ID = -1002292224661  # Replace with your channel ID for sending attack messages
FORWARD_CHANNEL_ID = -1002292224661  # Replace with your forward channel ID

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

bot = telebot.TeleBot(TOKEN)
REQUEST_INTERVAL = 1

attack_in_progress = False
remaining_attack_time = 0

# Create the send_message_with_retry function
def send_message_with_retry(chat_id, text, reply_markup=None, parse_mode=None, retry_limit=5, delay=10):
    """Function to handle rate limiting and retry logic."""
    retries = 0
    while retries < retry_limit:
        try:
            bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode=parse_mode)
            break  # If the message is sent successfully, break out of the loop
        except telebot.apihelper.ApiException as e:
            if e.result_json.get("error_code") == 429:
                # If rate limit is exceeded (Error 429), wait and try again
                retry_after = e.result_json.get("parameters", {}).get("retry_after", 1)
                time.sleep(retry_after)
                retries += 1
                logging.warning(f"Rate limit exceeded. Retrying after {retry_after}s...")
            else:
                logging.error(f"Failed to send message: {e}")
                break
        time.sleep(delay)  # Delay between retries

# Start function for the bot
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Create a markup object for custom keyboard
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)

    # Create buttons
    btn1 = KeyboardButton("Instant Plan 🧡")
    btn2 = KeyboardButton("Instant++ Plan 💥")
    btn3 = KeyboardButton("Canary Download✔️")
    btn4 = KeyboardButton("My Account🏦")
    btn5 = KeyboardButton("Help❓")
    btn6 = KeyboardButton("Contact admin✔️")

    # Add buttons to the markup
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)

    # Send message with buttons
    send_message_with_retry(message.chat.id, "*Choose an option:*", reply_markup=markup, parse_mode='Markdown')

# Function to handle Instant++ Plan button press
@bot.message_handler(func=lambda message: message.text == "Instant++ Plan 💥")
def handle_instant_plus_plan(message):
    # Prompt user for target IP, port, and duration
    bot.send_message(message.chat.id, "*Please provide the target IP, port, and duration (in seconds) separated by spaces.*", parse_mode='Markdown')
    bot.register_next_step_handler(message, process_attack_command)

# Function to process attack command and execute the attack
def process_attack_command(message):
    global attack_in_progress
    try:
        args = message.text.split()
        if len(args) != 3:
            bot.send_message(message.chat.id, "*Invalid command format. Please use: target_ip target_port duration*", parse_mode='Markdown')
            return
        
        target_ip, target_port, duration = args[0], int(args[1]), int(args[2])

        # Limit attack duration to 120 seconds
        if duration > 120:
            duration = 120
            bot.send_message(message.chat.id, "*Attack duration has been limited to 120 seconds.*", parse_mode='Markdown')

        # Check if an attack is already in progress
        if attack_in_progress:
            bot.send_message(message.chat.id, "*An attack is already in progress. Please wait until it finishes before initiating another one.*", parse_mode='Markdown')
            return

        # Start the attack
        attack_in_progress = True
        bot.send_message(message.chat.id, f"Attack started on Host: {target_ip}, Port: {target_port}, Duration: {duration} seconds.")

        # Simulate attack running (this can be replaced with actual attack code)
        asyncio.run(run_attack_simulation(target_ip, target_port, duration))

        # Notify that attack is complete
        bot.send_message(message.chat.id, "*Attack has finished! You can initiate another attack now.*", parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error in processing attack command: {e}")
        bot.send_message(message.chat.id, "*There was an error processing your request. Please try again.*", parse_mode='Markdown')

# Simulate an attack process (this is where you would run the actual attack logic)
async def run_attack_simulation(target_ip, target_port, duration):
    await asyncio.sleep(duration)
    attack_in_progress = False
    logging.info(f"Attack on Host: {target_ip}, Port: {target_port}, Duration: {duration} seconds has completed.")

# Start the bot's asyncio loop
async def start_asyncio_loop():
    while True:
        await asyncio.sleep(REQUEST_INTERVAL)

# Start the bot polling and handle async tasks
if __name__ == "__main__":
    # Ensure that the bot polling is run within asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(bot.polling(none_stop=True))  # Run bot polling in the background
    loop.run_forever()  # Keep the event loop running
    logging.info("Starting Telegram bot...")
    
    # Run the event loop
    while True:
        try:
            loop.run_until_complete(start_asyncio_loop())  # Keep async loop running
        except Exception as e:
            logging.error(f"An error occurred while polling: {e}")
        logging.info(f"Waiting for {REQUEST_INTERVAL} seconds before the next request...")
        time.sleep(REQUEST_INTERVAL)
