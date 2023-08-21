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
    "Cerveza": 2.50
    }

# Función para calcular el total del carrito
def calculate_total(cart):
    total = sum(PRODUCTS[item] * quantity for item, quantity in cart.items())
    return total

# Función que se ejecuta cuando un usuario inicia el bot
def start(update: Update, context: CallbackContext) -> None:
    user_name = update.message.from_user.first_name
    greeting_msg = f'¡Hola {user_name}! Bienvenido a Serranísimo. ¿En qué puedo ayudarte?'

    # Botones de interacción
    keyboard = [
        [InlineKeyboardButton("Menú", 
                              callback_data="productos")]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Enviar una imagen
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open('images/profile.jpg', 'rb')
        )

    # Inicializar el carrito
    context.user_data['cart'] = {}
    
    # Inicializar el estado
    context.user_data['state'] = 'initiated'


    update.message.reply_text(greeting_msg, reply_markup=reply_markup)

# Función para mostrar los productos
def display_products(query, context: CallbackContext) -> None:
    """Despliega la botonera de productos en el chat."""
    message = "Aquí tienes nuestro menú:\n\n"
    for product, price in PRODUCTS.items():
        message += f"{product}: ${price}\n"

    keyboard = [[InlineKeyboardButton(product, callback_data=product)] for product in PRODUCTS.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text(message, reply_markup=reply_markup)

# Función para solicitar la dirección del cliente:
def request_address(update: Update, context: CallbackContext) -> None:
    """Solicita al usuario su dirección después de elegir 'No' en la opción de agregar más productos"""
    update.message.reply_text("Por favor, proporciona tu dirección para la entrega:")

# Función que solicita indicar método de pago:
def request_payment_method(update: Update, context: CallbackContext) -> None:
    """Solicita al usuario seleccionar un método de pago después de proporcionar su dirección"""
    keyboard = [
        [InlineKeyboardButton("Efectivo", callback_data="payment_cash")],
        [InlineKeyboardButton("Tarjeta de crédito", callback_data="payment_credit_card")],
        [InlineKeyboardButton("Tarjeta de débito", callback_data="payment_debit_card")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Por favor, selecciona tu método de pago:", reply_markup=reply_markup)

# Función para finalizar el pedido:
def finalize_order(update: Update, context: CallbackContext) -> None:
    """Envía un mensaje final al usuario agradeciendo por su pedido y proporcionando detalles sobre la entrega"""
    query = update.callback_query
    query.answer()
    query.edit_message_text("¡Gracias por tu pedido! Por favor, ten listo tu método de pago. Tu pedido llegará en un tiempo estimado de 30 a 40 minutos. ¡Gracias y buen provecho!")

# Función para manejar las interacciones con los botones
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    logging.info(f"Received callback data: {query.data}")

    # Acción cuando se selecciona un producto
    if query.data in PRODUCTS:
        if query.data in context.user_data['cart']:
            context.user_data['cart'][query.data] += 1
        else:
            context.user_data['cart'][query.data] = 1

        logging.info(f"Current cart: {context.user_data['cart']}") # Rastrear el estado actual del carrito

        total_price = calculate_total(context.user_data['cart'])
        # query.edit_message_text(text, reply_markup=reply_markup)

        # Botones para seleccionar más productos o pasar a las siguientes opciones:
        keyboard = [
            [InlineKeyboardButton("¡Por su puesto!", callback_data="yes"),
             InlineKeyboardButton("Por hoy ya no...", callback_data="no")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            f"Has añadido {query.data} a tu carrito. Hasta el momento, tu total es ${total_price:.2f}. ¿Deseas algo más?", 
            reply_markup=reply_markup
            )

    # Acción cuando se selecciona "Menú"
    elif query.data == "productos":
        display_products(query, context)
        
    # Acción cuando se selecciona "Sí"
    elif query.data == "yes":
        display_products(query, context)

    # Acción cuando se selecciona "No"
    elif query.data == "no":
        query.edit_message_text(f"¡Gracias por tu pedido! Por favor, proporciona tu dirección.")
        context.user_data['state'] = 'waiting_for_address'

    # Acción cuando se selecciona un método de pago
    elif query.data.startswith("payment_"):
        context.user_data['payment_method'] = query.data
        finalize_order(query, context)

def get_gpt_response(prompt):
    """Genera una respuesta a la entrada del usuario utilizando GPT-4"""
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.5,
        max_tokens=100
    )
    return response.choices[0].text.strip()

# Función que maneja las respuestas de los usuarios:
def handle_user_reply(update: Update, context: CallbackContext) -> None:

    # Si el usuario acaba de iniciar el chat, ignoramos su mensaje y cambiamos el estado a None
    if context.user_data.get('state') == 'initiated':
        context.user_data['state'] = None
        return
    
    # El bot está esperando una dirección:
    if context.user_data.get('state') == 'waiting_for_address':
        context.user_data['address'] = update.message.text
        context.user_data['state'] = 'waiting_for_payment_method'
                
        # Llama a la función que solicita el método de pago:
        # update.message.reply_text("¡Gracias por proporcionar tu dirección! Ahora selecciona tu método de pago:")
        request_payment_method(update, context)
        
    else:
        gpt_response = get_gpt_response(update.message.text)
        update.message.reply_text(gpt_response)
        # update.message.reply_text("No estoy seguro de cómo manejar tu mensaje.")

# Función principal
def main() -> None:
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    # Manejadores de botones:
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    # dp.add_handler(MessageHandler(Filters.text & ~Filters.command, start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_user_reply))
    
    # Manejador de mensajes de texto: texto
    # message_handler = MessageHandler(Filters.text & ~Filters.command, request_payment_method)
    # dp.add_handler(message_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()