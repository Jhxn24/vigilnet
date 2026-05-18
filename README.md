# VIGILNET 🛡️✈️
> **El guardián de la red portátil para exámenes libres de IA.**

VIGILNET es una herramienta construida en Python que transforma la laptop del docente en un punto de acceso WiFi controlado y portátil durante evaluaciones académicas. Sin requerir instalaciones en los dispositivos de los estudiantes, intercepta y registra en tiempo real los intentos de acceso a inteligencias artificiales y URLs externas no autorizadas.

---

## 🚀 Características Principales

* **Portabilidad Absoluta:** No depende de la infraestructura tecnológica o del router del colegio o universidad. El profesor activa la red desde su laptop en cualquier aula.
* **Cero Instalación para Alumnos:** Los estudiantes solo necesitan conectarse a la red WiFi generada desde sus laptops o smartphones.
* **Portal Cautivo de Identificación:** Al conectarse, el sistema exige obligatoriamente el nombre completo y el carné/matrícula del alumno para habilitar el acceso a la red del examen.
* **Monitoreo DNS en Tiempo Real:** Captura al vuelo las solicitudes dirigidas a dominios de IA (como ChatGPT o Gemini) antes de que el tráfico se cifre por HTTPS.
* **Panel del Docente Protegido:** Interfaz web local exclusiva para el profesor, accesible mediante contraseña, que muestra las alertas y actividades de trampa mediante actualizaciones dinámicas.

---

## 🛠️ Arquitectura del Sistema

El software se compone de tres capas modulares controladas en su totalidad por Python:

1.  **Capa de Red (Punto de Acceso):** Levanta el Hotspot inalámbrico y gestiona el Portal Cautivo de autenticación.
2.  **Capa de Filtrado (El Núcleo Sniffer):** Actúa como un servidor DNS local o analizador de paquetes que inspecciona las solicitudes de dominio salientes.
3.  **Capa Web (Panel de Control):** Backend ligero que procesa las alertas de navegación y las envía al panel del profesor mediante WebSockets.

---

## 🗺️ Plan de Desarrollo del Proyecto

El proyecto está estructurado para desarrollarse en 3 fases incrementales:

* **Fase 1: El Interceptor de Tráfico:** Script base en Python encargado del análisis de paquetes y la captura de solicitudes de dominios restringidos.
* **Fase 2: El Panel Web del Profesor:** Construcción de la interfaz de usuario en el backend (usando Flask o FastAPI) para centralizar y visualizar las alertas de trampa de forma ordenada.
* **Fase 3: La Red Portátil e Integración:** Configuración de las herramientas del sistema operativo para desplegar de forma automatizada el Punto de Acceso WiFi y el Portal Cautivo.

---

## 🔒 Desafíos Técnicos y Seguridad

* **Filtrado HTTPS:** Dado que la navegación web moderna está cifrada, VIGILNET se enfoca en interceptar las resoluciones de nombres (DNS), las cuales viajan en texto plano en redes tradicionales, permitiendo detectar con total precisión el destino del alumno (ej. `api.openai.com`).
* **Mitigación de VPNs:** El sistema incluye reglas de inspección para identificar e impedir el tráfico proveniente de protocolos de redes privadas virtuales comunes que intenten saltarse el punto de acceso controlado.

---
© 2026 VIGILNET - Soluciones Tecnológicas Educativas. Todos los derechos reservados.
