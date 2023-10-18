from shuttlelib.openshift.client import OpenshiftClient
import urllib3, ssl, urllib
from urllib3.exceptions import InsecureRequestWarning
import websocket, subprocess
from fastapi.responses import FileResponse
from functions.utils import renaming_placing, identify_pid, clean_old_files

urllib3.disable_warnings(InsecureRequestWarning)

async def generate_heapdump(url, token, namespace, pod, action):
    headers = {
        "Authorization": "Bearer " + token,
        "Connection": "upgrade",
        "Upgrade": "SPDY/4.8",
        "X-Stream-Protocol-Version": "channel.k8s.io",
        "charset": "utf-8"
    }

    # Heapdump generation and compression
    dump_command = f"jmap -dump:format=b,file=heapdumpPRO 1; gzip heapdumpPRO"
    dump_command_encoded = urllib.parse.quote(dump_command, safe='')

    # Running the command on the target pod
    request_url = f'{url}/api/v1/namespaces/{namespace}/pods/{pod}/exec?'
    request_url += f'command=/bin/bash&command=-c&command={dump_command_encoded}'
    request_url += '&stdin=true&stderr=true&stdout=true&tty=false'

    data = []

    ws_destino = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
    ws_destino.connect(request_url.replace("https", "wss"), header=headers)
    while ws_destino.connected != False:
        recv = ws_destino.recv()
        if recv != '':
            data.append(recv.decode("utf-8"))

    login_command = ["oc", "login", "--token=" + token, "--server=" + url, "--namespace=" + namespace, "--insecure-skip-tls-verify=true"]
    login_process = subprocess.Popen(login_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Voy a intentar logarme en {url}, en el namespace {namespace}.")
    stderr = login_process.communicate()

    if login_process.returncode != 0:
        print(f"Login failed. Error message: {stderr}")
    else:
        print("Login succeeded.")

        #Copy the dump to the destination pod and download it locally.
        try:
            process = subprocess.run(["oc", "rsync", "--delete", "{}:/opt/produban/heapdumpPRO.gz".format(pod), "."], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if process.returncode == 0:
                print("RSYNC command completed successfully")
                # Rename the generic pod´s name and move it to downloads´s folder.
                original_file= "heapdumpPRO.gz"
                new_file = await renaming_placing(namespace, pod, original_file, action)

                return FileResponse(f"/app/downloads/{namespace}/{new_file}", media_type="application/octet-stream", filename = new_file)
            else:
                print(f"RSYNC command failed with the message: {process.stderr}")

        except subprocess.CalledProcessError as e:
            print(e.output)
    #Close websocket    
    ws_destino.close()

    return data

async def generate_threaddump(url, token, namespace, pod, action):
    headers = {
        "Authorization": "Bearer " + token,
        "Connection": "upgrade",
        "Upgrade": "SPDY/4.8",
        "X-Stream-Protocol-Version": "channel.k8s.io",
        "charset": "utf-8"
    }

    # ThreadDump generation and compression for a pod.
    dump_command = f"threaddump.d/0.start_threaddump.sh > DUMP-1; sleep 3; threaddump.d/0.start_threaddump.sh > DUMP-2; sleep 5; threaddump.d/0.start_threaddump.sh > DUMP-3; tar -czvf ThreadDump.gz DUMP-1/ DUMP-2/ DUMP-3/"
    dump_command_encoded = urllib.parse.quote(dump_command, safe='')

    # Running the command on the target pod
    request_url = f'{url}/api/v1/namespaces/{namespace}/pods/{pod}/exec?'
    request_url += f'command=/bin/bash&command=-c&command={dump_command_encoded}'
    request_url += '&stdin=true&stderr=true&stdout=true&tty=false'

    data = []

    ws_destino = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
    ws_destino.connect(request_url.replace("https", "wss"), header=headers)
    while ws_destino.connected != False:
        recv = ws_destino.recv()
        if recv != '':
            data.append(recv.decode("utf-8"))

    login_command = ["oc", "login", "--token=" + token, "--server=" + url, "--namespace=" + namespace, "--insecure-skip-tls-verify=true"]
    login_process = subprocess.Popen(login_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Voy a intentar logarme en {url}, en el namespace {namespace}.")
    stderr = login_process.communicate()

    if login_process.returncode != 0:
        print(f"Login failed. Error message: {stderr}")
    else:
        print("Login succeeded.")
        try:
            process = subprocess.run(["oc", "rsync", "--delete", "{}:/opt/produban/ThreadDump.gz".format(pod), "."], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if process.returncode == 0:
                print("RSYNC command completed successfully")
                # Rename the generic pod´s name and move it to downloads´s folder.
                original_file= "ThreadDump.gz"
                new_file = await renaming_placing(namespace, pod, original_file, action)

                return FileResponse(f"/app/downloads/{namespace}/{new_file}", media_type="application/octet-stream", filename = new_file)
            else:
                print(f"RSYNC command failed with the message: {process.stderr}")

        except subprocess.CalledProcessError as e:
            print(e.output)
    #Close websocket    
    ws_destino.close()

    return data

async def generate_heapdump_DG(url, token, namespace, pod, action):
    headers = {
        "Authorization": "Bearer " + token,
        "Connection": "upgrade",
        "Upgrade": "SPDY/4.8",
        "X-Stream-Protocol-Version": "channel.k8s.io",
        "charset": "utf-8"
    }

    # Running the command on the target pod
    request_url = f'{url}/api/v1/namespaces/{namespace}/pods/{pod}/exec?'
    request_url += f'&stdin=true&stderr=true&stdout=true&tty=false'

    data = []

    ws_destino = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
    ws_destino.connect(request_url.replace("https", "wss"), header=headers)
    while ws_destino.connected != False:
        recv = ws_destino.recv()
        if recv != '':
            data.append(recv.decode("utf-8"))

    login_command = ["oc", "login", "--token=" + token, "--server=" + url, "--namespace=" + namespace, "--insecure-skip-tls-verify=true"]
    login_process = subprocess.Popen(login_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Voy a intentar logarme en {url}, en el namespace {namespace}.")
    stderr = login_process.communicate()

    if login_process.returncode != 0:
        print(f"Login failed. Error message: {stderr}")
    else:
        print("Login succeeded.")

        #Copy the dump to the destination pod and download it locally.
        try:
            #Identify pid´s process for JBOSS
            pid = await identify_pid(pod)
            
            # HeadDump generation and compression for a pod.
            exec_command = subprocess.run(["oc", "rsh", pod, "sh", "-c", "jmap -dump:format=b,file=/tmp/jvm.hprof {}; gzip -f -c /tmp/jvm.hprof > /tmp/jvm.hprof.gz".format(pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if exec_command.returncode == 0:
                print("El HeadDump se ha ejecutado bien en el pod")
                process = subprocess.run(["oc", "rsync", "{}:/tmp/jvm.hprof.gz".format(pod), "."], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if process.returncode == 0:
                    print("RSYNC command completed successfully")
                    # Rename the generic pod´s name and move it to downloads´s folder.
                    original_file= "jvm.hprof.gz"
                    new_file = await renaming_placing(namespace, pod, original_file, action)
                    
                    return FileResponse(f"/app/downloads/{namespace}/{new_file}", media_type="application/octet-stream", filename = new_file)
                else:
                    print(f"RSYNC command failed with the message: {process.stderr}")
            else:
                print(f"Exec command failed with the message: {exec_command.stderr}")
        except subprocess.CalledProcessError as e:
            print(e.output)

    #Close websocket    
    ws_destino.close()

    return data

async def generate_threaddump_DG(url, token, namespace, pod, action):
    headers = {
        "Authorization": "Bearer " + token,
        "Connection": "upgrade",
        "Upgrade": "SPDY/4.8",
        "X-Stream-Protocol-Version": "channel.k8s.io",
        "charset": "utf-8"
    }

    # Running the command on the target pod
    request_url = f'{url}/api/v1/namespaces/{namespace}/pods/{pod}/exec?'
    request_url += f'&stdin=true&stderr=true&stdout=true&tty=false'

    data = []

    ws_destino = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
    ws_destino.connect(request_url.replace("https", "wss"), header=headers)
    while ws_destino.connected != False:
        recv = ws_destino.recv()
        if recv != '':
            data.append(recv.decode("utf-8"))

    login_command = ["oc", "login", "--token=" + token, "--server=" + url, "--namespace=" + namespace, "--insecure-skip-tls-verify=true"]
    login_process = subprocess.Popen(login_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Voy a intentar logarme en {url}, en el namespace {namespace}.")
    stderr = login_process.communicate()

    if login_process.returncode != 0:
        print(f"Login failed. Error message: {stderr}")
    else:
        print("Login succeeded.")
        try:
            #Identify pid´s process for JBOSS
            pid = await identify_pid(pod)
            
            # ThreadDump generation and compression for a pod.
            exec_command = subprocess.run(["oc", "rsh", pod, "sh", "-c", "for i in $(seq 1 10); do jstack -l {} >> /tmp/jstack.out; sleep 2; done; gzip -f -c /tmp/jstack.out > /tmp/jstack.out.gz".format(pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if exec_command.returncode == 0:
                print("ThreadDump´s execution is success finished")
                process = subprocess.run(["oc", "rsync", "{}:/tmp/jstack.out.gz".format(pod), "."], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if process.returncode == 0:
                    print("RSYNC command completed successfully")
                    # Rename the generic pod´s name and move it to downloads´s folder.
                    original_file= "jstack.out.gz"
                    new_file = await renaming_placing(namespace, pod, original_file, action)

                    return FileResponse(f"/app/downloads/{namespace}/{new_file}", media_type="application/octet-stream", filename = new_file)
                else:
                    print(f"RSYNC command failed with the message: {process.stderr}")
            else:
                print(f"Exec command failed with the message: {exec_command.stderr}")
        except subprocess.CalledProcessError as e:
            print(e.output)
    #Close websocket    
    ws_destino.close()

    return data

async def getHeapdump (functionalEnvironment, cluster , region, namespace, pod, action):
    client = OpenshiftClient(entityID="spain")
    url = client.clusters[functionalEnvironment][cluster][region]["url"]
    token =  client.clusters[functionalEnvironment][cluster][region]["token"]

    if action =="1":
        print("#####################################################################")
        print(f'Voy a obtener un HeapDump del pod {pod} del namespace {namespace}')
        print(f'Y para eso ya tengo instanciado el cliente y tengo la url: {url} y mi token {token}')
        print("#####################################################################")
        data_obtained = await generate_heapdump(url, token, namespace, pod[0], action)
        #delete = await clean_old_files()
        #print(f"Files deleted because they´re 7 days older: {delete}")
        return data_obtained
    elif action =="2":
        print("#####################################################################")
        print(f'Voy a obtener un ThreadDump del pod {pod} del namespace {namespace}')
        print(f'Y para eso ya tengo instanciado el cliente y tengo la url: {url} y mi token {token}')
        print("#####################################################################")
        data_obtained = await generate_threaddump(url, token, namespace, pod[0], action)
        #delete = await clean_old_files()
        #print(f"Files deleted because they´re 7 days older: {delete}")
        return data_obtained
    elif action =="3":
        print("#####################################################################")
        print(f'Voy a obtener un HeapDump del Datagrid {pod} del namespace {namespace}')
        print(f'Y para eso ya tengo instanciado el cliente y tengo la url: {url} y mi token {token}')
        print("#####################################################################")
        data_obtained = await generate_heapdump_DG(url, token, namespace, pod[0], action)
        #delete = await clean_old_files()
        #print(f"Files deleted because they´re 7 days older: {delete}")
        return data_obtained
    elif action =="4":
        print("#####################################################################")
        print(f'Voy a obtener un ThreadDump del Datagrid {pod} del namespace {namespace}')
        print(f'Y para eso ya tengo instanciado el cliente y tengo la url: {url} y mi token {token}')
        print("#####################################################################")
        data_obtained = await generate_threaddump_DG(url, token, namespace, pod[0], action)
        #delete = await clean_old_files()
        #print(f"Files deleted because they´re 7 days older: {delete}")
        return data_obtained
    else:
        print("The 'ACTION' parameter has not been set or has a invalid value")