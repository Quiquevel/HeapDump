import datetime, websocket
import os, ssl, pytz, subprocess, codecs
from pathlib import Path
from dateutil.relativedelta import relativedelta
from shuttlelib.openshift.client import OpenshiftClient
from shuttlelib.utils.logger import get_Logger
from sys import stderr

logger = get_Logger()
client = OpenshiftClient(entityID="spain")

def execute_in_pod(pod, command):
    # Build complete command
    complete_command = f"oc exec {pod} -- {command}"
    
    # Run the command and collect the output
    process = subprocess.Popen(complete_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    exit, error = process.communicate()

    # Manejar errores si es necesario
    if process.returncode != 0:
        print(f"Error executing command: {error}")
        return []

    # Split the output into lines and remove blank lines
    lines = exit.split('\n')
    clean_lines = [line.strip() for line in lines if line.strip()]

    return clean_lines

def automatic_delete():
    folder = "/app/downloads"
    try:
        # Execute sh command using subprocess
        subprocess.run(["find", "/app/downloads", "-type", "f", "-mtime", "+7", "-exec", "rm", "{}", ";"])
        logger.info(f'Older files in {folder} succefully erased.')
    except subprocess.CalledProcessError as e:
        logger.error(f'Error executing command: {e}')

async def get_namespaces(cluster, functionalEnvironment, region):
    global client
    namespace_list = await client.get_resource(resource="namespaces", functionalEnvironment=functionalEnvironment, region=region, cluster=cluster)
    namespaces_names = [dic['metadata']['name'] for dic in namespace_list[region]['items']]
    return namespaces_names

async def get_microservices(cluster, functionalEnvironment, region, namespace):
    global client
    
    # Get deployments.
    deployments_list = await client.get_resource(resource="deployments", functionalEnvironment=functionalEnvironment, region=region, cluster=cluster, namespace=namespace)
    deployments_names = [dic['metadata']['name'] for dic in deployments_list[region]['items']]
    
    # Get deploymentconfigs.
    deploymentconfigs_list = await client.get_resource(resource="deploymentconfigs", functionalEnvironment=functionalEnvironment, region=region, cluster=cluster, namespace=namespace)
    deploymentconfigs_names = [dic['metadata']['name'] for dic in deploymentconfigs_list[region]['items']]
    
    # Combine the results.
    microservices_names = deployments_names + deploymentconfigs_names
    
    return microservices_names

async def get_podnames(cluster, functionalEnvironment, region, namespace, microservices):
    global client
    pod_list = await client.get_resource(resource="pods", functionalEnvironment=functionalEnvironment, region=region, cluster=cluster, namespace=namespace)
    pod_names = [dic['metadata']['name'] for dic in pod_list[region]['items']]
    podsresult = list(filter(lambda x: microservices in x, pod_names))
    return podsresult

async def rename_and_move_files(namespace, pod, original_file, action):
    file_type = "HeapDump" if action in ["1", "3"] else "ThreadDump"
    #Time for renamed files.
    now: datetime = datetime.datetime.now()
    date = now.strftime("%Y%m%d_%H%M")
    
    new_file = f"{file_type}-{pod}-{date}.gz"
    downloads_dir = Path("/app/downloads")
    namespace_dir = downloads_dir / namespace
    new_file_path = namespace_dir / new_file

    if not namespace_dir.exists():
        namespace_dir.mkdir(parents=True, exist_ok=True)

    os.rename(original_file, new_file_path)
    logger.info("Renaming finished")

    move_command = ["mv", str(new_file_path), str(new_file_path)]
    subprocess.Popen(move_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Command to grant permissions
    permission_command = ["chmod", "-R", "777", "/app/downloads/"]
    subprocess.Popen(permission_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return new_file

#Identify pid´s process for JBOSS pods
async def get_my_pid(pod):
    try:
        proc = subprocess.run(["oc", "rsh", pod, "pgrep", "-f", "Djboss.modules.system.pkgs"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        pid = proc.stdout.decode('utf-8').strip()
        logger.info(f"The process ID is: {pid}")
        return pid
    except subprocess.CalledProcessError as e:
        logger.error(f"Error: {e}")
        return None

def fromtimestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, tz=pytz.utc)

# Delete files x days older for mantainance.
def clean_old_files(directory, days=30):
    now = datetime.datetime.now()
    deleted_files = []
    for root, dirs, files in os.walk(directory):
        dirs = [dir for dir in dirs if dir]
        for file in files:
            file_path = os.path.join(root, *dirs, file)
            creation_time = fromtimestamp(os.path.getctime(file_path))
            delta = relativedelta(now, creation_time)
            if delta.days > days:
                os.remove(file_path)
                deleted_files.append(file_path)

    return deleted_files

# Connecting using WebSocket
async def websocket_connection(token, request_url):
    headers = {
        "Authorization": "Bearer " + token,
        "Connection": "upgrade",
        "Upgrade": "SPDY/4.8",
        "X-Stream-Protocol-Version": "channel.k8s.io",
        "charset": "utf-8"
    }

    ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
    ws.connect(request_url.replace("https", "wss"), header=headers)
    data = []
    while ws.connected != False:
        recv = ws.recv()
        if recv != '':
            data.append
    return ws, data

def delete_pod(pod):
    delete = subprocess.run(["oc", "delete", "pod", codecs.encode(pod, "utf-8")], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if delete.returncode == 0:
        logger.info("Borrado del pod correcto")
    else:
        logger.error("El borrado del pod ha fallado")