#!/usr/bin/env python3
"""Root-only, path-confined mover for HAOS /share -> /media publication."""
from __future__ import annotations

import argparse
import errno
import json
import os
import re
import shutil
import stat
import tempfile
import time
import uuid
from pathlib import Path, PurePosixPath

SHARE_ROOT = Path(os.environ.get("HERMES_STORAGE_SHARE_ROOT", "/share"))
MEDIA_ROOT = Path(os.environ.get("HERMES_STORAGE_MEDIA_ROOT", "/media"))
QUEUE_ROOT = Path(os.environ.get("HERMES_STORAGE_QUEUE_ROOT", "/run/hermes-storage"))
REQUESTS = QUEUE_ROOT / "requests"
RESULTS = QUEUE_ROOT / "results"
REQUEST_ID_RE = re.compile(r"^[a-f0-9]{32}$")


class StorageError(RuntimeError):
    pass


def relative_parts(value: object) -> tuple[str, ...]:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise StorageError("path must be a non-empty relative POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise StorageError("path traversal is not allowed")
    return path.parts


def open_dir(root: Path, parts: tuple[str, ...], create: bool = False) -> int:
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(root, flags)
    try:
        for part in parts:
            try:
                child = os.open(part, flags, dir_fd=fd)
            except FileNotFoundError:
                if not create:
                    raise StorageError(f"directory does not exist: {'/'.join(parts)}")
                os.mkdir(part, 0o775, dir_fd=fd)
                child = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except Exception:
        os.close(fd)
        raise


def open_regular(root: Path, parts: tuple[str, ...]) -> int:
    parent_fd = open_dir(root, parts[:-1])
    try:
        flags = os.O_RDONLY | os.O_CLOEXEC
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            fd = os.open(parts[-1], flags, dir_fd=parent_fd)
        except OSError as exc:
            if exc.errno == errno.ELOOP:
                raise StorageError("source may not be a symlink") from exc
            raise
    finally:
        os.close(parent_fd)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise StorageError("source must be a regular file")
        return fd
    except Exception:
        os.close(fd)
        raise


def move(parts: tuple[str, ...], replace: bool) -> dict:
    src_fd = open_regular(SHARE_ROOT, parts)
    target_parent_fd = open_dir(MEDIA_ROOT, parts[:-1], create=True)
    try:
        target_name = parts[-1]
        try:
            target_stat = os.stat(target_name, dir_fd=target_parent_fd, follow_symlinks=False)
            if stat.S_ISLNK(target_stat.st_mode):
                raise StorageError("destination may not be a symlink")
            if not replace:
                raise StorageError("destination exists; pass --replace to overwrite")
        except FileNotFoundError:
            pass

        temporary = f".{target_name}.hermes-moving-{uuid.uuid4().hex}"
        out_fd = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC,
            0o664,
            dir_fd=target_parent_fd,
        )
        size = 0
        try:
            with os.fdopen(src_fd, "rb", closefd=True) as source, os.fdopen(out_fd, "wb", closefd=True) as output:
                src_fd = -1
                out_fd = -1
                shutil.copyfileobj(source, output, length=1024 * 1024)
                size = output.tell()
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, target_name, src_dir_fd=target_parent_fd, dst_dir_fd=target_parent_fd)
        except Exception:
            if out_fd >= 0:
                os.close(out_fd)
            try:
                os.unlink(temporary, dir_fd=target_parent_fd)
            except FileNotFoundError:
                pass
            raise
    finally:
        if src_fd >= 0:
            os.close(src_fd)
        os.close(target_parent_fd)

    source_parent_fd = open_dir(SHARE_ROOT, parts[:-1])
    try:
        os.unlink(parts[-1], dir_fd=source_parent_fd)
    finally:
        os.close(source_parent_fd)
    return {"bytes": size, "path": "/".join(parts), "replaced": replace}


def remove_tree(parent_fd: int, name: str) -> None:
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(name, flags, dir_fd=parent_fd)
    try:
        for entry in os.scandir(fd):
            info = entry.stat(follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode):
                raise StorageError("refusing recursive removal through a symlink")
            if stat.S_ISDIR(info.st_mode):
                remove_tree(fd, entry.name)
            else:
                os.unlink(entry.name, dir_fd=fd)
    finally:
        os.close(fd)
    os.rmdir(name, dir_fd=parent_fd)


def remove(parts: tuple[str, ...], recursive: bool) -> dict:
    parent_fd = open_dir(MEDIA_ROOT, parts[:-1])
    try:
        info = os.stat(parts[-1], dir_fd=parent_fd, follow_symlinks=False)
        if stat.S_ISLNK(info.st_mode):
            raise StorageError("refusing to remove a symlink")
        if stat.S_ISDIR(info.st_mode):
            if not recursive:
                raise StorageError("destination is a directory; pass --recursive")
            remove_tree(parent_fd, parts[-1])
        else:
            os.unlink(parts[-1], dir_fd=parent_fd)
    finally:
        os.close(parent_fd)
    return {"path": "/".join(parts), "recursive": recursive}


def handle_request(request: dict) -> dict:
    request_id = request.get("id")
    if not isinstance(request_id, str) or not REQUEST_ID_RE.fullmatch(request_id):
        raise StorageError("invalid request id")
    parts = relative_parts(request.get("path"))
    operation = request.get("operation")
    if operation == "move":
        return move(parts, bool(request.get("replace", False)))
    if operation == "remove":
        return remove(parts, bool(request.get("recursive", False)))
    raise StorageError("operation must be move or remove")


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o640)
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def process_request(path: Path) -> None:
    try:
        with path.open("r", encoding="utf-8") as stream:
            request = json.load(stream)
        result = {"ok": True, "result": handle_request(request)}
        request_id = request["id"]
    except Exception as exc:
        request_id = path.stem
        result = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    atomic_json(RESULTS / f"{request_id}.json", result)
    path.unlink(missing_ok=True)


def serve() -> int:
    REQUESTS.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    while True:
        for request in sorted(REQUESTS.glob("*.json")):
            try:
                if request.is_symlink() or not request.is_file():
                    request.unlink(missing_ok=True)
                    continue
                process_request(request)
            except Exception as exc:
                print(f"[hermes-storage] request failure: {type(exc).__name__}: {exc}", flush=True)
        time.sleep(0.2)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true")
    args = parser.parse_args()
    if not args.serve:
        parser.error("only --serve is supported")
    return serve()


if __name__ == "__main__":
    raise SystemExit(main())
