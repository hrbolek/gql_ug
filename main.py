import os
import asyncio
import socket

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from strawberry.fastapi import GraphQLRouter


import logging
import logging.handlers

from src.GraphTypeDefinitions import schema
from src.DBDefinitions import startEngine, ComposeConnectionString
from src.DBFeeder import initDB, createGroupPaths

# region logging setup

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s.%(msecs)03d\t%(levelname)s:\t%(message)s', 
    datefmt='%Y-%m-%dT%I:%M:%S')
SYSLOGHOST = os.getenv("SYSLOGHOST", None)
if SYSLOGHOST is not None:
    [address, strport, *_] = SYSLOGHOST.split(':')
    assert len(_) == 0, f"SYSLOGHOST {SYSLOGHOST} has unexpected structure, try `localhost:514` or similar (514 is UDP port)"
    port = int(strport)
    my_logger = logging.getLogger()
    my_logger.setLevel(logging.INFO)
    handler = logging.handlers.SysLogHandler(address=(address, port), socktype=socket.SOCK_DGRAM)
    #handler = logging.handlers.SocketHandler('10.10.11.11', 611)
    my_logger.addHandler(handler)


# endregion

# region DB setup

connectionString = ComposeConnectionString()

def singleCall(asyncFunc):
    """Dekorator, ktery dovoli, aby dekorovana funkce byla volana (vycislena) jen jednou. Navratova hodnota je zapamatovana a pri dalsich volanich vracena.
    Dekorovana funkce je asynchronni.
    """
    resultCache = {}

    async def result():
        if resultCache.get("result", None) is None:
            resultCache["result"] = await asyncFunc()
        return resultCache["result"]

    return result

@singleCall
async def RunOnceAndReturnSessionMaker():
    """Provadi inicializaci asynchronniho db engine, inicializaci databaze a vraci asynchronni SessionMaker.
    Protoze je dekorovana, volani teto funkce se provede jen jednou a vystup se zapamatuje a vraci se pri dalsich volanich.
    """

    makeDrop = os.getenv("DEMODATA", None) in ["True", "true"]
    logging.info(f'starting engine for "{connectionString} makeDrop={makeDrop}"')

    result = await startEngine(
        connectionstring=connectionString, makeDrop=makeDrop, makeUp=True
    )

    logging.info(f"initializing system structures")

    ###########################################################################################################################
    #
    # zde definujte do funkce asyncio.gather
    # vlozte asynchronni funkce, ktere maji data uvest do prvotniho konzistentniho stavu
    # await initDB(result)
    async def initAnd_(SessionMaker):
        await initDB(SessionMaker)
        await createGroupPaths(SessionMaker)
        print(f"data ready, paths created", flush=True)

    coroutine = initAnd_(result)
    asyncio.create_task(coroutine)
    
    #
    #
    ###########################################################################################################################
    logging.info(f"all done")
    return result

# endregion

# region API endpoints

from src.Dataloaders import createLoadersContext


async def get_context(request: Request):    
    result = {
        "request": request,
    }
    logging.info(f"context created {result}")
    return result

from uoishelpers.schema import SessionCommitExtensionFactory

schema.extensions.append(
    SessionCommitExtensionFactory(session_maker_factory=RunOnceAndReturnSessionMaker, loaders_factory=createLoadersContext)
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.DBFeeder import backupDB
    initizalizedEngine = await RunOnceAndReturnSessionMaker()
    yield
    await backupDB(initizalizedEngine)


app = FastAPI(lifespan=lifespan)
# app.mount("/gql", graphql_app)

from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app, metric_namespace="gql_ug").expose(app, endpoint="/metrics")

graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context
)

app.include_router(graphql_app, prefix="/gql")

@app.get("/voyager", response_class=FileResponse)
async def graphiql():
    realpath = os.path.realpath("./src/Htmls/voyager.html")
    return realpath

@app.get("/doc", response_class=FileResponse)
async def graphiql():
    realpath = os.path.realpath("./src/Htmls/liveschema.html")
    return realpath

@app.get("/ui", response_class=FileResponse)
async def graphiql():
    realpath = os.path.realpath("./src/Htmls/livedata.html")
    return realpath

@app.get("/test", response_class=FileResponse)
async def graphiql():
    realpath = os.path.realpath("./src/Htmls/tests.html")
    return realpath

logging.info("All initialization is done")

# from src.router.router import create_router_from_schema
# router = create_router_from_schema(schema)
# app.include_router(router, prefix="/ui")
# endregion

# region ENV setup tests
def envAssertDefined(name, default=None):
    result = os.getenv(name, None)
    assert result is not None, f"{name} environment variable must be explicitly defined"
    return result

DEMO = envAssertDefined("DEMO", None)
JWTPUBLICKEYURL = envAssertDefined("JWTPUBLICKEYURL", None)
JWTRESOLVEUSERPATHURL = envAssertDefined("JWTRESOLVEUSERPATHURL", None)
print(f"DEMO = {DEMO} is type {type(DEMO)}")
assert (DEMO in ["True", "true", "False", "false"]), "DEMO environment variable can have only `True` or `False` values"
DEMO = DEMO in ["True", "true"]

if DEMO:
    print("####################################################")
    print("#                                                  #")
    print("# RUNNING IN DEMO                                  #")
    print("#                                                  #")
    print("####################################################")

    logging.info("####################################################")
    logging.info("#                                                  #")
    logging.info("# RUNNING IN DEMO                                  #")
    logging.info("#                                                  #")
    logging.info("####################################################")
else:
    print("####################################################")
    print("#                                                  #")
    print("# RUNNING DEPLOYMENT                               #")
    print("#                                                  #")
    print("####################################################")

    logging.info("####################################################")
    logging.info("#                                                  #")
    logging.info("# RUNNING DEPLOYMENT                               #")
    logging.info("#                                                  #")
    logging.info("####################################################")    

logging.info(f"DEMO = {DEMO}")
logging.info(f"SYSLOGHOST = {SYSLOGHOST}")
logging.info(f"JWTPUBLICKEYURL = {JWTPUBLICKEYURL}")
logging.info(f"JWTRESOLVEUSERPATHURL = {JWTRESOLVEUSERPATHURL}")
# endregion