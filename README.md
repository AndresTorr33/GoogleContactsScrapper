# 📧 Google Contacts UTEC — Email Scraper

Herramienta para extraer correos electrónicos del directorio institucional de UTEC usando la **Google People API**, con filtrado inteligente por rol (alumnos) y agrupación por carrera.

Basado en el proyecto original de [aryanranderiya/GoogleContactsEmailScraper](https://github.com/aryanranderiya/GoogleContactsEmailScraper).

---

## ¿Qué hace?

- Se conecta al directorio de Google Workspace de UTEC via OAuth 2.0.
- Filtra únicamente correos con formato de alumno (`nombre.apellido@utec.edu.pe`).
- Ofrece dos modos de salida:

| Script | Salida |
|---|---|
| `app_nuevo.py` | Un `.txt` por carrera (`estudiantes_INGENIERIA_SISTEMAS.txt`, etc.) |
| `full_correos_alumnos.py` | Un solo archivo `todos_los_alumnos_utec.txt` con todos los alumnos |

---

## Requisitos previos

### 1. Proyecto en Google Cloud Console

Necesitas crear un proyecto con OAuth 2.0 y habilitar la **People API**:

1. Ve a [console.cloud.google.com](https://console.cloud.google.com/)
2. Crea un proyecto nuevo.
3. Habilita la **Google People API**.
4. En **Credenciales**, crea una credencial **OAuth 2.0 → Aplicación de escritorio**.
5. Descarga el archivo y renómbralo a `credentials.json`.
6. Colócalo en la raíz del proyecto.

Los scopes necesarios son:
- `https://www.googleapis.com/auth/contacts.readonly`
- `https://www.googleapis.com/auth/directory.readonly`

> **Nota:** Para usar `directory.readonly` necesitas una cuenta de Google Workspace (no cuenta personal).

---

## Instalación

```bash
# 1. Clona el repositorio
git clone https://github.com/TU_USUARIO/GoogleContactsUTEC.git
cd GoogleContactsUTEC

# 2. Crea y activa el entorno virtual
python -m venv venv
.\venv\Scripts\activate      # Windows
# source venv/bin/activate   # Mac / Linux

# 3. Instala las dependencias
pip install -r requirements.txt
```

---

## Uso

```bash
# Opción A: Un .txt por carrera
python app_nuevo.py

# Opción B: Un solo archivo con todos los alumnos
python full_correos_alumnos.py
```

La **primera vez** que ejecutes el script se abrirá el navegador para autenticarte con tu cuenta de Google. Después se creará un archivo `token.json` local que se reutiliza en ejecuciones futuras.

---

## Estructura del proyecto

```
GoogleContactsUTEC/
├── app_nuevo.py              # Extrae correos separados por carrera
├── full_correos_alumnos.py   # Extrae todos los alumnos en un solo archivo
├── requirements.txt          # Dependencias de Python
├── .gitignore                # Excluye credentials.json, token.json y *.txt
└── README.md
```

> `credentials.json` y `token.json` están en `.gitignore` por seguridad — **nunca los subas al repositorio**.

---

## ¿Usas otra universidad?

Solo necesitas cambiar **2 cosas** en `app_nuevo.py`:

1. **El dominio** (línea 14) — reemplaza `utec\.edu\.pe` por el de tu universidad:
   ```python
   # Antes (UTEC):
   patron_alumno = re.compile(r"^[a-z0-9_-]+\.[a-z0-9_.-]+@utec\.edu\.pe$")

   # Ejemplo para PUCP:
   patron_alumno = re.compile(r"^[a-z0-9_-]+\.[a-z0-9_.-]+@pucp\.edu\.pe$")
   ```

2. **El patrón del correo** — si en tu universidad el formato de alumno no es `nombre.apellido@universidad.edu`, ajusta el regex. Por ejemplo, si usan `a20201234@universidad.edu`:
   ```python
   patron_alumno = re.compile(r"^a\d+@universidad\.edu\.pe$")
   ```

El resto del script (autenticación, paginación, separación por carrera) funciona igual para cualquier Google Workspace universitario.

---

## Créditos

- Proyecto original: [aryanranderiya/GoogleContactsEmailScraper](https://github.com/aryanranderiya/GoogleContactsEmailScraper)
- Adaptación para UTEC: filtrado por dominio institucional, separación por carrera y normalización de nombres con tildes.
