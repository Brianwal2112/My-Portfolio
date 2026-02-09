"""Compatibility shim for imghdr module removed in Python 3.13"""
import os

def what(file, h=None):
    if h is None:
        with open(file, 'rb') as f:
            h = f.read(32)
    for test in (jpeg, png, gif, tiff):
        res = test(h)
        if res:
            return res
    return None

def jpeg(h):
    if h[:2] == b'\xff\xd8':
        return 'jpeg'
    return None

def png(h):
    if h[:8] == b'\x89PNG\r\n\x1a\n':
        return 'png'
    return None

def gif(h):
    if h[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'
    return None

def tiff(h):
    if h[:4] in (b'MM\x00*', b'II*\x00'):
        return 'tiff'
    return None

tests = [jpeg, png, gif, tiff]
