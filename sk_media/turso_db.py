"""turso_db.py — sqlite3-compatible connection layer backed by Turso (libsql-client).

Usage: `import turso_db as sqlite3` (drop-in for the subset of the sqlite3 API used here).

Environment:
  TURSO_DATABASE_URL        libsql://<db>-<org>.turso.io   (used for every DB file)
  TURSO_AUTH_TOKEN          Turso auth token
  TURSO_URL_<STEM>          optional per-file override, e.g. TURSO_URL_SETTINGS for settings.db
  TURSO_TOKEN_<STEM>        optional per-file token override
  TURSO_DISABLED=1          force local sqlite (debug)

If no Turso URL is configured, falls back to local sqlite3 so the bots still start.
"""
import logging
import os
import sqlite3 as _sqlite3
import threading
from pathlib import Path

log = logging.getLogger("turso_db")

Error = _sqlite3.Error
OperationalError = _sqlite3.OperationalError
IntegrityError = _sqlite3.IntegrityError
DatabaseError = _sqlite3.DatabaseError
Row = _sqlite3.Row

_clients = {}
_lock = threading.Lock()


def _settings_for(path):
    stem = Path(str(path)).stem.upper().replace("-", "_")
    url = os.environ.get("TURSO_URL_" + stem) or os.environ.get("TURSO_DATABASE_URL")
    token = os.environ.get("TURSO_TOKEN_" + stem) or os.environ.get("TURSO_AUTH_TOKEN")
    return url, token


def _get_client(url, token):
    with _lock:
        cli = _clients.get((url, token))
        if cli is None:
            import libsql_client
            # https:// is more robust than websockets behind mobile NAT / proxies
            http_url = url.replace("libsql://", "https://", 1)
            cli = libsql_client.create_client_sync(http_url, auth_token=token)
            _clients[(url, token)] = cli
        return cli


class _Cursor:
    def __init__(self, conn):
        self._conn = conn
        self._rows = []
        self._pos = 0
        self.rowcount = -1
        self.lastrowid = None
        self.description = None

    def execute(self, sql, params=()):
        rs = self._conn._client.execute(sql, list(params) if params else [])
        self._rows = [tuple(r) for r in rs.rows]
        self._pos = 0
        self.rowcount = rs.rows_affected if rs.rows_affected is not None else -1
        self.lastrowid = rs.last_insert_rowid
        cols = list(rs.columns or [])
        self.description = tuple((c, None, None, None, None, None, None) for c in cols) or None
        return self

    def executemany(self, sql, seq):
        total = 0
        for params in seq:
            self.execute(sql, params)
            total += max(self.rowcount, 0)
        self.rowcount = total
        return self

    def executescript(self, script):
        self._conn._client.batch([s.strip() for s in script.split(";") if s.strip()])
        return self

    def fetchone(self):
        if self._pos >= len(self._rows):
            return None
        row = self._rows[self._pos]
        self._pos += 1
        return row

    def fetchall(self):
        rows = self._rows[self._pos:]
        self._pos = len(self._rows)
        return rows

    def fetchmany(self, size=1):
        rows = self._rows[self._pos:self._pos + size]
        self._pos += len(rows)
        return rows

    def close(self):
        pass

    def __iter__(self):
        return iter(self.fetchall())


class _TursoConnection:
    row_factory = None  # accepted for compatibility; rows are plain tuples

    def __init__(self, url, token):
        self._client = _get_client(url, token)

    def cursor(self):
        return _Cursor(self)

    def execute(self, sql, params=()):
        return self.cursor().execute(sql, params)

    def executemany(self, sql, seq):
        return self.cursor().executemany(sql, seq)

    def executescript(self, script):
        return self.cursor().executescript(script)

    # Each statement auto-commits on the server.
    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def connect(path, timeout=5, *args, **kwargs):
    """Return a Turso connection when configured, otherwise a local sqlite3 one."""
    if os.environ.get("TURSO_DISABLED") != "1":
        url, token = _settings_for(path)
        if url:
            try:
                return _TursoConnection(url, token)
            except ImportError:
                log.error("libsql-client not installed; falling back to local sqlite (pip install libsql-client)")
            except Exception as e:
                log.error("Turso connect failed (%s); falling back to local sqlite", e)
    Path(str(path)).parent.mkdir(parents=True, exist_ok=True)
    return _sqlite3.connect(str(path), timeout=timeout, *args, **kwargs)
