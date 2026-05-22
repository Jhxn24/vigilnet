import json
import os
from pathlib import Path
from typing import Callable

from scapy.all import DNS, DNSQR, sniff


BASE_DIR = Path(__file__).resolve().parent
DOMINIOS_PATH = BASE_DIR / "dominios_ia.json"
DominioDetectadoCallback = Callable[[str, str], None]
PREFIJO_HOTSPOT = os.getenv("VIGILNET_HOTSPOT_PREFIX", "")
IGNORAR_IPV6_LOCAL = os.getenv("VIGILNET_IGNORE_IPV6_LINK_LOCAL", "1") == "1"


def cargar_dominios() -> list[str]:
    try:
        datos = json.loads(DOMINIOS_PATH.read_text(encoding="utf-8"))
        dominios = datos.get("dominios", [])
        return [dominio.lower().strip() for dominio in dominios if dominio.strip()]
    except FileNotFoundError:
        print("[VIGILNET] No se encontro dominios_ia.json. Usando lista minima.")
        return ["chatgpt.com", "openai.com", "gemini.google.com"]
    except Exception as exc:
        print(f"[VIGILNET] No se pudo leer la lista de dominios: {exc}")
        return []


def obtener_ip_origen(paquete) -> str:
    if paquete.haslayer("IP"):
        return paquete["IP"].src
    if paquete.haslayer("IPv6"):
        return paquete["IPv6"].src
    return "IP desconocida"


def dominio_bloqueado(qname: str, dominios: list[str]) -> bool:
    dominio = qname.lower().strip(".")
    return any(dominio == item or dominio.endswith(f".{item}") for item in dominios)


def ip_monitoreada(ip: str) -> bool:
    if IGNORAR_IPV6_LOCAL and ip.lower().startswith("fe80:"):
        return False
    if not PREFIJO_HOTSPOT:
        return True
    return ip.startswith(PREFIJO_HOTSPOT)


def crear_procesador(callback: DominioDetectadoCallback, dominios: list[str]):
    def procesar_paquete(paquete):
        if not paquete.haslayer(DNS) or not paquete.haslayer(DNSQR):
            return
        if paquete[DNS].qr != 0:
            return

        try:
            qname = paquete[DNSQR].qname.decode("utf-8", errors="ignore").strip(".")
            ip_origen = obtener_ip_origen(paquete)
            if ip_monitoreada(ip_origen) and dominio_bloqueado(qname, dominios):
                callback(ip_origen, qname)
        except Exception as exc:
            print(f"[VIGILNET] Error procesando paquete DNS: {exc}")

    return procesar_paquete


def iniciar_interceptor(callback: DominioDetectadoCallback, interfaz: str | None = None):
    dominios = cargar_dominios()
    print(f"[VIGILNET] Monitoreando {len(dominios)} dominios restringidos.")
    print(f"[VIGILNET] Monitoreando IPs que empiecen con: {PREFIJO_HOTSPOT or 'cualquier IP'}")
    print(f"[VIGILNET] Ignorar IPv6 link-local: {'si' if IGNORAR_IPV6_LOCAL else 'no'}")
    print("[VIGILNET] Sniffer DNS activo en UDP/53.")
    try:
        sniff(
            filter="udp port 53",
            prn=crear_procesador(callback, dominios),
            store=0,
            iface=interfaz,
        )
    except Exception as exc:
        print(f"[VIGILNET] No se pudo iniciar el sniffer DNS: {exc}")
