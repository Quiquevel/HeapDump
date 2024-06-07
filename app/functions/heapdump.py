from shuttlelib.openshift.client import OpenshiftClient
from urllib3.exceptions import InsecureRequestWarning
from fastapi.responses import FileResponse, JSONResponse
from functions.utils import delete_pod, rename_and_move_files, get_my_pid, websocket_connection, automatic_delete
from shuttlelib.utils.logger import get_Logger
import urllib3, urllib.parse, subprocess, datetime

urllib3.disable_warnings(InsecureRequestWarning)
logger = get_Logger()

async def generate_heapdump(url, token, namespace, pod, action, delete):
    # Heapdump generation and compression
    dump_command = "jcmd 1 GC.heap_dump /opt/produban/heapdumpPRO; gzip -f heapdumpPRO"
    dump_command_encoded = urllib.parse.quote(dump_command, safe='')

    # Running the command on the target pod
    request_url = f'{url}/api/v1/namespaces/{namespace}/pods/{pod}/exec?'
    request_url += f'command=/bin/bash&command=-c&command={dump_command_encoded}'
    request_url += '&stdin=true&stderr=true&stdout=true&tty=false'

    ws_connect, data = await websocket_connection(token, request_url)

    if data is None:
        logger.info("Data is empty")
        return JSONResponse(content={"status": "error", "message": "Required tools jcmd and jmap are not available in the pod."})
    else:
        logger.info("Data contains data")

    login_command = ["oc", "login", "--token=" + token, "--server=" + url, "--namespace=" + namespace, "--insecure-skip-tls-verify=true"]
    login_process = subprocess.Popen(login_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logger.info(f"Voy a intentar logarme en {url}, en el namespace {namespace}.")
    stderr = login_process.communicate()

    if login_process.returncode != 0:
        logger.error(f"Login failed. Error message {stderr}")
        return  # Early return if login fails
    else:
        logger.info("LOGIN SUCCEEDED")

    try:
        process = subprocess.run(["oc", "rsync", "--delete", "{}:/opt/produban/heapdumpPRO.gz".format(pod), "."], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
        if process.returncode == 0:
                logger.info("RSYNC command completed successfully")
                logger.info(f"Command output:\n{process.stdout}")
				# Rename the generic pod´s name and move it to downloads´s folder.
                original_file = "heapdumpPRO.gz"
                new_file = await rename_and_move_files(namespace, pod, original_file, action)
                
                if delete:
                    delete_pod(pod)

                return FileResponse(f"/app/downloads/{namespace}/{new_file}", media_type="application/octet-stream", filename = new_file)																													 
        else:
                logger.error(f"RSYNC command failed with return code {process.returncode}")
                logger.error(f"Error output:\n{process.stderr}")

        if delete:
            delete_pod(pod)

        # Command to grant permissions
        permission_command = ["chmod", "-R", "755", "/app/downloads/"]
        subprocess.Popen(permission_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return process  # Ensure process is returned after successful operations

    except subprocess.CalledProcessError as e:
        logger.error(f"Error during heapdump generation: {e.output}")
    finally:
        # Ensure the websocket connection is closed even if an error occurs
        ws_connect.close()

async def generate_threaddump(url, token, namespace, pod, action, delete):
    # ThreadDump generation and compression for a pod.
    dump_command = "threaddump.d/0.start_threaddump.sh > DUMP-1; sleep 3; threaddump.d/0.start_threaddump.sh > DUMP-2; sleep 5; threaddump.d/0.start_threaddump.sh > DUMP-3; tar -czvf ThreadDump.gz DUMP-1/ DUMP-2/ DUMP-3/"
    dump_command_encoded = urllib.parse.quote(dump_command, safe='')

    # Running the command on the target pod
    request_url = f'{url}/api/v1/namespaces/{namespace}/pods/{pod}/exec?'
    request_url += f'command=/bin/bash&command=-c&command={dump_command_encoded}'
    request_url += '&stdin=true&stderr=true&stdout=true&tty=false'

    ws_connect, data = await websocket_connection(token, request_url)

    login_command = ["oc", "login", "--token=" + token, "--server=" + url, "--namespace=" + namespace, "--insecure-skip-tls-verify=true"]
    login_process = subprocess.Popen(login_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logger.info(f"Voy a intentar logarme en {url}, en el namespace {namespace}.")
    stderr = login_process.communicate()

    if login_process.returncode != 0:
        logger.error()(f"Login failed. Error message: {stderr}")
    else:
        logger.info("LOGIN SUCCEEDED")
        try:
            process = subprocess.run(["oc", "rsync", "--delete", "{}:/opt/produban/ThreadDump.gz".format(pod), "."], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if process.returncode == 0:
                logger.info("RSYNC command completed successfully")
                # Rename the generic pod´s name and move it to downloads´s folder.
                original_file= "ThreadDump.gz"
                new_file = await rename_and_move_files(namespace, pod, original_file, action)

                if delete:
                    delete_pod(pod)

                return FileResponse(f"/app/downloads/{namespace}/{new_file}", media_type="application/octet-stream", filename = new_file)
            else:
                logger.error(f"RSYNC command failed with the message: {process.stderr}")

        except subprocess.CalledProcessError as e:
            logger.error(f"{e.output}")
    #Close websocket    
    ws_connect.close()
    return data

async def generate_heapdump_DG(url, token, namespace, pod, action, delete):
    # Running the command on the target pod
    request_url = f'{url}/api/v1/namespaces/{namespace}/pods/{pod}/exec?'
    request_url += f'&stdin=true&stderr=true&stdout=true&tty=false'

    ws_connect, data = await websocket_connection(token, request_url)

    login_command = ["oc", "login", "--token=" + token, "--server=" + url, "--namespace=" + namespace, "--insecure-skip-tls-verify=true"]
    login_process = subprocess.Popen(login_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logger.info(f"Voy a intentar logarme en {url}, en el namespace {namespace}.")
    stderr = login_process.communicate()

    if login_process.returncode != 0:
        logger.error(f"Login failed. Error message: {stderr}")
    else:
        logger.info("Login succeeded.")

        #Copy the dump to the destination pod and download it locally.
        try:
            #Identify pid´s process for JBOSS
            pid = await get_my_pid(pod)
            
            # HeadDump generation and compression for a pod.
            exec_command = subprocess.run(["oc", "rsh", pod, "sh", "-c", "jmap -dump:format=b,file=/tmp/jvm.hprof {}; gzip -f -c /tmp/jvm.hprof > /tmp/jvm.hprof.gz".format(pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if exec_command.returncode == 0:
                logger.info("El HeadDump se ha ejecutado bien en el pod")
                process = subprocess.run(["oc", "rsync", "{}:/tmp/jvm.hprof.gz".format(pod), "."], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if process.returncode == 0:
                    logger.info("RSYNC command completed successfully")
                    # Rename the generic pod´s name and move it to downloads´s folder.
                    original_file= "jvm.hprof.gz"
                    new_file = await rename_and_move_files(namespace, pod, original_file, action)
                    
                    if delete:
                        delete_pod(pod)

                    return FileResponse(f"/app/downloads/{namespace}/{new_file}", media_type="application/octet-stream", filename = new_file)
                else:
                    logger.error(f"RSYNC command failed with the message: {process.stderr}")
            else:
                logger.error(f"Exec command failed with the message: {exec_command.stderr}")
        except subprocess.CalledProcessError as e:
            logger.error(f"{e.output}")

    #Close websocket    
    ws_connect.close()
    return data

async def generate_threaddump_DG(url, token, namespace, pod, action, delete):
    # Running the command on the target pod
    request_url = f'{url}/api/v1/namespaces/{namespace}/pods/{pod}/exec?'
    request_url += f'&stdin=true&stderr=true&stdout=true&tty=false'

    ws_connect, data = await websocket_connection(token, request_url)
    
    login_command = ["oc", "login", "--token=" + token, "--server=" + url, "--namespace=" + namespace, "--insecure-skip-tls-verify=true"]
    login_process = subprocess.Popen(login_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logger.info(f"Voy a intentar logarme en {url}, en el namespace {namespace}.")
    stderr = login_process.communicate()

    if login_process.returncode != 0:
        logger.error(f"Login failed. Error message: {stderr}")
    else:
        logger.info("Login succeeded.")
        try:
            #Identify pid´s process for JBOSS
            pid = await get_my_pid(pod)
            
            # ThreadDump generation and compression for a pod.
            exec_command = subprocess.run(["oc", "rsh", pod, "sh", "-c", "for i in $(seq 1 10); do jstack -l {} >> /tmp/jstack.out; sleep 2; done; gzip -f -c /tmp/jstack.out > /tmp/jstack.out.gz".format(pid)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if exec_command.returncode == 0:
                logger.info("ThreadDump´s execution is success finished")
                process = subprocess.run(["oc", "rsync", "{}:/tmp/jstack.out.gz".format(pod), "."], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if process.returncode == 0:
                    logger.info("RSYNC command completed successfully")
                    # Rename the generic pod´s name and move it to downloads´s folder.
                    original_file= "jstack.out.gz"
                    new_file = await rename_and_move_files(namespace, pod, original_file, action)

                if delete:
                    delete_pod(pod)

                    return FileResponse(f"/app/downloads/{namespace}/{new_file}", media_type="application/octet-stream", filename = new_file)
                else:
                    logger.error(f"RSYNC command failed with the message: {process.stderr}")
            else:
                logger.error(f"Exec command failed with the message: {exec_command.stderr}")
        except subprocess.CalledProcessError as e:
            logger.error(f"{e.output}")
    #Close websocket    
    ws_connect.close()
    return data

async def getHeapdump(functionalEnvironment, cluster , region, namespace, pod, action, delete):
    client = OpenshiftClient(entityID="spain")
    url = client.clusters[functionalEnvironment][cluster][region]["url"]
    token =  client.clusters[functionalEnvironment][cluster][region]["token"]

    if action =="1":
        automatic_delete()
        logger.info(f'Voy a obtener un HeapDump del pod {pod} del namespace {namespace}')
        logger.info(f'Y para eso tengo instanciado el cliente y tengo la url: {url} y mi token secreto')
        data_obtained = await generate_heapdump(url, token, namespace, pod[0], action,  delete)
        print("Vuelta de la función heapdump")
        return data_obtained
    elif action =="2":
        automatic_delete()
        logger.info(f'Voy a obtener un ThreadDump del pod {pod} del namespace {namespace}')
        logger.info(f'Y para eso tengo instanciado el cliente y tengo la url: {url} y mi token secreto')
        data_obtained = await generate_threaddump(url, token, namespace, pod[0], action, delete)
        return data_obtained
    elif action =="3":
        automatic_delete()
        logger.info(f'Voy a obtener un HeapDump del Datagrid {pod} del namespace {namespace}')
        logger.info(f'Y para eso tengo instanciado el cliente y tengo la url: {url} y mi token secreto')
        data_obtained = await generate_heapdump_DG(url, token, namespace, pod[0], action, delete)
        return data_obtained
    elif action =="4":
        automatic_delete()
        logger.info(f'Voy a obtener un ThreadDump del Datagrid {pod} del namespace {namespace}')
        logger.info(f'Y para eso tengo instanciado el cliente y tengo la url: {url} y mi token secreto')
        data_obtained = await generate_threaddump_DG(url, token, namespace, pod[0], action, delete)
        return data_obtained
    else:
        logger.error("The 'ACTION' parameter has not been set or has a invalid value")