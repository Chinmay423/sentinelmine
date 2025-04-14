from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

from core.config import settings
from core.logging import get_request_logger

logger = get_request_logger()

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        for header_name, header_value in settings.SECURITY_HEADERS.items():
            response.headers[header_name] = header_value
            
        return response

class ContentSecurityPolicyMiddleware:
    """
    Middleware to add Content-Security-Policy headers with configurable policies
    """
    def __init__(self, app: ASGIApp):
        self.app = app
        
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = message.get("headers", [])
                headers.append(
                    (b"Content-Security-Policy", b"default-src 'self'; script-src 'self'; object-src 'none'; upgrade-insecure-requests;")
                )
                message["headers"] = headers
            await send(message)
            
        await self.app(scope, receive, send_wrapper)

class TLSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware to redirect HTTP requests to HTTPS in production
    """
    async def dispatch(self, request: Request, call_next):
        # Check if we're in production and the request is HTTP
        if (settings.API_ENV == "production" and 
            request.url.scheme == "http" and 
            request.headers.get("X-Forwarded-Proto") != "https"):
            
            url = request.url.replace(scheme="https")
            return Response(status_code=301, headers={"Location": str(url)})
            
        return await call_next(request)
        
class SecurityScanMiddleware(BaseHTTPMiddleware):
    """
    Middleware to detect and block potential security scanning attempts
    """
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # Common security scanner user agent patterns
        self.scanner_patterns = [
            "nmap", "nikto", "acunetix", "burp", "sqlmap", "metasploit",
            "hydra", "dirbuster", "gobuster", "zap", "w3af"
        ]
        
    async def dispatch(self, request: Request, call_next):
        # Check user agent for scanner patterns
        user_agent = request.headers.get("User-Agent", "").lower()
        
        for pattern in self.scanner_patterns:
            if pattern in user_agent:
                logger.warning(
                    f"Potential security scanner detected",
                    extra={
                        "ip": request.client.host,
                        "user_agent": user_agent,
                        "pattern": pattern,
                        "path": request.url.path
                    }
                )
                return Response(
                    status_code=403,
                    content="Access Denied",
                    media_type="text/plain"
                )
                
        # Check for common SQL injection patterns
        path = request.url.path.lower()
        query = request.url.query.lower()
        combined = f"{path}?{query}"
        
        sql_patterns = ["'--", "union select", "exec(", "eval(", "1=1"]
        for pattern in sql_patterns:
            if pattern in combined:
                logger.warning(
                    f"Potential SQL injection attempt detected",
                    extra={
                        "ip": request.client.host,
                        "path": request.url.path,
                        "query": request.url.query,
                        "pattern": pattern
                    }
                )
                return Response(
                    status_code=403,
                    content="Access Denied",
                    media_type="text/plain"
                )
                
        return await call_next(request) 