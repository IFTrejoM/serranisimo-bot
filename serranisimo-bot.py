import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
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

# Definición del diccionario de productos:
PRODUCTS = {
    "Fritada 🐷": 10.00,
    "Yahuarlocro 🐑": 9.50,
    "Guatita 🐮": 9.50,
    "Seco de chivo 🐐": 9.50,
    "Empanada de morocho 🥟": 2.00,
    "Humita 🌽": 1.50,
    "Higos con queso 🍨": 2.50,
    "Pristiños con miel 🥞": 2.50,
    "Jugo de frutas 🧃": 2.00,
    "Coca-Cola 🥤": 1.50,
    "Cerveza 🍺": 2.50
    }

# Función que se ejecuta cuando un usuario inicia el bot:
def start(update: Update, context: CallbackContext) -> None:
    user_name = update.message.from_user.first_name
    greeting_msg = f'¡Hola, {user_name}! Bienvenido al bot de Serranísimo 👨🏽‍🌾🤩 ¿En qué podemos ayudarte?'

    # Botones de interacción iniciales:
    keyboard = [
        [InlineKeyboardButton("Menú 😋", callback_data="productos"),
        InlineKeyboardButton("Comentarios y sugerencias 🙋🏻‍♂️", callback_data="feedback")]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Enviar una imagen
    with open('images/logo.png', 'rb') as photo:
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo
        )

    # Inicializar el carrito
    context.user_data['cart'] = {}

    # Inicializar el estado
    context.user_data['state'] = 'initiated'

    update.message.reply_text(greeting_msg, reply_markup=reply_markup)

# Función para análisis de sentimiento con GPT-3.5 en la sección "Comentarios y recomendaciones":
def analyze_sentiment(text: str) -> str:
    """
    Analiza el sentimiento de un texto utilizando GPT-3.5.
    """
    # Formulamos una pregunta específica para el modelo en formato de chat
    messages = [
        {"role": "system", "content": "You are a highly trained sentiment analysis expert, specialized in assessing text messages from restaurant customers. \
            Your expertise lies in distinguishing subtle nuances in feedback to accurately categorize sentiments. Use your expertise to provide the most precise sentiment evaluation possible."},
        {"role": "user", "content": f"¿What is the general feeling of this comment? '{text}'"}
    ]

    # Enviamos la pregunta al modelo usando el endpoint de chat
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo-0301",
      messages=messages
    )
    # Procesamos la respuesta
    sentiment_response = response.choices[0].message['content'].strip()
    if "positive" in sentiment_response:
        return "positive"
    elif "negative" in sentiment_response:
        return "negative"
    else:
        return "neutral"

# Función para manejar el feedback del usuario en "Comentarios y recomendaciones":
def handle_feedback(update: Update, context: CallbackContext, feedback: str) -> None:
    """ Maneja el feedback del usuario y envía una respuesta basada en el sentimiento """
    
    user_name = update.message.from_user.first_name
    
    # Invoca a la función que analiza sentimientos:
    sentiment = analyze_sentiment(feedback)
    
    # Devuelve un mensaje dependiendo del resultado de analyze_sentiment():
    if sentiment == "positive":
        update.message.reply_text(f"¡Gracias por tus amables palabras, {user_name}! Trabajamos para brindarte el mejor servicio. 😊")
    elif sentiment == "negative":
        update.message.reply_text(f"Lamentamos que no estés satisfecho, {user_name}. Una operadora se comunicará contigo por este medio 👩🏻📲. Agradecemos tu feedback y trabajaremos en mejorar.")
    else:
        update.message.reply_text(f"¡Gracias por tu feedback, {user_name}!. Siempre buscamos mejorar y valoramos tus comentarios. 👍")
    
    context.user_data['state'] = None

# Función para calcular el total del carrito:
def calculate_total(cart):
    total = sum(PRODUCTS[item] * quantity for item, quantity in cart.items())
    return total

# Función que despliega la botonera del menú en el chat.
def display_menu(query, context: CallbackContext) -> None:
    """
    Despliega la botonera del menú en el chat.
    """
    message = "Aquí tienes nuestro menú:\n\n"
    for product, price in PRODUCTS.items():
        message += f"{product}: ${price:.2f}\n"
    
    # Lista de botones de los productos + botón "VER CARRITO 🛒"
    product_buttons = [[InlineKeyboardButton(product, callback_data=product)] for product in PRODUCTS.keys()]
    cart_button = [InlineKeyboardButton("VER CARRITO 🛒", callback_data="vercarrito")]
    keyboard = product_buttons + [cart_button]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text(message, reply_markup=reply_markup)

# Función que controla el botón del carrito:
def view_cart(query, context: CallbackContext) -> None:
    """
    Función que controla el botón del carrito
    """
    cart = context.user_data.get('cart', {})
    if not cart:
        message = "Tu carrito está vacío... 😔 ¡llénalo de cosas deliciosas! 🤤"
    else:
        message = "Contenido de tu carrito: 🛒\n\n"
        for product, quantity in cart.items():
            message += f"{product}: {quantity}\n"

    # Botón para volver al menú
    keyboard = [[InlineKeyboardButton("Volver al Menú 🔄", callback_data="menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.message.reply_text(message, reply_markup=reply_markup)

# Función para solicitar la localización del cliente:
def request_location(update: Update, context: CallbackContext) -> None:
    """Solicita la localización al usuario después de elegir 'Por hoy ya no...' en la opción de agregar más productos"""
    
    # Calcula el valor total de la orden:
    total_invoice = calculate_total(context.user_data['cart'])
    
    # Genera el mensaje de total de la orden y solicita localización:
    update.callback_query.message.reply_text(
        f"¡Gracias por tu pedido! El valor total de tu orden es ${total_invoice:.2f}. \
            Por favor, comparte tu ubicación utilizando el botón 'Clip' 📎 y seleccionando 'Ubicación' 📍",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(text="Enviar ubicación", request_location=True)]],
            one_time_keyboard=True
        )
    )
    context.user_data['state'] = 'waiting_for_location'

def handle_location(update: Update, context: CallbackContext) -> None:
    user_location = update.message.location
    latitude = user_location.latitude
    longitude = user_location.longitude
    
    # Guardar la ubicación en context.user_data:
    context.user_data['location'] = {
        'latitude': latitude,
        'longitude': longitude
    }
    
    # Luego de guardar la ubicación, solicita método de pago
    request_payment_method(update, context)

# Función que solicita indicar método de pago:
def request_payment_method(update: Update, context: CallbackContext) -> None:
    """Solicita al usuario seleccionar un método de pago después de proporcionar su dirección"""
    keyboard = [
        [InlineKeyboardButton("💵 Efectivo", callback_data="payment_cash")],
        [InlineKeyboardButton("💳 Tarjeta de crédito", callback_data="payment_credit_card")],
        [InlineKeyboardButton("🏧 Tarjeta de débito", callback_data="payment_debit_card")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("¡Gracias por proporcionar tu ubicación! Ahora, selecciona tu método de pago: 💲",
                              reply_markup=reply_markup)

# Función que maneja las respuestas de los usuarios:
def handle_user_reply(update: Update, context: CallbackContext) -> None:

    user_name = update.message.from_user.first_name

    # Si el usuario acaba de iniciar el chat, ignoramos su mensaje y cambiamos el estado a None:
    if context.user_data.get('state') == 'initiated':
        context.user_data['state'] = None
        update.message.reply_text("Por favor, utiliza los botones del menú para seleccionar productos")
        return
    
     # El bot está esperando una ubicación:
    elif context.user_data.get('state') == 'waiting_for_location':
        update.message.reply_text(f"Por favor {user_name}, comparte tu ubicación utilizando el botón 'Clip' 📎 y seleccionando 'Ubicación' 📍")
        return

    # El bot está esperando feedback (felicitaciones o sugerencias):
    elif context.user_data.get('state') == 'waiting_for_feedback':
        feedback = update.message.text
        handle_feedback(update, context, feedback)
        return

    # Si el estado es None o no existe, muestra el saludo inicial y el menú:
    elif not context.user_data.get('state'):
        start(update, context)    

# Función para manejar las interacciones con los botones
def button(update: Update, context: CallbackContext) -> None:
    """"Función para manejar las interacciones con los botones."""

    query = update.callback_query

    user_name = query.from_user.first_name  # Accede al nombre del usuario desde aquí

    query.answer()
    
    logging.info(f"Received callback data: {query.data}")

    # Acción cuando se selecciona un producto
    if query.data in PRODUCTS:
        if query.data in context.user_data['cart']:
            context.user_data['cart'][query.data] += 1
        else:
            context.user_data['cart'][query.data] = 1

        logging.info(f"Current cart: {context.user_data['cart']}")

        total_price = calculate_total(context.user_data['cart'])

        # Botones para seleccionar más productos o pasar a las siguientes opciones:
        keyboard = [
            [InlineKeyboardButton("¡Por su puesto! 😎", callback_data="yes"),
             InlineKeyboardButton("Por hoy ya no... 😳", callback_data="no")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            f"Has añadido {query.data} a tu carrito. Hasta el momento, tu total es ${total_price:.2f}. ¿Deseas algo más?", 
            reply_markup=reply_markup
            )

    # Acción cuando se selecciona "Comentarios y sugerencias:"
    elif query.data == "feedback":
        query.edit_message_text(f"Por favor {user_name}, comparte tus comentarios o sugerencias con nosotros: 💬")
        context.user_data['state'] = 'waiting_for_feedback'

    # Acción cuando se selecciona "Menú"
    elif query.data == "productos":
        display_menu(query, context)
        
    # Acción cuando se selecciona "Sí"
    elif query.data == "yes":
        display_menu(query, context)

    # Acción cuando se selecciona "No"
    elif query.data == "no":
        request_location(update, context)
        
    # Acción cuando se selecciona "Ver carrito"
    if query.data == "vercarrito":
        view_cart(query, context)

    elif query.data == "menu":
        display_menu(query, context)

    # Acción cuando se selecciona un método de pago
    elif query.data.startswith("payment_"):
        context.user_data['payment_method'] = query.data
        query.edit_message_text(f"¡Muchas gracias, {user_name}! ¡Nuestro motorista 🛵 estará contigo en 30-40 minutos ⏳ ten listo tu método de pago! ¡Disfruta tu comida!")
        context.user_data['state'] = None

# Función principal
def main() -> None:
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    # Manejadores de botones:
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.location, handle_location))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_user_reply))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()