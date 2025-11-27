import subprocess
import sys
import colorama
import os
import shutil
import requests
import time
from colorama import Fore, Style, init
import zipfile
import rarfile


#primera parte para instalar las dependencias
def clear():
    os.system("cls" if os.name == "nt" else "clear")


#funcion para controlar como administra los archivos pyinstaller
def get_app_directory():
    if getattr(sys, 'frozen', False):
        # Ejecutable compilado
        return os.path.dirname(sys.executable)
    else:
        # Script de Python
        return os.path.dirname(os.path.abspath(__file__))

def aptupdate(package_manager):
    
    print(f"{Fore.RED}¿Desea Acutalizar el sistema de repositorios? si tiene paquetes Desactualizado puede que TSA no funcione. puede tomar un rato\n")
    userinput = input("Y/N: ")
    
    if userinput.lower() in ["y", "yes", "s", "si"]:
        subprocess.run(['sudo', package_manager, 'update', "-y"], check=True)
            

def instalar_dependencias():

    init(autoreset=True)
    # Si está compilado con PyInstaller, cambia el working directory
    # al directorio donde está el EXE (no _MEIPASS)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    FLAG_FILE = "archivo.txt"
    if os.path.exists(FLAG_FILE): 
        return
    elif os.path.exists('/usr/bin/apt-get'):
        package_manager = 'apt-get'
    elif os.path.exists('/usr/bin/yum'):
        package_manager = 'yum'
    elif os.path.exists('/usr/bin/dnf'):
        package_manager = 'dnf'
    else:
        raise EnvironmentError("No se encontró un gestor de paquetes compatible.")
    

        # Detecta el gestor de paquetes adecuado
    try:
        if package_manager == 'apt-get':
            # Comandos para distribuciones basadas en Debian/Ubuntu
            aptupdate(package_manager)
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'unrar'], check=True)
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'tmux'], check=True)
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'rar'], check=True)
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'syncthing'], check=True)
            

            print(Fore.RED + "\npaquetes de sistema instalados")
            return
            

                 

        elif package_manager in ['yum', 'dnf']:
            aptupdate(package_manager)
            # Comandos para distribuciones basadas en Red Hat (CentOS, RHEL, Rocky)
            subprocess.run(['sudo', package_manager, 'update', '-y'], check=True)
            subprocess.run(['sudo', package_manager, 'install', '-y', 'unrar'], check=True)
            subprocess.run(['sudo', package_manager, 'install', '-y', 'tmux'], check=True)
            subprocess.run(['sudo', package_manager, 'install', '-y', 'rar'], check=True)
            print(Fore.RED + "\npaquetes de sistema instalados")

        # Comandos comunes (independientes del gestor de paquetes)
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip', '--break-system-packages'], check=True)
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'rarfile', '--break-system-packages'], check=True)
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'rarfile', '--break-system-packages'], check=True)
        print(Fore.RED + "\npaquetes de python instalados")


        # Imprimir mensaje en color rojo
        print(Fore.GREEN + "\nDependencias instaladas, ya puedes ejecutar el server.py")
        print(Style.RESET_ALL)

    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Error al ejecutar el comando: {e.cmd}")
        print(f"Código de salida: {e.returncode}")
        print(Style.RESET_ALL)

   
# Inicializa colorama

# Definición de colores para el efecto arcoíris
colores = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA, Fore.RED]


# Función para imprimir el título ASCII con efecto arcoíris
def efecto_arcoiris(titulo_ascii):
    for _ in range(1):  # Muestra el efecto arcoíris 1 vez
        for color in colores:
            clear()
            print(color + titulo_ascii)
            time.sleep(0.2)  # Controla la velocidad del cambio de color




def cerrar_serveo():
    clear()
    try:
        subprocess.run(["tmux", "kill-session","-t","ngrok_session"], check=True)
        print("Se ha cerrado la sesion de ngrok")

    except subprocess.CalledProcessError as e:
        # Si el comando devuelve un error
        print(f"\n{Fore.RED}Nunca iniciaste ngrok")
        time.sleep(3)
    
    interfaz()


# Función para agregar el repositorio de Tailscale
def agregar_repositorio_tailscale():
    try:
        subprocess.run(
            "curl -fsSL https://tailscale.com/install.sh | sh", check=True, shell=True
        )
        print("Tailscale instalado correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al agregar Tailscale: {e}")


def agregar_ngrok():
    try:
        subprocess.run(
            'curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list && sudo apt update && sudo apt install ngrok',
            check=True,
            shell=True,
        )
        print("ngrok instalado")
    except subprocess.CalledProcessError as e:
        print(f"Error al agregar ngrok: {e}")

#cambia y actualiza de el archivo.txt
def cambiar_servidor(archivo_txt, servidor):
    # Lee el contenido actual del archivo
    lineas = []
    if os.path.exists(archivo_txt):
        with open(archivo_txt, "r") as archivo:
            lineas = archivo.readlines()

    # Sobrescribir la configuración del servidor
    with open(archivo_txt, "w") as archivo:
        servidor_existente = False

        for linea in lineas:
            if "server:" in linea:
                archivo.write(f"server:{servidor}\n")  # Actualiza la línea del servidor
                servidor_existente = True
            else:
                archivo.write(linea)

        if (
            not servidor_existente
        ):  # Si no existía, añadimos la configuración del servidor
            archivo.write(f"server:{servidor}\n")


# Uso de la función
def actualizar_archivo(archivo):
    lineas = []
    server_encontrado = False

    # Leer el archivo y buscar la línea que contiene "server:"
    with open(archivo, "r") as f:
        for linea in f:
            if "server:" in linea:
                lineas.append("server:2\n")  # Sobrescribir la línea
                server_encontrado = True
            else:
                lineas.append(linea)  # Mantener la línea original

    # Si no se encontró "server:", agregarlo al final
    if not server_encontrado:
        lineas.append("server:2\n")

    # Escribir el contenido actualizado de vuelta al archivo
    with open(archivo, "w") as f:
        f.writelines(lineas)


def abrirserveo():
    clear()
    # Nombre del archivo donde se guardará la salida
    output_file = "serveoip.log"

    # Crear el archivo vacío si no existe
    with open(output_file, "a"):
        pass  # Crea el archivo si no existe

    # Comando que quieres ejecutar en una nueva sesión de tmux
    comando = f"ssh -R 0:localhost:7777 serveo.net > {output_file} 2>&1"

    # Inicia una nueva sesión de tmux y redirige la salida a un archivo
    subprocess.Popen(["tmux", "new-session", "-d", "-s","serveo_session","bash", "-c", comando])

    # Espera un poco para que el proceso inicie
    time.sleep(3)

    # Enviar el comando "yes" a la sesión de tmux
    comando2 = f'tmux send-keys -t 0 "yes" C-m'
    subprocess.Popen(comando2, shell=True)

    # Crear la ruta absoluta al archivo de log
    log_file_path = os.path.join(os.getcwd(), output_file)

    # Esperar un poco para asegurarse de que se haya escrito en el archivo
    time.sleep(1)

    # Leer el contenido del archivo
    try:
        with open(log_file_path, "r") as log_file:
            contenido = log_file.read()  # Leer todo el contenido del archivo
            print(contenido)  # Imprimir el contenido

           
            if "Connection refused" in contenido:
                print(f"{Fore.RED}El servidor está caído o no está disponible, usa otra alternativa mientras")
                time.sleep(5)
            else:
                print(f"{Fore.CYAN}\nPuedes revisar la IP en el archivo 'serveoip.log'")

    except FileNotFoundError:
        print(f"El archivo {log_file_path} no existe.")
    except PermissionError:
        print(f"No tienes permiso para acceder a {log_file_path}.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
    interfaz()

def abrir_ngrok():
    # Crear o usar una sesión de tmux llamada 'ngrok_session'
    session_name = "ngrok_session"

    # Comando para ejecutar ngrok y redirigir la salida a 'serverip.txt'
    comando = "ngrok tcp 7777 > serverip.txt 2>&1"

    # Iniciar el proceso en tmux
    subprocess.run(
        ["tmux", "new-session", "-d", "-s", session_name, "bash", "-c", comando]
    )

    print(
        "Se ha abierto el server de ngrok.\nPuedes volver a ver la IP en el txt que se llama 'serverip.txt'. o directamente en tmux con ctrl + b-s"
    )

    time.sleep(5)


def leer_salida_ngrok():
    try:
        response = requests.get("http://localhost:4040/api/tunnels")
        data = response.json()
        # Extraer la dirección IP del primer túnel
        ip_info = data["tunnels"][0]
        ip_publica = ip_info["public_url"]

        # Escribir la dirección IP en el archivo serverip.txt
        with open("serverip.txt", "a") as file:  # Usar 'a' para agregar al final
            file.write(f"Dirección IP pública: {ip_publica}\n")

        print(f"{Fore.GREEN}Dirección IP pública: {ip_publica} escrita en serverip.txt")
    except Exception as e:
        print(f"Error al obtener la dirección IP: {e}")


# Función principal
def main():

    app_dir = get_app_directory()
    os.chdir(app_dir)
    archivo_txt = "archivo.txt"
    
    if os.path.exists(archivo_txt):
        print(f"{Fore.GREEN}Ninguna novedad")
       
        interfaz()
        

    with open(archivo_txt, "w") as f:
        f.write("Este archivo fue creado con un propósito divino, no lo borres.\n")
        f.write("tmodloaderversion:1.4.4\n")
    

    # Agregar el repositorio de Tailscale
    agregar_repositorio_tailscale()

    # Agregar ngrok

    agregar_ngrok()

    # Configura el repositorio

    usuario = "tModLoader"
    repositorio = "tModLoader"
    url_releases = (
        f"https://api.github.com/repos/{usuario}/{repositorio}/releases/latest"
    )
    response = requests.get(url_releases)

    if response.status_code == 200:
        latest_release = response.json()
        tmodloader_assets = [
            asset for asset in latest_release["assets"] if "tModLoader" in asset["name"]
        ]

        if tmodloader_assets:
            first_asset = tmodloader_assets[0]
            download_url = first_asset["browser_download_url"]
            archivo_destino = os.path.basename(download_url)
            r = requests.get(download_url)

            if r.status_code == 200:
                with open(archivo_destino, "wb") as f:
                    f.write(r.content)
                print(f"Descargado: {archivo_destino}")

                directorio_destino = os.path.join(app_dir, "server")
                os.makedirs(directorio_destino, exist_ok=True)

                if archivo_destino.endswith(".zip"):
                    extraer_zip(archivo_destino, directorio_destino)
                elif archivo_destino.endswith(".rar"):
                    extraer_rar(archivo_destino, directorio_destino)

            else:
                print(f"Error al descargar el archivo: {r.status_code}")
        else:
            print("No hay activos de tModLoader disponibles en la última release.")
    else:
        print(f"Error al obtener la última release: {response.status_code}")

    print(Fore.RED + "\n\n :) vuelve a iniciar el archivo para iniciar el server")


def interfaz():
    clear()
    ascii_art = r"""
        *                                               (              

    ) (  `        (   (           (                *   ))\ )   (      
 ( /( )\))(       )\ ))\       )  )\ )  (  (     ` )  /(()/(   )\     
 )\()((_)()\  (  (()/((_)(  ( /( (()/( ))\ )( ___ ( )(_)/(_)((((_)(   
(_))/(_()((_) )\  ((_)_  )\ )(_)) ((_)/((_(()|___(_(_()(_))  )\ _ )\  
| |_ |  \/  |((_) _| | |((_((_)_  _| (_))  ((_)  |_   _/ __| (_)_\(_) 
|  _|| |\/| / _ / _` | / _ / _` / _` / -_)| '_|    | | \__ \  / _ \   
 \__||_|  |_\___\__,_|_\___\__,_\__,_\___||_|      |_| |___/ /_/ \_\  
    """

    efecto_arcoiris(ascii_art)  # Llama a la función de efecto arcoíris

    # Ahora, mostramos el menú
    while True:
        print(
            f"{Fore.RED}Solo puedes tener (1) mundo a la vez si usas la aplicación. "
            f"De manera manual se pueden tener varios mundos, mira el tutorial para ver cómo ;) "
            f"{Fore.MAGENTA}| CUIDADO: si colocas un nuevo mundo, los datos del anterior se borrarán, primero guárdalos. "
            f"Lo mismo sucederá con los mods.{Style.RESET_ALL}"
        )
        print("\n")
        print("1. Iniciar server")
        print(f"2. Programa de conexión |{Fore.CYAN} Elige antes de iniciar el server ")
        print(
            f"3. Actualizar tmod |{Fore.RED} ojito {Fore.CYAN}| deberas importar tus mundos y tus mods denuevo"
        )
        print(
            f"4. Importar mundo | {Fore.GREEN}primero sube tu mundo a mediafire o cualquier host | {Style.RESET_ALL}"
        )
        print(
            f"5. importar mods | {Fore.GREEN}primero sube tus mods a mediafire o cualquier host| {Style.RESET_ALL}"
        )
        print(
            f"6. {Fore.LIGHTBLUE_EX}Elegir version de tmodloader|{Fore.RED} Configura esto primero {Fore.CYAN}| deberas importar tus mundos y tus mods denuevo"
        )
        print("7. salir")

        print(
            f"\n\n8. {Fore.LIGHTGREEN_EX}descargar mundo | {Fore.LIGHTBLUE_EX}se generara un archivo {Fore.RED}'empaquetado'{Fore.LIGHTBLUE_EX} dale click derecho, descargar"
        )
        print(
            f"9. {Fore.LIGHTGREEN_EX}Actualizar TSA | {Fore.LIGHTBLUE_EX}se descargara la ultima version del programa, se recomienda hacer copia de seguridad"
        )
        print(
            f"10. {Fore.LIGHTGREEN_EX}Configurar mundos compartidos | {Fore.LIGHTBLUE_EX}vincula tus equipos para que el mundo y los mods sean el mismo en todos{Fore.LIGHTRED_EX}[Beta]\033]8;;https://example.com\033\\[Tuto]\033]8;;\033\\"
        )

        try:
            opcion = input("Selecciona una opción (1-10): ")
        except EOFError:
            print(f"{Fore.RED}[ERROR] No hay entrada disponible (stdin cerrado). Cerrando...{Style.RESET_ALL}")
            sys.exit(0)  # salir de la función sin crashear

        except KeyboardInterrupt:
            clear()
            print("\n\nSaliendo del menú...")
            sys.exit(0)


        if opcion == "1":
            abrir_server("archivo.txt")
        elif opcion == "2":
            conexion()
        elif opcion == "3":
            actualizar_tmod()
        elif opcion == "4":
            importar_mundo()
        elif opcion == "5":
            importar_mods()
        elif opcion == "6":
            cambiar_version()
        elif opcion == "7":
            print("saliendo....")
            sys.exit()
        elif opcion == "8":
            empaquetar_mundo()
            print("se generara un archivo rar en la carpeta world con el nombre 'empaquetado' ")
            time.sleep(10)
        elif opcion == "9":
            actualizar_programa()
        elif opcion == "15":
            iniciar_syncthing()
            print(f"{Fore.RED}Se inicio syncthing si haces 'Ctrl + c' se cerrara pero si sales con 7 se ejecutara en segundo plano")
            time.sleep(15)
        else:
            clear()
            print(f"{Fore.RED}Opción inválida. Por favor, selecciona una opción válida.")
            time.sleep(5)
            interfaz()

                   
        
def ejecutar_script(version):
    # Ruta relativa de los scripts
    script_144 = os.path.join("server", "start-tModLoaderServer.sh")
    script_143 = os.path.join("1.4.3", "start-tModLoaderServer.sh")
    script_1353 = os.path.join("1.3.5.3", "tModLoaderServer")

    try:
        if version == "1.4.4":
            subprocess.run(["bash", script_144], check=True)
            print("Ejecutando start-tModLoaderServer.sh para la versión 1.4.4.")
        elif version == "1.4.3":
            subprocess.run(["bash", script_143,"-config","serverconfig.txt"],  check=True)
            print("Ejecutando start-tModLoaderServer.sh para la versión 1.4.3.")
        elif version == "1.3.5.3":
            subprocess.run([script_1353, "-config", "serverconfig.txt"], check=True)
            print("Ejecutando tModLoaderServer para la versión 1.3.5.3.")
        else:
            print(f"No hay un script definido para la versión {version}.")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el script para la versión {version}: {e}")


def abrir_server(ruta_archivo):
    clear()
    try:
        with open(ruta_archivo, "r") as f:
            for linea in f:
                if "tmodloaderversion:" in linea:
                    # Extraer la versión
                    version = linea.split(":")[1].strip()
                    print(f"Versión encontrada: {version}")
                    ejecutar_script(version)
                    return
            
            # Si no se encuentra la versión, usar la versión predeterminada
            print("No se especificó versión; se usará la última")
            ejecutar_script("1.4.4")
    except FileNotFoundError:
        print("Archivo no encontrado.")

    except KeyboardInterrupt:
            clear()
            print("\n\nSaliendo del menú...")
            sys.exit(0)



def conexion():
    clear()
    print("\n")
    print(
        f"¿Qué servicio usarás?\n1. ngrok | el más rápido pero es pago\n2. serveo | aguanta muchas personas pero es lento\n3. tailscale | aguanta pocas personas pero es rápido |{Fore.GREEN} recuerda tener la app en tu equipo{Style.RESET_ALL}\n4. Cerrar ngrok y serveo\n5. cerrar tailscale\n6. atras"
    )

    opcion3 = input("Selecciona una opción (1-4): ")

    if opcion3 == "1":
        token = input(
            'Pega tu config token de ngrok. Ejemplo:\n"2Pa56EWmwdsfVFHGEW4"\n:'
        )

        try:
            with open("archivo.txt", "r") as archivo:
                lineas = archivo.readlines()

            # Sobrescribir el token si ya existe
            with open("archivo.txt", "w") as archivo:
                token_existente = False
                server_existente = False
                for linea in lineas:
                    if "ngroktoken:" in linea:
                        archivo.write(f'ngroktoken:"{token}"\n')
                        token_existente = True
                    elif "server:" in linea:
                        archivo.write("server:1\n")  # Sobrescribe la línea del servidor
                        server_existente = True
                    else:
                        archivo.write(linea)

                if not token_existente:
                    archivo.write(f'ngroktoken:"{token}"\n')
                    print("Token guardado en archivo.txt.")

                if not server_existente:  # Si no existía, añadimos server:1
                    archivo.write("server:1\n")

        except FileNotFoundError:
            # Crear el archivo si no existe
            with open("archivo.txt", "w") as archivo:
                archivo.write(f'ngroktoken:"{token}"\n')
                print("El archivo no existía, pero fue creado con el token.")

                # Añadir el token a ngrok
        subprocess.run(["ngrok", "config", "add-authtoken", token], check=True)
        print("Token de ngrok configurado correctamente.")
        abrir_ngrok()
        leer_salida_ngrok()

    elif opcion3 == "2":
        print(f"{Fore.RED}\nIntentando abrir serveo")
        abrirserveo()
        actualizar_archivo("archivo.txt")
        time.sleep(4)

    elif opcion3 == "3":
        inciar_tailscale()

    elif opcion3 == "4":
        cerrar_serveo()

    elif opcion3 == "5":
        detener_tailscale()

    elif opcion3 == "6":
        interfaz()

    else:
        print("Opción inválida. Por favor, selecciona una opción válida.")


def importar_mods(destination_folder="mods"):

    # Comprobar y crear la carpeta de destino si no existe
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Preparar el comando para ejecutar mediafire-dl
    url = input(
        "Coloca tu link de mediafire | la raiz del rar o del el zip debe contener los mods \n:"
    )
    command = ["wget", "--content-disposition", url]

    try:
        # Ejecutar el comando
        subprocess.run(command, check=True, cwd=destination_folder)
        print(
            f"\n{Fore.RED}mods descargados y guardado en {destination_folder}{Style.RESET_ALL}"
        )

        # Listar los archivos en la carpeta de destino
        archivos_descargados = os.listdir(destination_folder)

        # Extraer archivos si hay un archivo zip o rar
        for archivo in archivos_descargados:
            archivo_path = os.path.join(destination_folder, archivo)

            # Comprobar si el archivo es un zip
            if archivo.endswith(".zip"):
                with zipfile.ZipFile(archivo_path, "r") as zip_ref:
                    zip_ref.extractall(destination_folder)
                print(f"{Fore.GREEN}Archivo zip extraído: {archivo}{Style.RESET_ALL}")
                actualizar_mods()

            # Comprobar si el archivo es un rar
            elif archivo.endswith(".rar"):
                with rarfile.RarFile(archivo_path) as rar_ref:
                    rar_ref.extractall(destination_folder)
                print(f"{Fore.GREEN}Archivo rar extraído: {archivo}{Style.RESET_ALL}")
                actualizar_mods()

    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Error al ejecutar el comando: {e}{Style.RESET_ALL}")
    except zipfile.BadZipFile:
        print(
            f"{Fore.RED}Error: El archivo {archivo} no es un zip válido.{Style.RESET_ALL}"
        )
    except rarfile.RarCannotExec:
        print(
            f"{Fore.RED}Error: No se puede ejecutar rar. Asegúrate de que esté instalado.{Style.RESET_ALL}"
        )
    except Exception as e:
        print(f"{Fore.RED}Se produjo un error: {e}{Style.RESET_ALL}")


def importar_mundo(destination_folder="worlds"):
    clear()
    formatear_carpeta()
    # Comprobar y crear la carpeta de destino si no existe
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Preparar el comando para ejecutar mediafire-dl
    url = input(
        "Coloca tu link de mediafire | El rar o el zip debe contener todos los archivos del mundo en la raiz\n:"
    )
    command = ["wget", "--content-disposition", url]
    
    if not url:
        clear()
        print(Fore.RED + "No se proporcionó una URL válida." + Style.RESET_ALL)
        time.sleep(3)
        interfaz()

    try:
        # Ejecutar el comando
        subprocess.run(command, check=True, cwd=destination_folder)
        print(
            f"\n{Fore.RED}Archivo descargado y guardado en {destination_folder}{Style.RESET_ALL}"
        )

        # Listar los archivos en la carpeta de destino
        archivos_descargados = os.listdir(destination_folder)

        # Extraer archivos si hay un archivo zip o rar
        for archivo in archivos_descargados:
            archivo_path = os.path.join(destination_folder, archivo)

            # Comprobar si el archivo es un zip
            if archivo.endswith(".zip"):
                with zipfile.ZipFile(archivo_path, "r") as zip_ref:
                    zip_ref.extractall(destination_folder)
                print(f"{Fore.GREEN}Archivo zip extraído: {archivo}{Style.RESET_ALL}")
                time.sleep(5)
                actualizar_mundo()
            # Comprobar si el archivo es un rar
            elif archivo.endswith(".rar"):
                with rarfile.RarFile(archivo_path) as rar_ref:
                    rar_ref.extractall(destination_folder)
                print(f"{Fore.GREEN}Archivo rar extraído: {archivo}{Style.RESET_ALL}")
                time.sleep(5)
                actualizar_mundo()
            
            interfaz()

    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Error al descargar el archivo")
        time.sleep(6)
        interfaz()
    except FileNotFoundError:
        print(
            Fore.RED
            + "El comando 'mediafire-dl' no se encuentra. Asegúrate de que esté instalado y en tu PATH."
            + Style.RESET_ALL
        )
    except Exception as e:
        print(Fore.RED + f"Ocurrió un error: {e}" + Style.RESET_ALL)

# Bloque 2: Función para extraer archivos .rar
def extraer_rar(rar_path, destino):
    try:
        with rarfile.RarFile(rar_path) as rf:
            rf.extractall(destino)
            print(f"Archivos extraídos de {rar_path} en: {destino}")
    except rarfile.Error as e:
        print(f"Error al extraer el archivo .rar: {e}")


# Bloque 3: Función para extraer archivos .zip
def extraer_zip(zip_path, destino):
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(destino)
            print(f"Archivos extraídos de {zip_path} en: {destino}")
    except zipfile.BadZipFile as e:
        print(f"Error al extraer el archivo .zip: {e}")


def formatear_carpeta(destination_folder="worlds"):
    """Elimina el contenido de la carpeta de destino sin eliminar la carpeta en sí."""
    if os.path.exists(destination_folder):
        # Eliminar todos los archivos y carpetas dentro de la carpeta de destino
        for item in os.listdir(destination_folder):
            item_path = os.path.join(destination_folder, item)
            if os.path.isfile(item_path):
                os.remove(item_path)  # Eliminar archivos
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Eliminar directorios





def obtener_version_tmodloader():
    ruta_archivo = "archivo.txt"
    with open(ruta_archivo, "r") as archivo:
        lineas = archivo.readlines()

    for linea in lineas:
        if "tmodloaderversion:" in linea:
            version = linea.split(":")[1].strip()  # Eliminar espacios en blanco
            return version

    return None


def descargar_configuracion():
    url = "https://gist.githubusercontent.com/luisfer153/75822586611e518d0ad369ebdae98acc/raw/dfaf49bbf8f0c7086383ceb64f61ac2122c66707/serverconfig.txt"

    if os.path.exists("1.3.5.3/serverconfig.txt"):
        print("El archivo de configuración ya existe. No se descargará.")
        return

    response = requests.get(url)

    if response.status_code == 200:
        with open("1.3.5.3/serverconfig.txt", "wb") as f:
            f.write(response.content)
        print("Archivo de configuración descargado correctamente.")
    else:
        print(f"Error al descargar el archivo: {response.status_code}")

#toma la version del jogo y edita el serverconfig 
def actualizar_mundo(destination_folder="worlds"):
    version = obtener_version_tmodloader()
    if version is None:
        print("No se encontró la versión de tModLoader en el archivo.")
        return

    if version == "1.4.4":
        config_path = "server/serverconfig.txt"
    elif version == "1.4.3":
        config_path = "1.4.3/serverconfig.txt"
    elif version == "1.3.5.3":
        descargar_configuracion()
        config_path = "1.3.5.3/serverconfig.txt"
    else:
        print("Versión no reconocida.")
        return

    wld_files = [f for f in os.listdir(destination_folder) if f.endswith(".wld")]

    if not wld_files:
        print("No se encontraron archivos .wld en la carpeta de destino.")
        return

    wld_file = wld_files[0]
    wld_file_path = os.path.abspath(os.path.join(destination_folder, wld_file))

    # Intentar leer el archivo de configuración con manejo de errores
    try:
        with open(config_path, "r", encoding="utf-8") as config_file:
            lines = config_file.readlines()
    except UnicodeDecodeError:
        # Si falla, intenta abrirlo con ISO-8859-1
        with open(config_path, "r", encoding="ISO-8859-1") as config_file:
            lines = config_file.readlines()

    for i, line in enumerate(lines):
        if line.startswith("world="):
            lines[i] = f"world={wld_file_path}\n"  # Reemplazar la línea
            break
    else:
        lines.append(f"world={wld_file_path}\n")

    with open(config_path, "w", encoding="utf-8") as config_file:
        config_file.writelines(lines)

    print(
        f'La dirección del archivo .wld "{wld_file_path}" se ha actualizado en {config_path}.'
    )


def actualizar_mods(destination_folder="mods"):
    version = obtener_version_tmodloader()
    if version is None:
        print("No se encontró la versión de tModLoader en el archivo.")
        return

    if version == "1.4.4":
        config_path = "server/serverconfig.txt"
    elif version == "1.4.3":
        config_path = "1.4.3/serverconfig.txt"
    elif version == "1.3.5.3":
        descargar_configuracion()
        config_path = "1.3.5.3/serverconfig.txt"
    else:
        print("Versión no reconocida.")
        return

    # Obtener la ruta de la carpeta de mods
    mod_folder_path = os.path.abspath(destination_folder)

    # Intentar leer el archivo de configuración con manejo de errores
    try:
        with open(config_path, "r", encoding="utf-8") as config_file:
            lines = config_file.readlines()
    except UnicodeDecodeError:
        # Si falla, intenta abrirlo con ISO-8859-1
        with open(config_path, "r", encoding="ISO-8859-1") as config_file:
            lines = config_file.readlines()

    # Reemplazar la línea existente que comienza con "modpath="
    for i, line in enumerate(lines):
        if line.startswith("modpath="):
            lines[i] = f"modpath={mod_folder_path}\n"  # Reemplazar la línea
            break
    else:
        lines.append(f"modpath={mod_folder_path}\n")

    # Escribir el contenido actualizado de nuevo en el archivo
    with open(config_path, "w", encoding="utf-8") as config_file:
        config_file.writelines(lines)

    print(f'La ruta de los mods se ha actualizado en {config_path}.')


def inciar_tailscale():
    try:
        # Ejecutar el comando 'sudo tailscale up'
        subprocess.Popen(
            ["sudo", "tailscaled"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print(
            f"{Fore.GREEN}\npresiona Ctrl + click en el enlace\nse incia automatico si ya vinculaste"
        )
        subprocess.run(["sudo", "tailscale", "up"], check=True)
        time.sleep(2)

    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {e}")
    except FileNotFoundError:
        print(
            'El comando "tailscale" no se encuentra. Asegúrate de que esté instalado.'
        )


def detener_tailscale():
    clear()
    try:

        subprocess.run(["sudo", "pkill", "tailscaled"], check=True)
        print(f"{Fore.GREEN}\nse ha detenido tailscale{Style.RESET_ALL}")
        time.sleep(1)

    except subprocess.CalledProcessError as e:
        print(f"\n{Fore.RED}nunca abriste tailcale")
        time.sleep(3)


def actualizar_tmod():
    clear()
    usuario = "tModLoader"
    repositorio = "tModLoader"
    url_releases = (
        f"https://api.github.com/repos/{usuario}/{repositorio}/releases/latest"
    )
    response = requests.get(url_releases)

    if response.status_code == 200:
        latest_release = response.json()
        tmodloader_assets = [
            asset for asset in latest_release["assets"] if "tModLoader" in asset["name"]
        ]

        if tmodloader_assets:
            first_asset = tmodloader_assets[0]
            download_url = first_asset["browser_download_url"]
            archivo_destino = os.path.basename(download_url)
            r = requests.get(download_url)

            if r.status_code == 200:
                with open(archivo_destino, "wb") as f:
                    f.write(r.content)
                print(f"Descargado: {archivo_destino}")

                directorio_destino = os.path.join(os.getcwd(), "server")
                os.makedirs(directorio_destino, exist_ok=True)

                if archivo_destino.endswith(".zip"):
                    extraer_zip(archivo_destino, directorio_destino)
                elif archivo_destino.endswith(".rar"):
                    extraer_rar(archivo_destino, directorio_destino)

                # Ruta del archivo
                ruta_archivo = "archivo.txt"

                # Abrir el archivo para leer todo el contenido
                with open(ruta_archivo, "r") as archivo:
                    lineas = archivo.readlines()

                # Revisar si ya existe la línea con "tmodloaderversion"
                nueva_version = "tmodloaderversion:1.4.4\n"
                encontrado = False

                for i, linea in enumerate(lineas):
                    if "tmodloaderversion:" in linea:
                        # Si encuentra la línea, la reemplaza
                        lineas[i] = nueva_version
                        encontrado = True
                        break

                # Si no se encuentra, agregarla al final
                if not encontrado:
                    lineas.append(nueva_version)

                # Escribir de nuevo todo el contenido en el archivo
                with open(ruta_archivo, "w") as archivo:
                    archivo.writelines(lineas)


                interfaz()

            else:
                print(f"Error al descargar el archivo: {r.status_code}")
        else:
            print("No hay activos de tModLoader disponibles en la última release.")
    else:
        print(f"Error al obtener la última release: {response.status_code}")


def cambiar_version():
    clear()
    version = input(
        f"\n\n\n\n¿que version desea usar?\n\n1. 1.4(ultima)\n2. 1.4.3\n3. 1.3.5.3\n"
    )
    if version == "1":
        actualizar_tmod()
    elif version == "2":
        importar_version_2()
    elif version == "3":
        importar_version_3()


def importar_version_3():
    clear()
    # Crear la carpeta si no existe
    carpeta = "1.3.5.3"
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    # URL del archivo a descargar
    url = "https://github.com/tModLoader/tModLoader/releases/download/v0.11.8.9/tModLoader.Linux.v0.11.8.9.zip"

    # Ruta para guardar el archivo
    archivo_destino = os.path.join(carpeta, "tModLoader.Linux.v0.11.8.9.zip")

    # Descargar el archivo
    response = requests.get(url)
    with open(archivo_destino, "wb") as f:
        f.write(response.content)

    print(f"se esta descargando la version 1.3.5.3 en: {archivo_destino}")

    # Descargar el archivo
    response = requests.get(url)
    with open(archivo_destino, "wb") as f:
        f.write(response.content)

    extraer_zip(archivo_destino, carpeta)
    dar_permisos_a_carpeta("1.3.5.3")

    print(f"se ha descargado la version 1.3.5.3 en: {archivo_destino}")
    # Ruta del archivo
    ruta_archivo = "archivo.txt"

    # Abrir el archivo para leer todo el contenido
    with open(ruta_archivo, "r") as archivo:
        lineas = archivo.readlines()

    # Revisar si ya existe la línea con "tmodloaderversion"
    nueva_version = "tmodloaderversion:1.3.5.3\n"
    encontrado = False

    for i, linea in enumerate(lineas):
        if "tmodloaderversion:" in linea:
            # Si encuentra la línea, la reemplaza
            lineas[i] = nueva_version
            encontrado = True
            break

    # Si no se encuentra, agregarla al final
    if not encontrado:
        lineas.append(nueva_version)

    # Escribir de nuevo todo el contenido en el archivo
    with open(ruta_archivo, "w") as archivo:
        archivo.writelines(lineas)


def importar_version_2():
    clear()
    # Crear la carpeta si no existe
    carpeta = "1.4.3"
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    # URL del archivo a descargar
    url = "https://github.com/tModLoader/tModLoader/releases/download/v2022.09.47.87/tModLoader.zip"

    # Ruta para guardar el archivo
    archivo_destino = os.path.join(carpeta, "tModLoader1.4.3.zip")

    # Descargar el archivo
    response = requests.get(url)
    with open(archivo_destino, "wb") as f:
        f.write(response.content)

    extraer_zip(archivo_destino, carpeta)
    dar_permisos_a_carpeta("1.4.3")

    print(f"se ha descargado la version 1.4.3 en: {archivo_destino}")
    # Ruta del archivo
    ruta_archivo = "archivo.txt"

    # Abrir el archivo para leer todo el contenido
    with open(ruta_archivo, "r") as archivo:
        lineas = archivo.readlines()

    # Revisar si ya existe la línea con "tmodloaderversion"
    nueva_version = "tmodloaderversion:1.4.3\n"
    encontrado = False

    for i, linea in enumerate(lineas):
        if "tmodloaderversion:" in linea:
            # Si encuentra la línea, la reemplaza
            lineas[i] = nueva_version
            encontrado = True
            break

    # Si no se encuentra, agregarla al final
    if not encontrado:
        lineas.append(nueva_version)

    # Escribir de nuevo todo el contenido en el archivo
    with open(ruta_archivo, "w") as archivo:
        archivo.writelines(lineas)


def dar_permisos_a_carpeta(ruta_carpeta):
    # Verificar si la carpeta existe
    if not os.path.exists(ruta_carpeta):
        print(f"La ruta especificada no existe: {ruta_carpeta}")
        return

    try:
        # Comando para dar permisos en Linux
        subprocess.run(["chmod", "-R", "777", ruta_carpeta], check=True)
        print(f"Permisos otorgados a la carpeta: {ruta_carpeta}")
    except subprocess.CalledProcessError as e:
        print(f"Error al cambiar permisos: {e}")

def empaquetar_mundo(carpeta="worlds", nombre_archivo="empaquetado.rar"):
    # Verificar si la carpeta existe
    if not os.path.exists(carpeta):
        print(f"La carpeta {carpeta} no existe.")
        return

    # Ruta absoluta de la carpeta
    carpeta_path = os.path.abspath(carpeta)

    # Comando para comprimir en formato RAR
    comando = ["rar", "a", nombre_archivo, carpeta_path]

    try:
        # Ejecutar el comando de compresión
        subprocess.run(comando, check=True)
        print(f"La carpeta {carpeta} se ha comprimido en {nombre_archivo}")
    except subprocess.CalledProcessError as e:
        print(f"Error al intentar comprimir la carpeta: {e}")


URL_VERSION = "https://raw.githubusercontent.com/luisfer153/TSA/main/version.txt"
URL_BINARIO_TEMPLATE = "https://github.com/luisfer153/TSA/releases/download/v{v}/TSA-{v}-linux-x86_64"

VERSION = "1.0.1"  # versión actual

def actualizar_programa():
    try:
        r = requests.get(URL_VERSION, timeout=5)
        r.raise_for_status()
        ultima = r.text.strip()
    except Exception as e:
        print(f"⚠ No se pudo verificar la versión: {e}")
        time.sleep(3)
        return

    if ultima != VERSION:
        print(f"Hay una nueva versión disponible: {ultima}")

        # Construir URL con la versión real
        url_binario = URL_BINARIO_TEMPLATE.format(v=ultima)
        print(f"Descargando desde: {url_binario}")

        try:
            r2 = requests.get(url_binario, stream=True, timeout=10)
            r2.raise_for_status()

            # Guardar en el directorio actual (pwd)
            directorio_actual = os.getcwd()
            nombre_archivo = os.path.join(directorio_actual, f"TSA-{ultima}-linux-x86_64")

            with open(nombre_archivo, "wb") as f:
                for chunk in r2.iter_content(chunk_size=8192):
                    f.write(chunk)

            os.chmod(nombre_archivo, 0o755)
            print(f"Descargado como {nombre_archivo}")
            print("Por seguridad, reemplaza manualmente el binario actual.")
        except Exception as e:
            print(f"Error descargando la actualización: {e}")
    else:
        print("Ya estás en la última versión")

    time.sleep(3)
    
            


if __name__ == "__main__":
    colorama.init(autoreset=True)  # Inicializa colorama
    #si el archivo txt existe no me interesa que se ejecute depenedencias
    FLAG_FILE = "archivo.txt"
    if os.path.exists(FLAG_FILE): 
        main()
    #si no existe que se ejecute dependencias y main para que instale la primera vez luego que se ejecute una segunda vez para que incialice la aplicacion
    instalar_dependencias()
    main()
    main()




