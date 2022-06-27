server {
    listen 80;

    location / {
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
        include proxy_params;
        proxy_pass http://unix:/tmp/my-server/ipc.sock;
    }
}

