import json, socket, uuid, sys, base64
def run(cmd, args, timeout=120):
    s = socket.create_connection(("127.0.0.1", 59929), timeout=30)
    req = {"command": cmd, "args": args, "env": {}, "token": "1b094220-dced-4d90-8b22-fb038cfdfe32", "id": str(uuid.uuid4())}
    s.sendall((json.dumps(req) + "\n").encode())
    buf = b""
    stdout, stderr, code = [], [], None
    s.settimeout(timeout)
    while True:
        chunk = s.recv(65536)
        if not chunk:
            break
        buf += chunk
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            if not line.strip():
                continue
            msg = json.loads(line.decode())
            t = msg.get("type")
            if t == "stdout" and msg.get("data") is not None:
                stdout.append(base64.b64decode(msg["data"]))
            elif t == "stderr" and msg.get("data") is not None:
                stderr.append(base64.b64decode(msg["data"]))
            elif t in ("exit", "close"):
                code = msg.get("code", msg.get("exitCode"))
                s.close()
                return code, b"".join(stdout), b"".join(stderr)
    s.close()
    return code, b"".join(stdout), b"".join(stderr)
cmd, *args = sys.argv[1:]
c,o,e = run(cmd, args)
sys.stdout.buffer.write(o)
if e:
    sys.stderr.buffer.write(e)
sys.exit(0 if c in (0, None) else int(c))
