import datetime, os, time
import subprocess

# Time for renaming files.
now = datetime.datetime.now()
date = now.strftime("%Y%m%d_%H%M")

# Function to renaming and placing files from Heapdump´s functions.
async def renaming_placing(namespace, pod, original_file, action):
    if action == "1" or action == "3":
        new_file = f"HeadDump_{pod}_{date}.gz"
    else:
        new_file = f"ThreadDump_{pod}_{date}.gz"

    os.rename(original_file, new_file)
    time.sleep(1)
    print("Renaming finished")
    host = os.environ["HOSTNAME"]
    print(f"Hostname at 1 is: {host}")

    if new_file is not None and os.path.isfile(new_file) and os.path.exists(f"/app/downloads/{namespace}"):
        command = ["mv", f"{new_file}", f"/app/downloads/{namespace}/{new_file}"]
        subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Lanzar el comando para cambiar los permisos
        permission_command = ["chmod", "-R 777", "/app/downloads/"]
        subprocess.Popen(permission_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        host = os.environ["HOSTNAME"]
        print(f"Hostname at 2 is: {host}")
        time.sleep(1)

    elif not os.path.exists(f"/app/downloads/{namespace}") and new_file is not None and os.path.isfile(new_file):
        os.makedirs(f"/app/downloads/{namespace}", exist_ok=True)
        command = ["mv", f"{new_file}", f"/app/downloads/{namespace}/{new_file}"]
        subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        permission_command = ["chmod", "-R 777", "/app/downloads/"]
        subprocess.Popen(permission_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        host = os.environ["HOSTNAME"]
        print(f"Hostname at 3 is: {host}")
        time.sleep(1)

    else:
        print(f"{new_file} file does NOT exist.")
        host = os.environ["HOSTNAME"]
        print(f"Hostname at 4 is: {host}")

    return new_file

async def identify_pid(pod):
    #Identify pid´s process for JBOSS
    proc = subprocess.run(["oc", "rsh", pod, "pgrep", "-f", "Djboss.modules.system.pkgs"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pid = proc.stdout.decode('utf-8').strip()
    print(f"The process ID is: {pid}")

    return pid

async def clean_old_files():
    directory = "/app/downloads"
    days = 7
    now = time.time()
    deleted_files = []
    for root, dirs, files in os.walk(directory):
        dirs = [dir for dir in dirs if dir]
        for file in files:
            file_path = os.path.join(root, *dirs, file)
            creation_time = os.path.getctime(file_path)
            if now - creation_time > days * 24 * 60 * 60:
                os.remove(file_path)
                deleted_files.append(file_path)

    return deleted_files