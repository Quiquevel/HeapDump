import uvicorn
from fastapi import FastAPI
from routes import openshift

description = """
FASTAPI BASE model de pruebas

### SUMMARY
With the help of this microservice, pod stack dumps can be pulled and downloaded.
Use:
The parameters and possible values are:

  "functionalEnvironment": “dev, pre, pro”
  "cluster": "ohe (only for dev & pre), bks (only for dev & pre), probks, dmzbbks, azure, prodarwin, dmzbdarwin, confluent, proohe, dmzbohe”
  "region": "bo1, bo2",
  "namespace": "pod's namespace",
  "pod": ["pod's name"],
  "action": "1, 2, 3, 4"

### ENDPOINTS

* **almastatus:** Obtener info de estado del POD de alma

### PARAMETERS
* **project**: namespaces's name
* **env**: ohe (only for dev & pre), bks (only for dev & pre), probks, dmzbbks, azure, prodarwin, dmzbdarwin, confluent, proohe, dmzbohe
* **namespace**: Pod's namespace
* **pod**: pod's name
* **action**: Action to perform (1 - HeapDump, 2 - ThreadDump, 3 - HeapDump DataGrid, 4 - ThreadDump DataGrid)

### REPO 
* [FASTAPI-BASE](https://github.alm.europe.cloudcenter.corp/sanes-shuttle/fastapi-base)
"""
tags_healthcheck = [
    {
        "name" : "POD's DUMPS",
        "description" :"Uso para sacar HeapDumps/ThreadDumps de pods."
    },
    {
        "name" : "healthcheck",
        "description" : "Uso para status del servicio en el POD" 
    }    
]
app = FastAPI(
                docs_url="/api/v1/dumps",
                title="shuttle-openshift-heapdump",
                description = description,
                version="1.0.6",
                openapi_url="/api/v1/openapi.json",
                contact={ "name" : "SRE CoE DevSecOps","email" : "SRECoEDevSecOps@gruposantander.com"},
              )

app.include_router(openshift.pod_exec, prefix="/dumps", tags=["v1"])

@app.get("/health", tags=["healthcheck"])
async def healthcheck():
    return "SERVER OK"

#COMENTAR PARA DESPLEGAR EN OPENSHIFT
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True, workers=2, timeout_keep_alive=600)