# 🚗 DriveMe Local - Sistema de Gestión de Archivos

**Framework:** Flask  
**Base de Datos:** SQLite  
**Sistema Operativo:** Ubuntu 24.04.3 LTS  
**Lenguaje Principal:** Python  
**Licencia:** Uso Académico  

---

## 👥 Información del Proyecto Académico

| Campo | Detalle |
|-------|----------|
| 📚 **Materia** | Modelos y Metodos Para el Desarolo de Software |
| 🏫 **Institución** | Universidad del Valle de México (UVM) |
| 👨‍🏫 **Docente** | Ernesto Gonzales Cardenas|
| 📅 **Fecha de entrega** | 14 de Noviembre de 2025 |
| 🧩 **Tarea** | Proyecto Examen Parcial 2 |
| 💻 **Carrera** | Ingeniería en Sistemas Computacionales |

---

## 👨‍💻 Equipo de Desarrollo

- **Leo Gael Cruz Castañeda**  
- **Sergio Gerardo Cárdenas Mendoza**  
- **Jorge Alberto Posadas Chavarría**

---

## 🧠 Descripción General

**DriveMe Local** es un sistema de almacenamiento y gestión de archivos desarrollado como proyecto académico.  
Permite a los usuarios **subir, visualizar y descargar archivos** dentro de una interfaz tipo *Google Drive local*, implementando una base de datos **SQLite** y un servidor **Flask** desplegado en **Ubuntu**.

El objetivo principal del proyecto es demostrar los fundamentos de **administración de bases de datos**, **gestión de usuarios**, y **manipulación de datos persistentes** en un entorno real.

---

## 🏗️ Arquitectura General del Sistema

| Capa | Tecnología | Descripción |
|------|-------------|--------------|
| **Frontend** | HTML5, CSS3, Bootstrap Icons | Interfaz visual con diseño responsivo |
| **Backend** | Python + Flask | Servidor que gestiona rutas, sesiones y peticiones |
| **Base de Datos** | SQLite3 | Sistema de almacenamiento embebido |
| **Sistema Operativo** | Ubuntu 24.04.3 LTS | Entorno de desarrollo Linux nativo |
| **Servidor Local** | Flask Server | Comunicación entre cliente y servidor local |
| **Seguridad** | Flask-Bcrypt y Flask-Login | Manejo de sesiones e inicio de sesión seguro |

---

## 🎯 Objetivos Académicos

Este proyecto tiene como propósito aplicar los siguientes conceptos:

- Normalización y gestión de tablas SQLite  
- Implementación de rutas y consultas SQL desde Flask  
- Validación de usuarios mediante sesiones seguras  
- Inserción, consulta, y actualización de datos  
- Conexión entre servidor, cliente y base de datos en entorno Linux  
- Buenas prácticas en estructura de carpetas, seguridad y despliegue local  

---

## 📁 Estructura del Proyecto — DriveMe.Local

```bash
DriveMe.Local/
│
├── app.py              # Aplicación principal Flask
├── database.db         # Base de datos SQLite
├── admin.py            # Módulo del panel de administración
│
├── static/
│   ├── css/
│   │   ├── style.css
│   │   └── admin.css
│   └── uploads/        # Archivos almacenados por usuarios
│
└── templates/
    ├── base.html
    ├── index.html
    ├── dashboard.html
    ├── login.html
    ├── register.html
    └── admin.html

---

## ⚙️ Funcionalidades Principales

| Módulo | Descripción |
|---------|-------------|
| 🔐 **Autenticación** | Inicio y cierre de sesión con Flask-Login |
| 📂 **Gestión de Archivos** | Subida, visualización y descarga desde SQLite |
| 🧮 **Panel de Administración** | Visualización de usuarios, archivos y logs |
| 💾 **Registro Automático** | Inserción de metadatos (`uploaded_by`, `uploaded_at`) |
| 📊 **Dashboard Interactivo** | Vista tipo Google Drive con íconos y cuadrícula |



## 🧰 Tecnologías y Dependencias

| Categoría | Tecnología |
|------------|------------|
| **Lenguaje** | Python 3.12 |
| **Framework Web** | Flask 3.x |
| **Base de Datos** | SQLite 3.45 |
| **Seguridad** | Flask-Bcrypt, Flask-Login |
| **Frontend** | HTML5, CSS3, Bootstrap Icons |
| **Servidor Local** | Werkzeug (integrado en Flask) |
| **Sistema Operativo** | Ubuntu 24.04.3 LTS |



## 🖥️ Entorno de Ejecución

Este proyecto fue desarrollado y probado en:

```bash
System: Ubuntu 24.04.3 LTS (Noble Numbat)
Kernel: 6.14.0-29-generic
CPU: Intel Core i7-1195G7 (11th Gen)
GPU: Intel Iris Xe Graphics
RAM: 16 GB
Storage: 1 TB SSD

🔄 Flujo de Trabajo

El usuario inicia sesión desde login.html.

Flask verifica credenciales en la tabla users de database.db.

Una vez autenticado, el usuario accede a su dashboard tipo Drive.

Los archivos subidos se registran en la tabla files con metadatos.

El panel de administración permite revisar usuarios y archivos.



📚 Competencias Desarrolladas

Administración de Bases de Datos Relacionales

Integración Backend–Frontend

Manejo de sesiones y autenticación

Estructuración y documentación técnica

Desarrollo en entorno Linux (Ubuntu)

Despliegue local con Flask


🌐 Conclusión Académica

DriveMe Local demuestra cómo una arquitectura sencilla puede representar los fundamentos de un sistema de información completo, integrando interfaz gráfica, lógica del servidor y persistencia de datos.
El desarrollo permitió aplicar conocimientos de SQL, administración de bases de datos y prácticas seguras de desarrollo en Python.

© 2025 Universidad del Valle de México
Proyecto académico sin fines comerciales.
