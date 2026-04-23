import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator

# --- ESTILO VISUAL (FONDO MORADO) ---
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #4B0082, #8A2BE2);
        color: white;
    }
    h1, h2, h3, p {
        color: white;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def on_publish(client,userdata,result):
    print("El dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received=str(message.payload.decode("utf-8"))
    st.write("📩 Mensaje recibido:", message_received)

broker="broker.mqttdashboard.com"
port=1883
client1= paho.Client("Salogib")
client1.on_message = on_message

# --- TITULOS CON EMOJIS ---
st.title("🎤 Detecta tu voz aquí")
st.subheader("🗣️ Control por voz")

image = Image.open('voice_ctrl.jpg')
st.image(image, width=200)

st.write("👉 Toca el botón y habla")

# --- BOTON ---
stt_button = Button(label="🎙️ Iniciar", width=200)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        texto = result.get("GET_TEXT")
        st.success(f"📝 Dijiste: {texto}")

        client1.on_publish = on_publish                            
        client1.connect(broker,port)  
        message =json.dumps({"Act1":texto.strip()})
        ret= client1.publish("voice_ctrlSalogib", message)

    try:
        os.mkdir("temp")
    except:
        pass
