from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
import paho.mqtt.client as mqtt
import os
from pathlib import Path

# Modelo para validar datos de entrada
class MessageData(BaseModel):
    message: str

# Configuración de FastAPI
app = FastAPI(title="API MQTT Publisher")

# Configuración del broker MQTT
BROKER = "broker.mqtt.cool"
PORT = 1883  # Puerto estándar para MQTT
TOPIC = "ciros"
CLIENT_ID = "MQTT_Publisher_Client"

# Callbacks para el cliente MQTT
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"✅ Conectado al broker MQTT ({BROKER})")
    else:
        print(f"⚠️ Error al conectar: {rc}")

def on_disconnect(client, userdata, rc, properties=None):
    print(f"Desconectado con código: {rc}")

def on_publish(client, userdata, mid):
    print(f"✅ Mensaje publicado con éxito (Message ID: {mid})")

# Crear cliente MQTT
mqtt_client = mqtt.Client(client_id=CLIENT_ID)
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_publish = on_publish

# Conectar al broker de forma más segura
try:
    mqtt_client.connect(BROKER, PORT, 60)
    mqtt_client.loop_start()  # Iniciar loop en segundo plano
except Exception as e:
    print(f"⚠️ Error al conectar con el broker MQTT: {e}")

# Endpoint para favicon
@app.get("/favicon.ico")
async def favicon():
    """Maneja la solicitud de favicon.ico"""
    favicon_path = Path("static/favicon.ico")
    if favicon_path.exists():
        return FileResponse(favicon_path)
    return Response(status_code=204)

# Endpoint original para publicar
@app.post("/publish/")
async def publish_message(data: MessageData):
    """Recibe un mensaje por API y lo publica en MQTT"""
    try:
        result = mqtt_client.publish(TOPIC, data.message, qos=0, retain=True)
        print(result)
        if result.rc != 0:
            raise HTTPException(status_code=500, detail=f"Error al publicar: {result.rc}")
        return {"status": "success", "message": f"Publicado en MQTT: {data.message}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

'''
# Limpieza al cerrar la aplicación
@app.on_event("shutdown")
def shutdown_event():
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    print("Cliente MQTT desconectado")
'''

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1000)
