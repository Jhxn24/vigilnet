# VIGILNET 🛡️✈️

> **El guardián de la red portátil para exámenes libres de IA.**

VIGILNET es una herramienta construida en Python que transforma la laptop del docente en un punto de acceso WiFi controlado y portátil durante evaluaciones académicas. Sin requerir instalaciones en los dispositivos de los estudiantes, intercepta y registra en tiempo real los intentos de acceso a inteligencias artificiales y URLs externas no autorizadas.

---

## 🚀 Características Principales

- **Portabilidad Absoluta:** No depende de la infraestructura tecnológica o del router del colegio o universidad. El profesor activa la red desde su laptop en cualquier aula.
- **Cero Instalación para Alumnos:** Los estudiantes solo necesitan conectarse a la red WiFi generada desde sus laptops o smartphones.
- **Portal Cautivo de Identificación:** Al conectarse, el sistema exige obligatoriamente el nombre completo y el carné/matrícula del alumno para habilitar el acceso a la red del examen.
- **Monitoreo DNS en Tiempo Real:** Captura al vuelo las solicitudes dirigidas a dominios de IA (como ChatGPT o Gemini) antes de que el tráfico se cifre por HTTPS.
- **Panel del Docente Protegido:** Interfaz web local exclusiva para el profesor, accesible mediante contraseña, que muestra las alertas y actividades de trampa mediante actualizaciones dinámicas.

---

## 🛠️ Arquitectura del Sistema

El software se compone de tres capas modulares controladas en su totalidad por Python:

1.  **Capa de Red (Punto de Acceso):** Levanta el Hotspot inalámbrico y gestiona el Portal Cautivo de autenticación.
2.  **Capa de Filtrado (El Núcleo Sniffer):** Actúa como un servidor DNS local o analizador de paquetes que inspecciona las solicitudes de dominio salientes.
3.  **Capa Web (Panel de Control):** Backend ligero que procesa las alertas de navegación y las envía al panel del profesor mediante WebSockets.

---

## 🗺️ Plan de Desarrollo del Proyecto

El proyecto está estructurado para desarrollarse en 3 fases incrementales:

- **Fase 1: El Interceptor de Tráfico:** Script base en Python encargado del análisis de paquetes y la captura de solicitudes de dominios restringidos.
- **Fase 2: El Panel Web del Profesor:** Construcción de la interfaz de usuario en el backend (usando Flask o FastAPI) para centralizar y visualizar las alertas de trampa de forma ordenada.
- **Fase 3: La Red Portátil e Integración:** Configuración de las herramientas del sistema operativo para desplegar de forma automatizada el Punto de Acceso WiFi y el Portal Cautivo.

---

📦 Librerías y Dependencias del Entorno
El proyecto utiliza un conjunto específico de herramientas de alto rendimiento para la web asíncrona y la manipulación de paquetes. Asegúrate de tener instalado lo siguiente:

1. Requisitos de Software Base
   Python 3.10 o superior: Lenguaje de programación principal del ecosistema.

Npcap (Crítico para entornos Windows): Debe descargarse e instalarse obligatoriamente desde npcap.com habilitando de forma estricta la casilla de verificación "Install Npcap in WinPcap API-compatible Mode". Sin este driver, Python no podrá capturar ni interpretar el tráfico inalámbrico.

2. Librerías de Python
   fastapi: Framework web moderno y rápido para construir la API y gestionar la lógica de backend.

uvicorn[standard]: Servidor ASGI de alta velocidad encargado de levantar la aplicación web y dar soporte nativo a WebSockets.

scapy: Potente librería de manipulación e interactividad con paquetes de red para auditar el tráfico en tiempo real.

Para instalar todas las librerías de Python en un solo comando, ejecuta en tu terminal:

**pip install fastapi "uvicorn[standard]" scapy**

## ⚙️Configuración Previa a la Ejecución (Puesta a Punto de la Red)

Encender el Hotspot de Windows: \* Ve a Configuración de Windows > Red e Internet > Zona con cobertura inalámbrica móvil y activa el interruptor.

Entra a "Editar propiedades" y fuerza la banda de red a 2.4 GHz para asegurar la compatibilidad con cualquier dispositivo móvil (muchos smartphones no detectan la banda de 5 GHz).

## 💻 Pasos Exactos para Ejecutar el Proyecto

1. Abrir la terminal como Administrador
   Dado que la librería scapy requiere permisos del sistema de bajo nivel para auditar los adaptadores de red, abre tu terminal de comandos (o VS Code) haciendo clic derecho y seleccionando "Ejecutar como Administrador".
2. Iniciar el Servidor Maestro
   Ejecuta el siguiente comando para encender el servidor web y activar automáticamente el hilo del interceptor inalámbrico:
   **uvicorn main:app --reload**

## 🧪 Métodos de Prueba y Validación

El sistema cuenta con dos metodologías para verificar que las alertas se transmitan correctamente:

**Método A:** Prueba en Vivo (Con Dispositivo Físico)
Conecta un celular al WiFi emitido por tu laptop (JHONPC 0762 o el nombre que hayas configurado).

Abre el navegador del celular en Modo Incógnito (es crucial para evitar que el teléfono use una copia guardada de la página en caché).

Intenta navegar a chatgpt.com o gemini.google.com.

El panel web en la laptop registrará la trampa de inmediato desplegando una fila roja parpadeante.

**Método B:** Modo de Simulación (Por Software)
Si deseas comprobar el correcto funcionamiento de los WebSockets y la interfaz de usuario sin necesidad de conectar un dispositivo físico, abre una pestaña en tu navegador web e ingresa a:
**http://localhost:8000/simular**

---

© 2026 VIGILNET - Soluciones Tecnológicas Educativas. Todos los derechos reservados.
