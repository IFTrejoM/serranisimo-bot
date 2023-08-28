# Serranísimo Chatbot README

### Descripción:
Este es un bot para Telegram que permite a los usuarios interactuar con el menú de "Serranísimo, Delicias de la sierra ecuatoriana". A través de este bot, los usuarios pueden ver el menú, agregar productos a su carrito, proporcionar comentarios y sugerencias, chatear con una IA y finalizar su pedido compartiendo su ubicación y eligiendo un método de pago.

### Configuración:

1. **Dependencias**:
   - `os`
   - `pickle`
   - `openai`
   - `logging`
   - `dotenv`
   - `telegram`
   - `langchain`

2. **Variables de entorno**: Asegúrese de tener un archivo `.env` en la misma carpeta que su script con las siguientes variables:
   - `TELEGRAM_TOKEN`: Tu token de bot de Telegram.
   - `OPENAI_API_KEY`: Tu API key de OpenAI.

3. **Vectorstore**: El archivo 'serranisimo-script.pkl' debe estar presente en el mismo directorio que este script. Se utiliza para gestionar el chat con la IA.

### Funcionalidad:

- **Inicio del bot**:
  Al iniciar el bot, el usuario recibe un saludo y se presenta con tres opciones: ver el menú, proporcionar comentarios y sugerencias o chatear con la IA.

- **Menú**:
  Los usuarios pueden ver el menú y los precios de los productos. Al seleccionar un producto, se agrega al carrito del usuario. Los usuarios pueden revisar el contenido de su carrito en cualquier momento.

- **Feedback**:
  La sección de comentarios y sugerencias permite a los usuarios proporcionar feedback sobre el servicio. El bot utiliza GPT-3.5 para analizar el sentimiento del comentario y responder adecuadamente.

- **Chat con IA**:
  Los usuarios pueden hacer preguntas a una IA entrenada. El bot utiliza una combinación de `langchain` y OpenAI para gestionar esta interacción.

- **Finalización del pedido**:
  Una vez que los usuarios hayan terminado de agregar productos a su carrito, pueden finalizar su pedido compartiendo su ubicación y eligiendo un método de pago.

### Instrucciones de uso:

1. **Inicio**:
   Inicie una conversación con el bot en Telegram. Se le saludará y se le presentará con las opciones iniciales.

2. **Menú**:
   Seleccione la opción "Menú" para ver y agregar productos a su carrito. Use los botones proporcionados para interactuar con el bot.

3. **Feedback**:
   Seleccione "Comentarios y sugerencias" si desea proporcionar feedback. Escriba su comentario y el bot responderá adecuadamente.

4. **Chat con IA**:
   Si selecciona "¡Chatea con nuestra IA!", puede hacer preguntas a la IA. Escriba su pregunta y espere la respuesta.

5. **Finalización del pedido**:
   Si ha terminado de agregar productos a su carrito, siga las instrucciones para compartir su ubicación y elegir un método de pago.

### Contribuciones:
Si tiene alguna mejora o corrección para este bot, no dude en hacer un pull request o abrir un issue en GitHub.
