#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import http.server
import socketserver
import html
import io
import os
import sys
import datetime
import urllib.parse
import logging
from optparse import OptionParser



logger_dir="./log"
img_dir="./img"
SUFFIX = urllib.parse.quote('.xhtml')
img_file=os.path.join(img_dir,'t.png')
logger_file=os.path.join(logger_dir,'work_log-{0}.{1}'.format(datetime.datetime.now().strftime("%Y.%m.%d_%H-%M-%S"),'log'))



class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        client_ip=str(self.client_address[0])
        logging.info('request from '+ client_ip)
        if self.path.endswith(SUFFIX):
            path = self.path.replace(SUFFIX, '')
            f = self.send_file_in_html(path)
        else:
            f = self.send_head()
        
        if f:
            self.copyfile(f, self.wfile)
            f.close()
    
    def send_file_in_html(self, path):
        enc = sys.getfilesystemencoding()
        path = self.translate_path(path)
        (dirname, filename) = os.path.split(path)
        try:
            list = os.listdir(dirname)
            list.sort(key=lambda a: a.lower())
        except os.error:
            list = []
        try:
            nextname = list[list.index(filename)+1] + SUFFIX
        except ValueError:
            self.send_error(404, "File not found")
            return None
        except IndexError:
            nextname = ''
        
        r=[]
        r.append('<html>')
        r.append('<head><meta http-equiv="Content-Type" content="text/html; charset=%s"></head>' % enc)
        r.append('<body><a href="%s"><img src="%s"></img></a></body>'\
            % (os.path.join('./',nextname), os.path.join('./',filename) ))
        r.append('</html>')
        
        encoded = '\n'.join(r).encode(enc)
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f

if __name__=='__main__':
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-ip", "--ip_addr", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(level=logging.DEBUG,filename=logger_file,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    httpd = socketserver.TCPServer((opts.ip_addr, opts.port), Handler)
    logging.info("Serving on %s" %opts.ip_addr)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.shutdown()
