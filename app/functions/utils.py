import datetime, websocket
import os, ssl, pytz
import subprocess
from pathlib import Path
from fastapi.responses import FileResponse
from dateutil.relativedelta import relativedelta
from shuttlelib.openshift.client import OpenshiftClient

#Time for renamed files.
now = datetime.datetime.now()
date = now.strftime("%Y%m%d_%H%M")

async def get_namespaces(cluster, functionalEnvironment, region):
    client = OpenshiftClient(entityID="spain")
    namespace_list = await client.get_resource(resource="namespaces", functionalEnvironment=functionalEnvironment, region=region, cluster=cluster)
    namespaces_names = [dic['metadata']['name'] for dic in namespace_list[region]['items']]
    return namespaces_names

async def get_microservices(cluster, functionalEnvironment, region):
    client = OpenshiftClient(entityID="spain")
    microservices_list = await client.get_resource(resource=["deploymentconfigs", "deployments"], functionalEnvironment=functionalEnvironment, region=region, cluster=cluster)
    microservices_names = [dic['metadata']['name'] for dic in microservices_list[region]['items']]
    return microservices_names

async def get_podnames(cluster, functionalEnvironment, region):
    client = OpenshiftClient(entityID="spain")
    pod_list = await client.get_resource(resource="pods", functionalEnvironment=functionalEnvironment, region=region, cluster=cluster)
    pod_names = [dic['metadata']['name'] for dic in pod_list[region]['items']]
    return pod_names

async def rename_and_move_files(namespace, pod, original_file, action):
    file_type = "HeapDump" if action in ["1", "3"] else "ThreadDump"
    new_file = f"{file_type}-{pod}-{date}.gz"
    downloads_dir = Path("/app/downloads")
    namespace_dir = downloads_dir / namespace
    new_file_path = namespace_dir / new_file

    if not namespace_dir.exists():
        namespace_dir.mkdir(parents=True, exist_ok=True)

    os.rename(original_file, new_file_path)
    print("Renaming finished")

    move_command = ["mv", str(new_file_path), str(new_file_path)]
    subprocess.Popen(move_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Command to grant permissions
    permission_command = ["chmod", "-R", "777", "/app/downloads/"]
    subprocess.Popen(permission_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return new_file

#Identify pid´s process for JBOSS pods
async def identify_pid(pod):
    try:
        proc = subprocess.run(["oc", "rsh", pod, "pgrep", "-f", "Djboss.modules.system.pkgs"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        pid = proc.stdout.decode('utf-8').strip()
        print(f"The process ID is: {pid}")
        return pid
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None

def fromtimestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, tz=pytz.utc)

# Delete files x days older for mantainance.
def clean_old_files(directory, days=1):
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
            data.append#(recv.decode("utf-8"))
    return ws, data

# RSYNC command to copy the dump to application´s pod
async def rsync_command(namespace, pod, file_name, action):
    try:
        process = subprocess.run(["oc", "rsync", "--delete", f"{pod}:/opt/produban/{file_name}", "."], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        if process.returncode == 0:
            print("RSYNC command completed successfully")
            # Rename the dump´s filename adding microservice and date. Move renamed file to downloads folder.
            original_file = file_name
            new_file = await rename_and_move_files(namespace, pod, original_file, action)
            return FileResponse(f"/app/downloads/{namespace}/{new_file}", media_type="application/octet-stream", filename=new_file)
    except subprocess.CalledProcessError as e:
        print(f"RSYNC command failed with the message: {e.output}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")