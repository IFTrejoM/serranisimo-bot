import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters
import openai
from dotenv import load_dotenv
import os

# Cargar las variables del .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# Inicialización de logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Definición del diccionario de productos
PRODUCTS = {
    "Fritada": 10.00,
    "Yahuarlocro": 9.50,
    "Guatita": 9.50,
    "Empanada de morocho": 2.00,
    "Humita": 1.50,
    "Coca-Cola": 1.50,
    "Fioravanti": 1.50
}

# Función para calcular el total del carrito
def calculate_total(cart):
    total = sum(PRODUCTS[item] * quantity for item, quantity in cart.items())
    return total

# Función que se ejecuta cuando un usuario inicia el bot
def start(update: Update, context: CallbackContext) -> None:
    user_name = update.message.from_user.first_name  # Obtenemos el nombre del usuario
    greeting_msg = f'¡Hola {user_name}! Bienvenido a Serranísimo. ¿En qué puedo ayudarte?'

    # Botones de interacción
    keyboard = [
        [InlineKeyboardButton("Menú", callback_data="productos")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Inicializar el carrito
    context.user_data['cart'] = {}

    update.message.reply_text(greeting_msg, reply_markup=reply_markup)

# Función para mostrar los productos
def display_products(query, context: CallbackContext) -> None:
    message = "Aquí tienes nuestros productos:\n\n"
    for product, price in PRODUCTS.items():
        message += f"{product}: ${price}\n"

    keyboard = [[InlineKeyboardButton(product, callback_data=product)] for product in PRODUCTS.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text(message, reply_markup=reply_markup)

# Función para manejar las interacciones con los botones
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer() # Es importante responder al callback para evitar errores
    logging.info(f"Received callback data: {query.data}")

    # Acción cuando se selecciona un producto
    if query.data in PRODUCTS:
        if query.data in context.user_data['cart']:
            context.user_data['cart'][query.data] += 1
        else:
            context.user_data['cart'][query.data] = 1

        # Rastrear el estado actual del carrito
        logging.info(f"Current cart: {context.user_data['cart']}")  # <-- Add this line here

        total_price = calculate_total(context.user_data['cart'])
        query.edit_message_text(f"Has añadido {query.data} a tu carrito. Tu total hasta ahora es ${total_price:.2f}. ¿Deseas algo más?")

    # Acción cuando se selecciona "Menú"
    elif query.data == "productos":
        display_products(query, context)

# Función principal
def main() -> None:
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    # Handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, start))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()