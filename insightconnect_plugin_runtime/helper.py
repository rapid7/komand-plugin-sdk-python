# -*- coding: utf-8 -*-
import base64
import hashlib
import logging
import os
import re
import ssl
import subprocess
import time
from io import IOBase
from urllib import request

import requests


def extract_value(begin, key, end, s):
    """
    Returns a string from a given key/pattern using provided regular expressions.

    It takes 4 arguments:
    * begin: a regex/pattern to match left side
    * key: a regex/pattern that should be the key
    * end: a regex/pattern to match the right side
    * s: the string to extract values from

    Example: The following will use pull out the /bin/bash from the string s
    s = '\nShell: /bin/bash\n'
    shell = get_value(r'\s', 'Shell', r':\s(.*)\s', s)

    This function works well when you have a list of keys to iterate through where the pattern is the same.
    """
    regex = begin + key + end
    r = re.search(regex, s)
    if hasattr(r, "group"):
        if r.lastindex == 1:
            return r.group(1)
    return None


def clean_dict(dictionary):
    """
    Returns a new but cleaned dictionary.

    * Keys with None type values are removed
    * Keys with empty string values are removed

    This function is designed so we only return useful data
    """

    newdict = dict(dictionary)
    for key in dictionary.keys():
        if dictionary.get(key) is None:
            del newdict[key]
        if dictionary[key] == "":
            del newdict[key]
    return newdict


def clean_list(lst):
    """
    Returns a new but cleaned list.

    * None type values are removed
    * Empty string values are removed

    This function is designed so we only return useful data
    """
    newlist = list(lst)
    for i in lst:
        if i is None:
            newlist.remove(i)
        if i == "":
            newlist.remove(i)
    return newlist


def clean(obj):
    """
    Returns a new but cleaned JSON object.

    * Recursively iterates through the collection
    * None type values are removed
    * Empty string values are removed

    This function is designed so we only return useful data
    """

    cleaned = clean_list(obj) if isinstance(obj, list) else clean_dict(obj)

    # The only *real* difference here is how we have to iterate through these different collection types
    if isinstance(cleaned, list):
        for key, value in enumerate(cleaned):
            if isinstance(value, list) or isinstance(value, dict):
                cleaned[key] = clean(value)
    elif isinstance(cleaned, dict):
        for key, value in cleaned.items():
            if isinstance(value, dict) or isinstance(value, list):
                cleaned[key] = clean(value)

    return cleaned


def get_hashes_string(s):
    """Return a dictionary of hashes for a string."""
    s = s.encode("utf-8")
    hashes = {
        "md5": hashlib.md5(s).hexdigest(),
        "sha1": hashlib.sha1(s).hexdigest(),
        "sha256": hashlib.sha256(s).hexdigest(),
        "sha512": hashlib.sha512(s).hexdigest(),
    }
    return hashes


def check_hashes(src, checksum):
    """Return boolean on whether a hash matches a file or string."""
    if type(src) is str:
        hashes = get_hashes_string(src)
    else:
        logging.error("CheckHashes: Argument must be a string")
        raise Exception("CheckHashes")
    for alg in hashes:
        if hashes[alg] == checksum:
            return True
    logging.info("CheckHashes: No checksum match")
    return False


def check_cachefile(cache_file):
    """Return boolean on whether cachefile exists."""
    cache_dir = "/var/cache"
    if cache_dir not in cache_file:
        cache_file = cache_dir + "/" + cache_file
    if os.path.isdir(cache_dir):
        if os.path.isfile(cache_file):
            logging.info("CheckCacheFile: File %s exists", cache_file)
            return True
        logging.info("CheckCacheFile: File %s did not exist", cache_file)
    return False


def open_file(file_path):
    """Return file object if it exists."""
    dirname = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    if os.path.isdir(dirname):
        if os.path.isfile(file_path):
            f = open(file_path, "rb")
            if isinstance(f, IOBase):
                return f
            return None
        else:
            logging.info("OpenFile: File %s is not a file or does not exist ", filename)
    else:
        logging.error(
            "OpenFile: Directory %s is not a directory or does not exist", dirname
        )


def open_cachefile(cache_file, append=False):
    """Return file object if cachefile exists, create and return new cachefile if it doesn't exist."""
    cache_dir = "/var/cache"
    if cache_dir not in cache_file:
        cache_file = cache_dir + "/" + cache_file
    if os.path.isdir(cache_dir):
        if os.path.isfile(cache_file):
            f = open(cache_file, "a+" if append else "r+")
            logging.info("OpenCacheFile: %s exists, returning it", cache_file)
        else:
            if not os.path.isdir(os.path.dirname(cache_file)):
                os.makedirs(os.path.dirname(cache_file))
            f = open(cache_file, "w+")  # Open once to create the cache file
            f.close()
            logging.info("OpenCacheFile: %s created", cache_file)
            f = open(cache_file, "a+" if append else "r+")
        return f
    logging.error("OpenCacheFile: %s directory or does not exist", cache_dir)


def remove_cachefile(cache_file):
    """Returns boolean on whether cachefile was removed."""
    cache_dir = "/var/cache"
    if cache_dir not in cache_file:
        cache_file = cache_dir + "/" + cache_file
    if os.path.isdir(cache_dir):
        if os.path.isfile(cache_file):
            os.remove(cache_file)
            return True
        logging.info("RemoveCacheFile: Cache file %s did not exist", cache_file)
    return False


def lock_cache(lock_file):
    """Returns boolean on whether lock was created."""
    lock_dir = "/var/cache/lock"
    if not os.path.isdir(lock_dir):
        os.makedirs(lock_dir)
    if not lock_file.startswith("/"):
        lock_file = lock_dir + "/" + lock_file
    if os.path.isdir(lock_dir):
        while os.path.isfile(lock_file):
            pass
        if not os.path.isdir(os.path.dirname(lock_file)):
            os.makedirs(os.path.dirname(lock_file))
        f = open(lock_file, "w")
        f.close()
        logging.info("Cache lock %s created", lock_file)
        return True
    logging.info("Cache lock %s failed, lock not created", lock_file)
    return False


def unlock_cache(lock_file, wait_time):
    """
    Returns boolean on whether lock was released.

    Wait_time value used to wait before unlocking and is measured in seconds
    """
    lock_dir = "/var/cache/lock"
    if not lock_file.startswith("/"):
        lock_file = lock_dir + "/" + lock_file
    if os.path.isdir(lock_dir):
        if os.path.isfile(lock_file):
            time.sleep(wait_time)
            os.remove(lock_file)
            return True
        logging.info("Cache unlock %s failed, lock not released", lock_file)
    return False


def open_url(url, timeout=None, verify=True, **kwargs):
    """
    Returns a urllib.request object given a URL as a string.

    Optional parameters include
    * timeout - Timeout value for request as int
    * verify  - Certificate validation as boolean
    * headers - Add many headers as Header_Name='Val', Header_Name2='Val2'
    """
    req = request.Request(url)
    if type(kwargs) is dict:
        for key in kwargs.keys():
            header = key.replace("_", "-")
            req.add_header(header, kwargs[key])
    try:
        if verify:
            ctx = ssl.create_default_context(cafile=os.environ["SSL_CERT_FILE"])
            urlobj = request.urlopen(req, timeout=timeout, context=ctx)
        else:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            urlobj = request.urlopen(req, timeout=timeout, context=ctx)
        return urlobj
    except request.HTTPError as e:
        logging.error("HTTPError: %s for %s", str(e.code), url)
        if e.code == 304:
            return None
    except request.URLError as e:
        logging.error("URLError: %s for %s", str(e.reason), url)
    raise Exception("GetURL Failed")


def check_url(url):
    """
    Return boolean on whether we can access url successfully.

    We submit an HTTP HEAD request to check the status. This way we don't download the file for performance.
    If the server doesn't support HEAD we try a Range of bytes so we don't download the entire file.
    """
    resp = None
    try:
        # Try HEAD request first
        resp = requests.head(url)
        if 200 <= resp.status_code <= 399:
            return True

        # Try Range request as secondary option
        hrange = {"Range": "bytes=0-2"}
        req = request.Request(url, headers=hrange)
        ctx = ssl.create_default_context(cafile=os.environ["SSL_CERT_FILE"])
        resp = request.urlopen(req, context=ctx)
        if 200 <= resp.code <= 299:
            return True

    except requests.exceptions.HTTPError:
        logging.error(
            "Requests: HTTPError: status code %s for %s",
            str(resp.status_code) if resp else None,
            url,
        )
    except requests.exceptions.Timeout:
        logging.error("Requests: Timeout for %s", url)
    except requests.exceptions.TooManyRedirects:
        logging.error("Requests: TooManyRedirects for %s", url)
    except requests.ConnectionError:
        logging.error("Requests: ConnectionError for %s", url)
    return False


def exec_command(command):
    """Return dict with keys stdout, stderr, and return code of executed subprocess command."""
    try:
        p = subprocess.Popen(
            command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=True,
        )
        stdout = p.stdout.read()
        stderr = p.stderr.read()
        rcode = p.poll()
        return {"stdout": stdout, "stderr": stderr, "rcode": rcode}
    except OSError as e:
        logging.error(
            "SubprocessError: %s %s: %s", str(e.filename), str(e.strerror), str(e.errno)
        )
    raise Exception("ExecCommand")


def encode_string(s):
    """Returns a base64 encoded string given a string."""
    if type(s) is str:
        _bytes = base64.b64encode(s.encode("utf-8"))
        return _bytes
    return None


def encode_file(file_path):
    """Return a string of base64 encoded file provided as an absolute file path."""
    f = None
    try:
        f = open_file(file_path)
        if isinstance(f, IOBase):
            efile = base64.b64encode(f.read())
            return efile
        return None
    except (IOError, OSError) as e:
        logging.error("EncodeFile: Failed to open file: %s", e.strerror)
        raise Exception("EncodeFile")
    finally:
        if isinstance(f, IOBase):
            f.close()


def check_url_modified(url):
    """
    Return boolean on whether the url has been modified.

    We submit an HTTP HEAD request to check the status. This way we don't download the file for performance.
    """
    resp = None
    try:
        resp = requests.head(url)
        resp.raise_for_status()
        if resp.status_code == 304:
            return False
        if resp.status_code == 200:
            return True
    except requests.exceptions.HTTPError:
        logging.error(
            "Requests: HTTPError: status code %s for %s",
            str(resp.status_code) if resp else None,
            url,
        )
    except requests.exceptions.Timeout:
        logging.error("Requests: Timeout for %s", url)
    except requests.exceptions.TooManyRedirects:
        logging.error("Requests: TooManyRedirects for %s", url)
    except requests.ConnectionError:
        logging.error("Requests: ConnectionError for %s", url)
    return False


def get_url_content_disposition(headers):
    """Return filename as string from content-disposition by supplying requests headers."""
    # Dict is case-insensitive
    for key, value in headers.items():
        if key.lower() == "content-disposition":
            filename = re.findall("filename=(.+)", value)
            return str(filename[0].strip('"'))
    return None


def get_url_path_filename(url):
    """Return filename from url as string if we have a file extension, otherwise return None."""
    if url.find("/", 9) == -1:
        return None
    name = os.path.basename(url)
    try:
        for n in range(-1, -5, -1):
            if name[n].endswith("."):
                return name
    except IndexError:
        logging.error("Range: IndexError: URL basename is short: %s of %s", name, url)
        return None
    return None


def get_url_filename(url):
    """Return filename as string from url by content-disposition or url path, or return None if not found."""
    resp = None
    try:
        resp = requests.head(url)
        resp.raise_for_status()
        name = get_url_content_disposition(resp.headers)
        if name is not None:
            return name
        name = get_url_path_filename(url)
        if name is not None:
            return name
        return None
    except requests.exceptions.MissingSchema:
        logging.error("Requests: MissingSchema: Requires ftp|http(s):// for %s", url)
    except requests.exceptions.HTTPError:
        logging.error(
            "Requests: HTTPError: status code %s for %s",
            str(resp.status_code) if resp else None,
            url,
        )
    except requests.exceptions.Timeout:
        logging.error("Requests: Timeout for %s", url)
    except requests.exceptions.TooManyRedirects:
        logging.error("Requests: TooManyRedirects for %s", url)
    except requests.ConnectionError:
        logging.error("Requests: ConnectionError for %s", url)
