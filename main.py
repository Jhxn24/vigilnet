import asyncio
import datetime
import os
import threading
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from sniffer import iniciar_interceptor


BASE_DIR = Path(__file__).resolve().parent
PANEL_TOKEN = os.getenv("VIGILNET_PANEL_TOKEN", "vigilnet-docente")
SNIFFER_IFACE = os.getenv("VIGILNET_IFACE")

app = FastAPI(title="VIGILNET", version="1.0.0")

loop_principal: asyncio.AbstractEventLoop | None = None
conexiones_profesor: set[WebSocket] = set()
alumnos_registrados: dict[str, dict[str, str]] = {}
alertas: dict[str, dict[str, str]] = {}


class RegistroAlumno(BaseModel):
    nombre: str = Field(min_length=3, max_length=80)
    codigo: str = Field(min_length=2, max_length=40)


def ahora() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")


def validar_token(token: str | None) -> None:
    if token != PANEL_TOKEN:
        raise HTTPException(status_code=401, detail="Token docente invalido")


def leer_index() -> HTMLResponse:
    index_path = BASE_DIR / "index.html"
    return HTMLResponse(index_path.read_text(encoding="utf-8"))


def buscar_alumno(ip: str) -> dict[str, str]:
    if ip in alumnos_registrados:
        return alumnos_registrados[ip]

    if len(alumnos_registrados) == 1:
        alumno = next(iter(alumnos_registrados.values()))
        return {
            **alumno,
            "ip": ip,
        }

    return alumnos_registrados.get(
        ip,
        {
            "nombre": "Alumno no identificado",
            "codigo": "Sin registro",
            "ip": ip,
        },
    )


@app.get("/", response_class=HTMLResponse)
async def portal_alumno() -> HTMLResponse:
    return leer_index()


@app.get("/panel", response_class=HTMLResponse)
async def panel_docente(token: str | None = Query(default=None)) -> HTMLResponse:
    validar_token(token)
    return leer_index()


@app.post("/api/alumnos")
async def registrar_alumno_http(
    request: Request,
    registro: RegistroAlumno,
    client_ip: str | None = Query(default=None),
):
    ip = client_ip or (request.client.host if request.client else "IP pendiente")
    alumno = {
        "nombre": registro.nombre.strip(),
        "codigo": registro.codigo.strip(),
        "ip": ip,
        "hora": ahora(),
    }
    alumnos_registrados[ip] = alumno
    await enviar_evento_profesor({"tipo": "alumno", "alumno": alumno})
    await actualizar_alertas_de_alumno(alumno)
    return {"ok": True, "alumno": alumno}


@app.get("/api/estado")
async def obtener_estado(token: str | None = Query(default=None)):
    validar_token(token)
    return {
        "alumnos": list(alumnos_registrados.values()),
        "alertas": list(alertas.values())[-100:],
        "total_alertas": len(alertas),
    }


@app.get("/simular")
async def simular_trampa(token: str | None = Query(default=None)):
    validar_token(token)
    alerta = crear_alerta("192.168.137.50", "chatgpt.com", "simulacion")
    await enviar_alerta_trampa(alerta)
    return {"ok": True, "alerta": alerta}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str | None = Query(default=None)):
    if token != PANEL_TOKEN:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    conexiones_profesor.add(websocket)
    print("[VIGILNET] Panel docente conectado.")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        conexiones_profesor.discard(websocket)
        print("[VIGILNET] Panel docente desconectado.")


def crear_alerta(ip: str, dominio: str, origen: str = "dns") -> dict[str, str]:
    alumno = buscar_alumno(ip)
    return {
        "id": f"{ip}|{dominio}".lower(),
        "hora": ahora(),
        "ip": ip,
        "nombre": alumno["nombre"],
        "codigo": alumno["codigo"],
        "dominio": dominio,
        "origen": origen,
        "conteo": "1",
    }


async def enviar_alerta_trampa(datos_alerta: dict[str, Any]):
    alerta_entrante = {clave: str(valor) for clave, valor in datos_alerta.items()}
    alerta_id = alerta_entrante.get(
        "id",
        f"{alerta_entrante.get('ip', '')}|{alerta_entrante.get('dominio', '')}".lower(),
    )

    if alerta_id in alertas:
        alerta = alertas[alerta_id]
        alerta["hora"] = alerta_entrante["hora"]
        alerta["conteo"] = str(int(alerta.get("conteo", "1")) + 1)
    else:
        alerta = alerta_entrante
        alerta["id"] = alerta_id
        alerta["conteo"] = alerta.get("conteo", "1")
        alertas[alerta_id] = alerta

    if len(alertas) > 500:
        for clave in list(alertas.keys())[:-500]:
            del alertas[clave]

    await enviar_evento_profesor({"tipo": "alerta", "alerta": alerta})


async def enviar_evento_profesor(evento: dict[str, Any]):
    desconectados: list[WebSocket] = []
    for conexion in conexiones_profesor:
        try:
            await conexion.send_json(evento)
        except Exception:
            desconectados.append(conexion)

    for conexion in desconectados:
        conexiones_profesor.discard(conexion)


async def actualizar_alertas_de_alumno(alumno: dict[str, str]):
    for alerta in alertas.values():
        if alerta.get("ip") != alumno["ip"]:
            continue

        alerta["nombre"] = alumno["nombre"]
        alerta["codigo"] = alumno["codigo"]
        await enviar_evento_profesor({"tipo": "alerta", "alerta": alerta})


def manejar_deteccion(ip: str, dominio: str):
    if loop_principal is None:
        return
    alerta = crear_alerta(ip, dominio)
    print(f"[VIGILNET] Alerta: {alerta['nombre']} ({ip}) intento abrir {dominio}")
    asyncio.run_coroutine_threadsafe(enviar_alerta_trampa(alerta), loop_principal)


@app.on_event("startup")
async def arrancar_componentes():
    global loop_principal
    loop_principal = asyncio.get_running_loop()
    hilo_sniffer = threading.Thread(
        target=iniciar_interceptor,
        kwargs={"callback": manejar_deteccion, "interfaz": SNIFFER_IFACE},
        daemon=True,
    )
    hilo_sniffer.start()
    print("[VIGILNET] Servidor iniciado.")
    print(f"[VIGILNET] Interfaz de captura: {SNIFFER_IFACE or 'automatica'}")
    print(f"[VIGILNET] Panel docente: http://localhost:8000/panel?token={PANEL_TOKEN}")
