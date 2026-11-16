from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os.path
import re
import unicodedata

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/contacts.readonly",
          "https://www.googleapis.com/auth/directory.readonly"]

# Patrón estricto para correos de alumnos
patron_alumno = re.compile(r"^[a-z0-9_-]+\.[a-z0-9_.-]+@utec\.edu\.pe$")

def wrap_error(func):
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e)
    return func_wrapper

def normalizar_carrera(texto):
    """Quita tildes, eñes, pasa a mayúsculas y cambia espacios por guiones bajos."""
    # Eliminar tildes y caracteres especiales
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    # Convertir a mayúsculas y dejar solo alfanuméricos
    limpio = "".join(c if c.isalnum() else "_" for c in texto.upper())
    # Limpiar guiones bajos múltiples
    limpio = re.sub(r'_+', '_', limpio).strip('_')
    return limpio if limpio else "SIN_CARRERA"

def authenticate() -> None:
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        print("User not authenticated... Authentication flow Started...")
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=8080)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    if creds.valid:
        print("User authenticated")

    try:
        service = build("people", "v1", credentials=creds)
        fetch_directory_contacts(service)
    except Exception as err:
        print("Error: ", err)

@wrap_error
def fetch_directory_contacts(service) -> None:
    finished: bool = False
    next_page_token: str = None
    
    data_dict: dict = {} 
    count: int = 0

    print("Fetching Directory Contacts...", end='\r')

    while not finished:
        results = service.people().listDirectoryPeople(
            readMask='names,emailAddresses,organizations',
            pageSize=1000,
            sources="DIRECTORY_SOURCE_TYPE_DOMAIN_PROFILE",
            pageToken=next_page_token,
        ).execute()

        result = results.get('people', [])
        count += len(result)
        print(f"Fetching Directory Contacts {count}...", end='\r')

        for person in result:
            emailAddresses: list = person.get("emailAddresses", [])
            orgs: list = person.get("organizations", [])
            
            carrera = "SIN_CARRERA"
            if orgs:
                carrera = orgs[0].get("department", orgs[0].get("title", "SIN_CARRERA"))
            
            # Normalizamos el nombre (ej. "IngenierÃa Mecánica" -> "INGENIERIA_MECANICA")
            carrera_limpia = normalizar_carrera(carrera)
            
            if emailAddresses:
                for email_data in emailAddresses:
                    email = email_data['value'].strip().lower()
                    
                    if patron_alumno.match(email) and "." in email.split("@")[0]:
                        if carrera_limpia not in data_dict:
                            data_dict[carrera_limpia] = set()
                        data_dict[carrera_limpia].add(email)

        next_page_token = results.get('nextPageToken')
        finished = not next_page_token

    write_directory_file(data_dict)

def perform_write(lista: list, filename: str) -> None:
    if lista:
        with open(filename, "w", encoding="utf-8") as file:
            for data in lista:
                file.write(data + "\n")
        print(f"{filename} Successfully Written! ({len(lista)} correos)")

def write_directory_file(data_dict: dict) -> None:
    if not data_dict:
        print("\nNo Directory Exists or no valid student emails found!")
        return

    print("\n\nSeparando correos por carrera...")
    
    # Guardado secuencial (sin hilos) para evitar choques en el disco duro
    for carrera, emails_set in data_dict.items():
        data: list = sorted(emails_set)
        filename = f"estudiantes_{carrera}.txt"
        perform_write(data, filename)

if __name__ == "__main__":
    authenticate()