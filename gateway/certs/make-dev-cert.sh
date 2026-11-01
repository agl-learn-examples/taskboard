#!/bin/sh
# Makes a self-signed certificate for https://localhost, for practice on your laptop (Course A7).
# Self-signed means nobody vouches for it, so browsers warn and curl needs -k. A real site gets its
# certificate from a certificate authority such as Let's Encrypt. The files are in .gitignore: a private
# key never goes into git.
set -e
cd "$(dirname "$0")"
openssl req -x509 -newkey rsa:2048 -nodes -days 30 \
    -keyout localhost.key -out localhost.crt \
    -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
echo "Made gateway/certs/localhost.crt and gateway/certs/localhost.key (valid 30 days)"
