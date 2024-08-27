import sys
from http_s.http_server import run_server as run_http_server, Handler as HttpHandler
from http_s.proxy_server import run_server as run_proxy_server, Handler as ProxyHandler

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <proxy|https>")
        sys.exit(1)
    
    server_type = sys.argv[1]

    if server_type == "proxy":
        run_proxy_server("0.0.0.0", 4433, ProxyHandler.PROXY)
    elif server_type == "https":
        run_http_server("0.0.0.0", 4434, HttpHandler.TEST)
    else:
        print("Unknown server type. Use 'proxy' or 'https'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
