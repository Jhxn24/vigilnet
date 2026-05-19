import json
import datetime
from scapy.all import sniff, DNS, DNSQR

def cargar_dominios_negros():
    """
    Lee el archivo JSON externo y extrae la lista de dominios a monitorear.
    """
    try:
        with open("dominios_ia.json", "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
            print(f"[VIGILNET] Se cargaron {len(datos['dominios'])} dominios de la lista negra.")
            return datos["dominios"]
    except FileNotFoundError:
        print("[ERROR] No se encontró el archivo 'dominios_ia.json'. Usando lista de emergencia por defecto.")
        # Lista de respaldo por si el archivo llega a borrarse por accidente
        return ["chatgpt.com", "openai.com", "gemini.google.com"]
    except Exception as e:
        print(f"[ERROR] Hubo un problema al leer el archivo JSON: {e}")
        return []

# Cargamos la lista al iniciar el script
DOMINIOS_IA = cargar_dominios_negros()

# Importamos el conector web para enviar la alerta
import asyncio
from main import enviar_alerta_trampa

def procesar_paquete(packet):
    if packet.haslayer(DNS) and packet[DNS].opcode == 0 and packet.haslayer(DNSQR):
        try:
            qname = packet[DNSQR].qname.decode('utf-8').strip('.')
            ip_origen = packet['IP'].src if packet.haslayer('IP') else "IP Desconocida"
            
            for dominio in DOMINIOS_IA:
                if dominio in qname:
                    ahora = datetime.datetime.now().strftime("%H:%M:%S")
                    
                    # Estructuramos la alerta para el panel del docente
                    alerta = {
                        "hora": ahora,
                        "ip": ip_origen,
                        "dominio": qname
                    }
                    
                    # Enviamos la alerta de forma asíncrona al servidor web
                    try:
                        asyncio.run_coroutine_threadsafe(enviar_alerta_trampa(alerta), loop_principal)
                    except Exception:
                        pass
                    break
        except Exception:
            pass

# Variable global para coordinar los hilos de red y web
loop_principal = None

def iniciar_interceptor(loop, interfaz=None):
    global loop_principal
    loop_principal = loop
    print("🛡️ [VIGILNET] Núcleo interceptor sincronizado con el servidor web.")
    sniff(filter="udp port 53", prn=procesar_paquete, store=0, iface=interfaz)