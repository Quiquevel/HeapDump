from fastapi import APIRouter, HTTPException, Header, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel, validator
from functions.utils import get_podnames, get_microservices, get_namespaces
from functions.heapdump import getHeapdump
from shuttlelib.middleware.authorization import is_devops_knowledge
from functions.historical import get_hist_dumps, get_download_dump
from fastapi.responses import StreamingResponse
from typing import List

bearer = HTTPBearer()

pod_exec = APIRouter(tags=["v1"])
class heapDumpModel(BaseModel):
    functionalEnvironment: str
    cluster: str
    region: str
    namespace: str
    pod: list
    action: str
    ldap: str
    delete: bool=False

    @validator("functionalEnvironment")
    def validate_environment(cls, v):
        if not any(x in v for x in ["dev","pre","pro"]):
            raise HTTPException(status_code=400, detail=f"{v} value is not valid for functionalEnvironment")
        return v
    
    #To validate the cluster parameter.
    @validator("cluster")
    def validate_cluster(cls, v):
        if not any(x in v for x in ["ohe","bks","probks","dmzbbks","azure","prodarwin","dmzbdarwin","proohe","dmzbohe","confluent"]):
            raise HTTPException(status_code=400, detail=f"{v} value is not valid for cluster")
        return v
    
    @validator("namespace")
    def validate_namespace(cls,v):
        return v
    
    #to validate the region parameter
    @validator("region")
    def validate_region(cls, v):
        if not any(x in v for x in ["bo1","bo2","weu1","weu2"]):
            raise HTTPException(status_code=400, detail=f"{v} value is not valid for region")
        return v
    
#Calling to the principal function
@pod_exec.post("/heapdump")
async def execute_heapdump(target: heapDumpModel, Authorization: str = Depends(bearer)):
    devops = await is_devops_knowledge(token=Authorization.credentials, uid=target.ldap)
    if devops == False:
        raise HTTPException(status_code=403, detail="User not authorized")
    return await getHeapdump(functionalEnvironment=target.functionalEnvironment, cluster=target.cluster, region=target.region, namespace=target.namespace, pod=target.pod, action=target.action, delete=target.delete)

class namespace_list(BaseModel):
    functionalEnvironment: str
    cluster: str
    region: str
    ldap: str

@pod_exec.post("/namespace_list")
async def get_namespace_list(target: namespace_list, Authorization: str = Depends(bearer)):  
    devops = await is_devops_knowledge(token=Authorization.credentials, uid=target.ldap)
    if devops == False:
        raise HTTPException(status_code=403, detail="User not authorized")
    return await get_namespaces(functionalEnvironment=target.functionalEnvironment, cluster=target.cluster, region=target.region)

class MicroserviceList(BaseModel):
    functionalEnvironment: str
    cluster: str
    region: str
    namespace: str
    ldap: str

@pod_exec.post("/microservices_list")
async def get_microservice_list(target: MicroserviceList, Authorization: str = Depends(bearer)):
    devops = await is_devops_knowledge(token=Authorization.credentials, uid=target.ldap)
    if devops == False:
        raise HTTPException(status_code=403, detail="User not authorized")
    return await get_microservices(functionalEnvironment=target.functionalEnvironment, cluster=target.cluster, region=target.region, namespace=target.namespace)

class PodList(BaseModel):
    functionalEnvironment: str
    cluster: str
    region: str
    namespace: str
    microservices: str
    ldap: str

@pod_exec.post("/pod_list")
async def get_pod_list(target: PodList, Authorization: str = Depends(bearer)):
    devops = await is_devops_knowledge(token=Authorization.credentials, uid=target.ldap)
    if devops == False:
        raise HTTPException(status_code=403, detail="User not authorized")
    return await get_podnames(functionalEnvironment=target.functionalEnvironment, cluster=target.cluster, region=target.region, namespace=target.namespace, microservices=target.microservices)

class HistDump(BaseModel):
    namespace: str
    ldap: str

@pod_exec.post("/historical_dumps")
async def recover_hist_dumps(target: HistDump, Authorization: str = Depends(bearer)):
    devops = await is_devops_knowledge(token=Authorization.credentials, uid=target.ldap)
    if devops == False:
        raise HTTPException(status_code=403, detail="User not authorized")
    return await get_hist_dumps(namespace=target.namespace)

class DownloadDump(BaseModel):
    namespace: str
    file_name: str
    ldap: str

@pod_exec.post("/download_dump")
async def download_dump(target: DownloadDump, Authorization: str = Depends(bearer)):
    devops = await is_devops_knowledge(token=Authorization.credentials, uid=target.ldap)
    if devops == False:
        raise HTTPException(status_code=403, detail="User not authorized")
    return await get_download_dump(namespace=target.namespace, file_name=target.file_name)