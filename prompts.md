# Prompting

Ejemplos de prompting

## Generacion automatica de varias respuestas a partir de una inicial

> Dame una lista extensa de frameworks y librerias (internas y externas) de python.  Al final genera una lista separada por comas con cada nombre de libreria/framework.

Este prompt deberia devolver una LISTA al final.
> Django, Flask, NumPy, Pandas, Matplotlib, Scikit-learn, Requests, BeautifulSoup, Pygame, Cython, TensorFlow, Keras, PyTorch, OpenCV, scikit-image, Pillow, Sanic, FastAPI, Tornado, Twisted, cryptography, PyNaCl, OpenSSL, SSL/TLS, PyCrypto, Pycryptodome, Hashlib, HMAC, SHA-256, MD5, os, sys, pathlib, shutil, tempfile, filecmp, mimetypes, gzip, bz2, tarfile

La copiamos y usamos en el siguiente prompt:
> Genera un ejemplo de código completo con {variable} en python.
>
> variable=LISTA
