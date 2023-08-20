#!/usr/bin/env python3
import asyncio
import json
import os
import signal

PROXY_ID = os.getenv("PROXY_ID", "nrp1")
LOG_LEVEL = os.getenv("LOG_LEVEL", "debug")
SALT_MASTER = os.getenv("SALT_MASTER", True)
SALT_API = os.getenv("SALT_API", True)
SALT_PROXY = os.getenv("SALT_PROXY", True)
    
async def main():
    futures = []
    # check if need to start salt master process
    if SALT_MASTER:
        futures.append(await asyncio.create_subprocess_exec("salt-master", '-l', LOG_LEVEL))
    # check if need to start salt REST API process
    if SALT_MASTER and SALT_API:
        futures.append(await asyncio.create_subprocess_exec("salt-api", '-l', LOG_LEVEL))
    # check if need to start salt-proxy process
    if SALT_PROXY:
        futures.append(await asyncio.create_subprocess_exec("salt-proxy", f'--proxyid={PROXY_ID}', f'--log-level={LOG_LEVEL}', f'--log-file=/var/log/salt/proxy-{PROXY_ID}'))
    await asyncio.gather(*[future.communicate() for future in futures])

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    for signame in {"SIGINT", "SIGTERM"}:
        loop.add_signal_handler(getattr(signal, signame), loop.stop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()