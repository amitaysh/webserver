from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import socket
import cacheHandler
import config


class MyServer(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    # GET return requests count or just dummy request
    def do_GET(self):
        if self.path == '/count':
            requests_count = self.update_count()
            self._set_headers()
            response = json.dumps({'count': requests_count})
            response = bytes(response, 'utf-8')
            self.wfile.write(response)
        else:
            self.dummy_response()

    # POST request to simulate real requests or reset count
    def do_POST(self):
        if self.path == '/reset':
            self.update_count(reset=True)
            self._set_headers()
            response = json.dumps({'response': 'count reset'})
            response = bytes(response, 'utf-8')
            self.wfile.write(response)
        else:
            self.dummy_response()

    # if health check - don't increase count
    def dummy_response(self):
        if self.path != '/health':
            self.update_count()
        self._set_headers()
        response = json.dumps({'response': 'ok'})
        response = bytes(response, 'utf-8')
        self.wfile.write(response)

    @staticmethod
    def update_count(reset=False):
        cache = cacheHandler.Boto3Handler()
        if reset:
            cache.delete(config.webserver['count_key_name'])
            return
        try:
            requests_count = int(cache.pull(config.webserver['count_key_name']))
        except ValueError:
            requests_count = 0
        new_count = requests_count+1
        cache.push(config.webserver['count_key_name'], new_count)
        return new_count


def main():
    local_address = socket.gethostbyname(socket.gethostname())
    web_server = HTTPServer((local_address, config.webserver['server_port']), MyServer)
    print('Server started http://{}:{}'.format(local_address, config.webserver['server_port']))

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass

    web_server.server_close()
    print('Server stopped.')


if __name__ == "__main__":
    main()
