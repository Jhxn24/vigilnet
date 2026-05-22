# VIGILNET

VIGILNET es una herramienta local para apoyar evaluaciones presenciales. La laptop del docente funciona como punto de control: muestra un portal de identificacion para estudiantes, registra alumnos conectados y alerta en tiempo real cuando detecta consultas DNS hacia dominios de IA o sitios restringidos.

## Que incluye esta version

- Portal de alumno para registrar nombre y codigo universitario.
- Panel docente protegido por token.
- Listado en vivo de alumnos logueados.
- Alertas DNS en vivo por WebSocket.
- Conteo de intentos repetidos por alumno/IP y dominio, sin llenar la tabla con filas duplicadas.
- Lista configurable de dominios restringidos en `dominios_ia.json`.
- Filtro para ignorar IPv6 link-local (`fe80::...`) y reducir ruido.
- Ruta de simulacion para probar el panel sin trafico real.

Todavia no automatiza por completo el hotspot de Windows ni implementa un portal cautivo real a nivel de sistema operativo. El hotspot se activa manualmente desde Windows.

## Requisitos

- Windows.
- Python 3.10 o superior.
- Npcap instalado con la opcion `Install Npcap in WinPcap API-compatible Mode`.
- PowerShell o terminal ejecutada como administrador.

## Instalacion

Desde la carpeta del proyecto:

```powershell
python -m pip install -r requirements.txt
```

## Ejecucion recomendada para aula

1. Activa la zona WiFi movil de Windows.
2. Conecta los celulares o laptops de alumnos al hotspot.
3. Abre PowerShell como administrador.
4. Ejecuta:

```powershell
cd C:\Users\ashla\Documents\Codex\2026-05-22\podrias-analizar-esta-repo-que-estamos\vigilnet
python -m pip install -r requirements.txt
$env:VIGILNET_IFACE="Local Area Connection* 2"
$env:VIGILNET_HOTSPOT_PREFIX="192.168.137."
python -m uvicorn main:app --reload --host 0.0.0.0
```

En tu caso, segun `ipconfig`, el hotspot usa:

```text
192.168.137.1
```

## URLs

Panel docente en la laptop:

```text
http://localhost:8000/panel?token=vigilnet-docente
```

Portal para alumnos conectados al hotspot:

```text
http://192.168.137.1:8000/
```

Simular alerta desde la laptop:

```text
http://localhost:8000/simular?token=vigilnet-docente
```

## Token docente

El token por defecto es:

```text
vigilnet-docente
```

Para cambiarlo:

```powershell
$env:VIGILNET_PANEL_TOKEN="mi-token-seguro"
python -m uvicorn main:app --reload --host 0.0.0.0
```

## Variables utiles

`VIGILNET_IFACE`

Define la interfaz que Scapy debe capturar. En Windows, el hotspot suele aparecer como:

```powershell
$env:VIGILNET_IFACE="Local Area Connection* 2"
```

`VIGILNET_HOTSPOT_PREFIX`

Filtra alertas para tomar solo dispositivos del hotspot. Para Windows normalmente es:

```powershell
$env:VIGILNET_HOTSPOT_PREFIX="192.168.137."
```

Si quieres capturar cualquier IP, dejalo vacio:

```powershell
$env:VIGILNET_HOTSPOT_PREFIX=""
```

`VIGILNET_IGNORE_IPV6_LINK_LOCAL`

Por defecto ignora IPs `fe80::...` para evitar duplicados. Para desactivar ese filtro:

```powershell
$env:VIGILNET_IGNORE_IPV6_LINK_LOCAL="0"
```

## Flujo de uso

1. El docente activa el hotspot de Windows.
2. El docente inicia VIGILNET como administrador.
3. Cada alumno abre `http://192.168.137.1:8000/`.
4. El alumno registra nombre y codigo universitario.
5. El docente abre el panel.
6. Si un alumno consulta un dominio restringido por DNS clasico, aparece una alerta.
7. Si el mismo alumno repite el mismo dominio, se actualiza el conteo en una sola fila.

## Notas para aulas grandes

- El panel agrupa alertas por IP y dominio para evitar acumulacion masiva de filas.
- El contador muestra el total de intentos, aunque la tabla muestre una fila por combinacion IP/dominio.
- Para 30 o mas alumnos, usa `VIGILNET_HOTSPOT_PREFIX="192.168.137."` para evitar capturar trafico externo a la red del examen.
- Si una alerta aparece antes de que el alumno se registre, al registrarse se actualiza con su nombre y codigo si la IP coincide.

## Limitaciones importantes

VIGILNET monitorea DNS clasico en UDP/53. No puede garantizar deteccion si el alumno usa VPN, datos moviles, DNS-over-HTTPS, DNS-over-TLS, cache DNS, navegadores con resolucion privada o aplicaciones que no consultan el DNS del sistema.

Para un control mas fuerte, los siguientes pasos serian integrar configuracion de red, bloqueo de DoH y un portal cautivo real.

## Estructura

- `main.py`: servidor FastAPI, portal, panel, WebSocket y estado en memoria.
- `sniffer.py`: captura DNS y dispara alertas al backend.
- `index.html`: interfaz autocontenida para alumnos y docente.
- `dominios_ia.json`: dominios restringidos.
- `requirements.txt`: dependencias Python.
