from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import socket
import cacheHandler

hostName = "localhost"
serverPort = 8080
count_key_name = 'requests_count'


class MyServer(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    # GET return requests count
    def do_GET(self):
        if self.path == '/count':
            requests_count = self.increase_count()
            self._set_headers()
            response = json.dumps({'count': requests_count})
            response = bytes(response, 'utf-8')
            self.wfile.write(response)

    # POST request to simulate real requests
    def do_POST(self):
        self.increase_count()
        self._set_headers()
        response = json.dumps({'response': 'ok'})
        response = bytes(response, 'utf-8')
        self.wfile.write(response)

    def increase_count(self):
        cache = cacheHandler.Boto3Handler()
        try:
            requests_count = int(cache.pull(count_key_name))
        except ValueError:
            requests_count = 0
        new_count = requests_count+1
        cache.push(count_key_name, new_count)
        return new_count


def main():
    local_address = socket.gethostbyname(socket.gethostname())
    web_server = HTTPServer((local_address, serverPort), MyServer)
    print('Server started http://{}:{}'.format(local_address, serverPort))

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass

    web_server.server_close()
    print('Server stopped.')


if __name__ == "__main__":
    main()
