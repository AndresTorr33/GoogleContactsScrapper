from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os.path
import re

# Permisos requeridos
SCOPES = ["https://www.googleapis.com/auth/contacts.readonly",
          "https://www.googleapis.com/auth/directory.readonly"]

# Patrón estricto para asegurar que solo entren alumnos
patron_alumno = re.compile(r"^[a-z0-9_-]+\.[a-z0-9_.-]+@utec\.edu\.pe$")

def wrap_error(func):
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e)
    return func_wrapper

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
    
    # Un solo set maestro para toda la universidad
    todos_los_alumnos: set = set()
    count: int = 0

    print("Fetching Directory Contacts...", end='\r')

    while not finished:
        # Petición optimizada (sin organizations) para mayor velocidad
        results = service.people().listDirectoryPeople(
            readMask='names,emailAddresses',
            pageSize=1000,
            sources="DIRECTORY_SOURCE_TYPE_DOMAIN_PROFILE",
            pageToken=next_page_token,
        ).execute()

        result = results.get('people', [])
        count += len(result)
        print(f"Fetching Directory Contacts {count}...", end='\r')

        for person in result:
            emailAddresses: list = person.get("emailAddresses", [])
            
            if emailAddresses:
                for email_data in emailAddresses:
                    email = email_data['value'].strip().lower()
                    
                    # Filtro de alumnos actuando como guardián
                    if patron_alumno.match(email) and "." in email.split("@")[0]:
                        todos_los_alumnos.add(email)

        next_page_token = results.get('nextPageToken')
        finished = not next_page_token

    write_directory_file(todos_los_alumnos)

def write_directory_file(data_set: set) -> None:
    if not data_set:
        print("\nNo Directory Exists or no valid student emails found!")
        return

    filename = "todos_los_alumnos_utec.txt"
    data: list = sorted(data_set)
    
    print("\n\nGuardando la base de datos maestra...")
    
    with open(filename, "w", encoding="utf-8") as file:
        for data_item in data:
            file.write(data_item + "\n")
            
    print(f"\n¡Éxito total! {filename} guardado exitosamente. ({len(data)} correos listos para la campaña)")

if __name__ == "__main__":
    authenticate()