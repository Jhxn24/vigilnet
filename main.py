import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
import threading
import datetime
from scapy.all import sniff, DNS, DNSQR

app = FastAPI()

# Guardamos la conexión activa del profesor
conexion_profesor: WebSocket = None

# Guardamos el bucle de ejecución de FastAPI para poder enviar alertas desde el hilo del sniffer
loop_principal = None

@app.get("/")
async def obtener_panel():
    """Sirve la interfaz HTML del panel del profesor al acceder a http://localhost:8000"""
    try:
        with open("index.html", "r", encoding="utf-8") as archivo:
            return HTMLResponse(content=archivo.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: No se encontró index.html</h1>", status_code=404)

@app.get("/simular")
async def simular_trampa():
    ahora = datetime.datetime.now().strftime("%H:%M:%S")
    alerta_falsa = {
        "hora": ahora,
        "ip": "192.168.2.50",
        "dominio": "chatgpt.com (Simulado)"
    }
    await enviar_alerta_trampa(alerta_falsa)
    return {"status": "Alerta enviada al panel con éxito"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global conexion_profesor
    await websocket.accept()
    conexion_profesor = websocket
    print("🔌 [VIGILNET] El panel del profesor se ha conectado al WebSocket.")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        print("❌ [VIGILNET] El panel del profesor se ha desconectado.")
        conexion_profesor = None

async def enviar_alerta_trampa(datos_alerta: dict):
    """Función que envía la alerta en tiempo real a la interfaz."""
    global conexion_profesor
    if conexion_profesor:
        try:
            await conexion_profesor.send_json(datos_alerta)
        except Exception as e:
            print(f"Error al enviar datos por WebSocket: {e}")

# =====================================================================
#  NUEVA SECCIÓN: INTERCEPTOR INALÁMBRICO INTEGRADO (SNIFFER)
# =====================================================================

def procesar_paquete(paquete):
    """
    Analiza cada paquete DNS inalámbrico extrayendo direcciones IPv4 o IPv6 reales.
    """
    global loop_principal
    # Verificamos si es una consulta DNS estándar (petición de página web)
    if paquete.haslayer(DNS) and paquete[DNS].qr == 0:
        try:
            # Extraemos el dominio y lo convertimos a texto limpio
            dominio = paquete[DNSQR].qname.decode('utf-8').strip('.')
            
            # 🛠️ CAPTURA DE IP AVANZADA (Soporta IPv4 e IPv6)
            ip_origen = "Dispositivo WiFi"
            if paquete.haslayer('IP'):
                ip_origen = paquete['IP'].src  # Extrae IPv4 (ej: 192.168.137.45)
            elif paquete.haslayer('IPv6'):
                ip_origen = paquete['IPv6'].src  # Extrae IPv6 si el celular usa el protocolo moderno
            
            # Lista de palabras clave de Inteligencias Artificiales y sitios prohibidos
            lista_trampas = ["chatgpt", "gemini", "openai", "claude", "brainly", "wikipedia", "deepseek", "perplexities"]
            
            if any(trampa in dominio.lower() for trampa in lista_trampas):
                ahora = datetime.datetime.now().strftime("%H:%M:%S")
                
                # Preparamos el paquete de datos para la interfaz del profesor
                alerta = {
                    "hora": ahora,
                    "ip": ip_origen,
                    "dominio": dominio
                }
                print(f"🚨 [TRAMPA EN VIVO] Alumno ({ip_origen}) intentó ir a -> {dominio}")
                
                # Despachamos la alerta asíncrona hacia el panel por WebSockets
                if loop_principal:
                    asyncio.run_coroutine_threadsafe(enviar_alerta_trampa(alerta), loop_principal)
        except Exception:
            pass

def ejecutar_sniffer():
    """Arranca la escucha en la tarjeta inalámbrica sin bloquear la web."""
    print("📡 [VIGILNET] El interceptor inalámbrico está encendido y escuchando...")
    # Al no pasarle 'iface' (interfaz fija), Scapy captura el tráfico de CUALQUIER
    # adaptador activo, resolviendo el problema de las tarjetas virtuales del Hotspot.
    sniff(filter="udp port 53", prn=procesar_paquete, store=0)

@app.on_event("startup")
def arrancar_componentes():
    """Se ejecuta automáticamente cuando enciendes el servidor."""
    global loop_principal
    loop_principal = asyncio.get_event_loop()
    
    # Iniciamos el sniffer en un hilo separado para que no congele tu página web
    hilo_sniffer = threading.Thread(target=ejecutar_sniffer, daemon=True)
    hilo_sniffer.start()