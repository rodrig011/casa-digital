"""Corre la CLI de Harvey en la nube de Claude, donde la única salida a internet
es el proxy del entorno. Harvey abre las páginas de los negocios sin proxy (a
propósito); aquí se cambia ese cliente por uno que sí usa el proxy y que sigue
rechazando direcciones locales por nombre."""
import sys, httpx
import harvey.public_http as ph

class _Guard(httpx.AsyncBaseTransport):
    def __init__(self):
        self._t = httpx.AsyncHTTPTransport(trust_env=True, verify="/root/.ccr/ca-bundle.crt",
                                           proxy=__import__("os").environ.get("HTTPS_PROXY"))
    async def handle_async_request(self, request):
        host = request.url.host.lower().rstrip(".")
        if request.url.scheme not in ("http", "https") or host in ("localhost",) or host.endswith(".localhost"):
            raise ph.UnsafeURLError("Only public HTTP(S) websites are allowed", request=request)
        try:
            ph._public_address(host)
        except ValueError as e:
            if "does not appear" not in str(e):
                raise ph.UnsafeURLError("non-public address", request=request)
        return await self._t.handle_async_request(request)
    async def aclose(self):
        await self._t.aclose()

def public_http_client(*, timeout=15.0, headers=None):
    return httpx.AsyncClient(transport=_Guard(), timeout=timeout, headers=headers,
                             follow_redirects=True, max_redirects=10)

ph.public_http_client = public_http_client
for mod in ("harvey.agents.scout", "harvey.collectors.profile", "harvey.trainer"):
    __import__(mod); sys.modules[mod].public_http_client = public_http_client

if __name__ == "__main__":
    from harvey.cli import main
    sys.exit(main())
