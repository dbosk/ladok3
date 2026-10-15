"""Privacy scrubbing and drift detection for VCR cassettes.

Copy this file into the project's tests/ directory next to conftest.py.
It has no dependencies beyond the standard library and PyYAML (which
vcrpy already requires).

Three jobs:

1. Pseudonymize identities (names, emails, logins, personnummer) at
   record time with a keyed HMAC, so the same person gets the same
   pseudonym everywhere and relationships in the data survive.
2. Find leaks: secret-looking strings, personal-data patterns, and any
   original value the pseudonymizer replaced during this recording.
3. Extract the *shape* of recorded responses (status, content type,
   JSON key paths and value types) so that a live re-recording can be
   compared with the committed one without ever printing a value.
"""

from __future__ import annotations

import gzip
import hashlib
import hmac
import json
import os
import re
import stat
import tempfile
import urllib.parse
from pathlib import Path
from typing import Any, Iterable, Iterator

KEY_ENV = "TEST_PSEUDONYM_KEY"
ORIGINALS_ENV = "TEST_ORIGINALS_FILE"

# Identity fields, matched case-insensitively at any depth of a JSON body.
# Extend per project; never shrink without a reason written next to it.
NAME_KEYS = {
    "sortable_name", "short_name", "display_name", "full_name",
    "first_name", "last_name", "given_name", "family_name", "surname",
    "firstname", "lastname", "fornamn", "efternamn", "author", "author_name",
    "user_name", "student_name", "teacher_name",
    "beslutsfattare",  # LADOK: who decided a result or credit transfer
}
# Keys such as "name" also name courses, repos and files.  They are
# pseudonymized only in person-shaped objects: objects that also carry an
# identity field above, or that sit under a key naming a person.  A person
# object outside these keys is caught by the denylist scan, so add the
# service's own keys here.
AMBIGUOUS_NAME_KEYS = {"name"}
PERSON_PARENT_KEYS = {
    "user", "users", "author", "authors", "owner", "owners", "grader",
    "assignee", "assignees", "submitter", "committer", "creator", "student",
    "students", "teacher", "teachers", "instructor", "instructors", "sender",
    "recipient", "recipients", "reviewer", "reviewers", "member", "members",
    "participant", "participants", "editor", "last_edited_by", "actor",
    "person", "people", "contributor", "contributors", "observer", "observers",
}
# An object with one of these "type" values is not a person (GitHub).
NON_PERSON_TYPES = {"organization", "bot"}
# The defaults include the Swedish keys of LADOK (Fornamn, Epostadress,
# SenastAndradAv: the staff member who last changed a record, ...).
EMAIL_KEYS = {
    "email", "primary_email", "login_email", "email_address", "mail",
    "epost", "epostadress", "senastandradav",
}
LOGIN_KEYS = {
    "login_id", "username", "login", "sis_user_id", "integration_id",
    "sis_login_id", "uid", "user_login", "anvandarnamn",
}
# Replaced by key, valid checksum or not (the text scan needs a valid one).
PNR_KEYS = {"personnummer", "samordningsnummer", "personal_identity_number", "ssn"}
# Postal address and phone: replaced wholesale, like free text.
CONTACT_KEYS = {
    "address", "street_address", "postal_address", "postal_code", "zip",
    "zip_code", "city", "phone", "phone_number", "mobile", "mobile_phone",
    "utdelningsadress", "coadress", "postnummer", "postort", "telefonnummer",
    "mobilnummer",
}
# Contact keys whose values are replaced but not logged as originals: a
# place name or postal code also names courses and fills code tables, so
# the leak scan would report every such mention.
UNLOGGED_CONTACT_KEYS = {"city", "postort", "postal_code", "zip", "zip_code", "postnummer"}
# Prose can mention anyone, so it is replaced wholesale.
FREE_TEXT_KEYS = {
    "body", "message", "comment", "comments", "text_comment", "description",
    "subject", "bio", "notes", "note", "signature",
    "anteckning", "kommentar", "meddelande",
}
# Identifier fields to pseudonymize, keeping the type (int stays int with
# the same number of digits).  Empty by default: replay matching breaks
# for tests that hard-code such an id in a request.  Enable for public
# services (e.g. GitHub user ids resolve to a person for anyone) and drive
# those tests from ids found in earlier responses instead.
ID_KEYS: set[str] = set()
# Fields that are dropped to a placeholder because they point at a person.
URL_IDENTITY_KEYS = {"avatar_url", "avatar_image_url", "profile_url", "photo_url"}

SECRET_HEADERS = [
    "authorization", "proxy-authorization", "cookie", "x-api-key",
    "x-auth-token", "private-token", "x-xsrf-token", "x-csrf-token",
    "x-csrftoken",
]
SECRET_RESPONSE_HEADERS = {"x-auth-token", "authorization"}
# Set-Cookie is kept with its values replaced: session services (LADOK's
# XSRF-TOKEN) need the cookie to exist in replay, not its value.
COOKIE_RESPONSE_HEADERS = {"set-cookie"}
SECRET_QUERY_PARAMS = [
    "access_token", "refresh_token", "id_token", "auth_token", "csrf_token",
    "session_token", "private_token", "token", "api_key", "apikey", "key",
    "client_secret", "password", "secret", "sig", "signature",
    # A SAML response is the signed identity of the user who logged in.
    "SAMLResponse", "SAMLart", "j_password",
]

FREE_TEXT_PLACEHOLDER = "[redacted free text]"
CONTACT_PLACEHOLDER = "[redacted contact]"
SECRET_PLACEHOLDER = "redacted"
URL_PLACEHOLDER = "https://example.invalid/redacted"
# RFC 2606 names: addresses there belong to nobody.
PLACEHOLDER_DOMAINS = ("example.invalid", "example.com", "example.org", "example.net")
PLACEHOLDER_TLDS = ("test", "example", "invalid", "localhost")

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+\.)+[A-Za-z]{2,}\b")
# Swedish personnummer/samordningsnummer: (CC)YYMMDD[-+]NNNN, validated below.
PNR_RE = re.compile(r"(?<!\d)(?:19|20)?(\d{2})(\d{2})(\d{2})[-+]?(\d{4})(?!\d)")
JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")
BEARER_RE = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{12,}")
ASSIGNED_SECRET_RE = re.compile(  # also access_token, csrf_token, ...
    r"(?i)(?<![A-Za-z0-9])(?:[a-z_-]*token|[a-z_-]*secret|api[_-]?key|password|passwd)"
    r"[\"']?\s*[:=]\s*[\"']?([A-Za-z0-9_\-./+=]{16,})"
    r"(?![A-Za-z0-9_\-./+=(])"  # a call (keyring.get_password(...)) is not a value
)
# SAMLResponse=..., "SAMLResponse": "...", or <input name="SAMLResponse" value="...">
SAML_RE = re.compile(
    r"(?i)SAML(?:Response|art)[\"']?(?:\s*[=:]\s*|[^>]{0,40}?value\s*=\s*)[\"']?"
    r"([A-Za-z0-9+/%]{40,}=*)")
UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
# Well-known fictive personnummer, not reported by the scan: Tolvan
# Tolvansson (Skatteverket's test identity).  Add more with --allow.
KNOWN_FICTIVE_PNR = {"1212121212"}


def _form_field_re(names: Iterable[str]) -> re.Pattern:
    alternation = "|".join(map(re.escape, names))
    return re.compile(  # name="X" ... value="v", or X=v in a form body
        rf'''(?i)(name\s*=\s*["']?(?:{alternation})["']?[^>]*?value\s*=\s*["']?)([^"'>\s]+)'''
        rf"|((?:^|&)(?:{alternation})=)([^&\s]+)")


SECRET_FORM_RE = _form_field_re(SECRET_QUERY_PARAMS)


def is_placeholder_email(address: str) -> bool:
    domain = address.rsplit("@", 1)[-1].lower().rstrip(".")
    if domain.rsplit(".", 1)[-1] in PLACEHOLDER_TLDS:
        return True
    return any(domain == d or domain.endswith("." + d) for d in PLACEHOLDER_DOMAINS)


def luhn_ok(digits: str) -> bool:
    total = 0
    for i, ch in enumerate(digits):
        d = int(ch) * (2 if i % 2 == 0 else 1)
        total += d - 9 if d > 9 else d
    return total % 10 == 0


def is_personnummer(match: re.Match) -> bool:
    yy, mm, dd, tail = match.groups()
    day = int(dd)
    if not 1 <= int(mm) <= 12:
        return False
    if not (1 <= day <= 31 or 61 <= day <= 91):  # 61-91: samordningsnummer
        return False
    return luhn_ok(yy + mm + dd + tail)


def personnummer_spans(text: str) -> list[tuple[int, int]]:
    return [m.span() for m in PNR_RE.finditer(text) if is_personnummer(m)]


def private_dir() -> Path:
    """A directory only we can enter: $XDG_RUNTIME_DIR, else one in the temp dir.

    The temp dir is shared on multi-user machines, so a predictable file
    name there could be created first by someone else.
    """
    runtime = os.environ.get("XDG_RUNTIME_DIR")
    base = Path(runtime) if runtime and Path(runtime).is_dir() else Path(tempfile.gettempdir())
    directory = base / f"vcr-originals-{os.getuid()}"
    directory.mkdir(mode=0o700, exist_ok=True)
    info = os.lstat(directory)
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() \
            or stat.S_IMODE(info.st_mode) & 0o077:
        raise PermissionError(f"{directory} is not a private directory of ours")
    return directory


def default_originals_path(root: str | os.PathLike = ".") -> Path:
    """A per-project file outside the repository, readable only by us."""
    tag = hashlib.sha256(str(Path(root).resolve()).encode()).hexdigest()[:10]
    return private_dir() / f"{tag}.txt"


class Pseudonymizer:
    """Replace identities with stable pseudonyms and remember the originals.

    The same input always yields the same pseudonym for a given key, so
    "Anna Svensson" in one endpoint and "Svensson, Anna" in another map to
    the same "Person-3f9a1c".  Every replaced original is appended to
    `originals_path` (mode 0600, outside the repo) so a later scan can
    prove none of them reached a cassette.
    """

    def __init__(self, key: bytes, originals_path: Path | None = None,
                 name_keys: Iterable[str] = NAME_KEYS,
                 email_keys: Iterable[str] = EMAIL_KEYS,
                 login_keys: Iterable[str] = LOGIN_KEYS,
                 free_text_keys: Iterable[str] = FREE_TEXT_KEYS,
                 url_identity_keys: Iterable[str] = URL_IDENTITY_KEYS,
                 id_keys: Iterable[str] = ID_KEYS,
                 ambiguous_name_keys: Iterable[str] = AMBIGUOUS_NAME_KEYS,
                 person_parent_keys: Iterable[str] = PERSON_PARENT_KEYS,
                 pnr_keys: Iterable[str] = PNR_KEYS,
                 contact_keys: Iterable[str] = CONTACT_KEYS):
        if not key:
            raise ValueError("an empty pseudonymization key is not allowed")
        self.key = key
        self.originals_path = originals_path
        self.name_keys = {k.lower() for k in name_keys}
        self.email_keys = {k.lower() for k in email_keys}
        self.login_keys = {k.lower() for k in login_keys}
        self.free_text_keys = {k.lower() for k in free_text_keys}
        self.url_identity_keys = {k.lower() for k in url_identity_keys}
        self.id_keys = {k.lower() for k in id_keys}
        self.ambiguous_name_keys = {k.lower() for k in ambiguous_name_keys}
        self.person_parent_keys = {k.lower() for k in person_parent_keys}
        self.pnr_keys = {k.lower() for k in pnr_keys}
        self.contact_keys = {k.lower() for k in contact_keys}
        self.person_marker_keys = (self.name_keys | self.email_keys | self.pnr_keys
                                   | self.login_keys | self.url_identity_keys)
        # Free-text keys to record verbatim for the current test only: set
        # by the template's `synthetic_text` marker for sandbox prose.
        self.keep_text: set[str] = set()
        self.replacements: dict[str, str] = {}  # original (lower) -> pseudonym
        self._recorded: set[str] = set()
        self._pattern: re.Pattern | None = None  # rebuilt when replacements grow

    # -- pseudonyms ---------------------------------------------------------

    def _tag(self, kind: str, canonical: str) -> str:
        mac = hmac.new(self.key, f"{kind}:{canonical}".encode(), hashlib.sha256)
        return mac.hexdigest()[:6]

    def _remember(self, original: str, pseudonym: str, parts: Iterable[str] = ()):
        original = original.strip()
        if not original or original.lower() == pseudonym.lower():
            return
        for form in {original, urllib.parse.quote(original),
                     urllib.parse.quote_plus(original)}:
            if self.replacements.get(form.lower()) != pseudonym:
                self.replacements[form.lower()] = pseudonym
                self._pattern = None
        self._log(original, *parts)

    def _log(self, *values: str):
        new = [v for v in values if v and len(v) >= 3 and v not in self._recorded]
        if not new:
            return
        self._recorded.update(new)
        if self.originals_path is None:
            return
        fd = os.open(self.originals_path,
                     os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0),
                     0o600)
        info = os.fstat(fd)
        if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
            os.close(fd)
            raise PermissionError(f"{self.originals_path} must be ours and mode 0600: "
                                  "it holds the real values")
        with os.fdopen(fd, "a", encoding="utf-8") as f:
            for v in new:
                f.write(v.replace("\n", " ") + "\n")

    @staticmethod
    def name_tokens(value: str) -> list[str]:
        return [t for t in re.split(r"[\s,]+", value.strip()) if t]

    def name(self, value: str) -> str:
        tokens = self.name_tokens(value)
        canonical = " ".join(sorted(t.lower() for t in tokens))
        pseudonym = f"Person-{self._tag('name', canonical)}"
        self._remember(value, pseudonym, tokens)
        # Also map the reordered forms so they are replaced in free strings.
        if len(tokens) >= 2:
            self._remember(" ".join(tokens[::-1]), pseudonym)
            self._remember(f"{tokens[-1]}, {' '.join(tokens[:-1])}", pseudonym)
        return pseudonym

    def email(self, value: str) -> str:
        if is_placeholder_email(value):
            return value
        pseudonym = f"person-{self._tag('email', value.lower())}@example.invalid"
        local = value.split("@", 1)[0]
        self._remember(value, pseudonym, [local])
        return pseudonym

    def _uuid(self, kind: str, value: str) -> str:
        h = hmac.new(self.key, f"{kind}:{value.lower()}".encode(), hashlib.sha256).hexdigest()
        return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"

    def login(self, value: str) -> str:
        if UUID_RE.fullmatch(value):  # keep the shape: code may parse it
            pseudonym = self._uuid("login", value)
        else:
            pseudonym = f"user-{self._tag('login', value.lower())}"
        self._remember(value, pseudonym)
        return pseudonym

    def identifier(self, value: int | str) -> int | str:
        digits = str(value)
        tag = int(hmac.new(self.key, f"id:{digits}".encode(), hashlib.sha256).hexdigest(), 16)
        if isinstance(value, int):
            width = len(digits)
            low = 10 ** (width - 1) if width > 1 else 0
            pseudonym: int | str = low + tag % (10 ** width - low)
        elif UUID_RE.fullmatch(digits):
            pseudonym = self._uuid("id", digits)
        else:
            pseudonym = f"id-{tag % 16 ** 8:08x}"
        if len(digits) >= 4:  # short numbers are too common to replace in text
            self._remember(digits, str(pseudonym))
        else:
            self._log(digits)
        return pseudonym

    def personnummer(self, value: str) -> str:
        digits = re.sub(r"\D", "", value)[-10:]
        tag = int(self._tag("pnr", digits), 16)
        self._log(value, digits)
        # A fixed, obviously fake date with a pseudonymous serial; fails Luhn
        # on purpose half the time, which is fine: it only needs to be fake.
        return f"000000-{tag % 10000:04d}"

    # -- scrubbing ----------------------------------------------------------

    def scrub_text(self, text: str) -> str:
        """Replace known originals, emails and personnummer in a free string."""
        if self.replacements:
            if self._pattern is None:
                # One alternation, longest first, so that scrubbing stays
                # linear in the text however many people were seen.
                alternatives = sorted(self.replacements, key=len, reverse=True)
                self._pattern = re.compile(
                    r"(?<!\w)(?:" + "|".join(map(re.escape, alternatives)) + r")(?!\w)",
                    re.I)
            text = self._pattern.sub(self._replacement_for, text)
        text = EMAIL_RE.sub(lambda m: self.email(m.group(0)), text)
        for start, end in reversed(personnummer_spans(text)):
            text = text[:start] + self.personnummer(text[start:end]) + text[end:]
        return text

    def _replacement_for(self, match: re.Match) -> str:
        found = match.group(0)
        pseudonym = self.replacements.get(found.lower())
        if pseudonym is None:  # case folding that .lower() does not mirror
            pseudonym = next((v for k, v in self.replacements.items()
                              if k.casefold() == found.casefold()), "[redacted]")
        return pseudonym

    def _is_person(self, obj: dict, parent: str | None) -> bool:
        if str(obj.get("type", "")).lower() in NON_PERSON_TYPES:
            return False
        if parent in self.person_parent_keys:
            return True
        return any(str(k).lower() in self.person_marker_keys for k in obj)

    @staticmethod
    def _embedded_json(value: str) -> Any:
        """The JSON object or array a string holds, or None."""
        if value[:1] not in ("{", "["):
            return None
        try:
            data = json.loads(value)
        except ValueError:
            return None
        return data if isinstance(data, (dict, list)) else None

    def _collect(self, obj: Any, parent: str | None = None) -> Any:
        """First pass: replace identity fields, learning the originals."""
        if isinstance(obj, dict):
            person = self._is_person(obj, parent)
            out = {}
            for k, v in obj.items():
                lk = str(k).lower()
                number = isinstance(v, int) and not isinstance(v, bool)
                if lk in self.id_keys and (number or (isinstance(v, str) and v)):
                    v = self.identifier(v)
                elif isinstance(v, str) and v:
                    if lk in self.name_keys or (person and lk in self.ambiguous_name_keys):
                        v = self.name(v)
                    elif lk in self.email_keys:
                        v = self.email(v)
                    elif lk in self.pnr_keys:
                        v = self.personnummer(v)
                    elif lk in self.contact_keys:
                        if lk not in UNLOGGED_CONTACT_KEYS:
                            self._log(v)
                        v = CONTACT_PLACEHOLDER
                    elif lk in self.login_keys and person:
                        v = self.login(v)
                    elif lk in self.free_text_keys and lk not in self.keep_text:
                        self._log(v)
                        v = FREE_TEXT_PLACEHOLDER
                    elif lk in self.url_identity_keys:
                        v = URL_PLACEHOLDER
                    elif (inner := self._embedded_json(v)) is not None:
                        v = json.dumps(self._collect(inner, lk), ensure_ascii=False)
                elif number and lk in self.login_keys and person:
                    v = self.login(str(v))
                out[k] = self._collect(v, lk)
            return out
        if isinstance(obj, list):
            return [self._collect(v, parent) for v in obj]
        return obj

    def _apply(self, obj: Any) -> Any:
        """Second pass: scrub every remaining string with what was learned."""
        if isinstance(obj, dict):
            return {k: self._apply(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._apply(v) for v in obj]
        if isinstance(obj, str):
            inner = self._embedded_json(obj)
            if inner is not None:
                return json.dumps(self._apply(inner), ensure_ascii=False)
            return self.scrub_text(obj)
        return obj

    def scrub_json(self, obj: Any) -> Any:
        return self._apply(self._collect(obj))

    def scrub_body(self, body: bytes | str | None) -> bytes | str | None:
        if body is None or body == b"" or body == "":
            return body
        was_bytes = isinstance(body, bytes)
        try:
            text = body.decode("utf-8") if was_bytes else body
        except UnicodeDecodeError:
            return body  # binary; the leak scan still covers the cassette
        try:
            data = json.loads(text)
        except ValueError:
            scrubbed = self.scrub_text(scrub_form_secrets(text))
        else:
            scrubbed = json.dumps(self.scrub_json(data), ensure_ascii=False)
        return scrubbed.encode("utf-8") if was_bytes else scrubbed

    # -- vcrpy hooks --------------------------------------------------------

    def scrub_uri(self, uri: str) -> str:
        """Scrub a URI, looking inside percent-encoded path and query too."""
        parts = urllib.parse.urlsplit(self.scrub_text(uri))
        path = urllib.parse.unquote(parts.path)
        new_path = self.scrub_text(path)
        query = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
        new_query = [(k, self.scrub_text(v)) for k, v in query]
        if new_path != path:
            parts = parts._replace(path=urllib.parse.quote(new_path, safe="/:@!$&'()*+,;=~"))
        if new_query != query:
            parts = parts._replace(query=urllib.parse.urlencode(new_query))
        return urllib.parse.urlunsplit(parts)

    def before_record_request(self, request):
        request.uri = self.scrub_uri(request.uri)
        if request.body:
            request.body = self.scrub_body(request.body)
        return request

    def before_record_response(self, response):
        headers = response.get("headers", {})
        for name in list(headers):
            if name.lower() in SECRET_RESPONSE_HEADERS:
                del headers[name]
            elif name.lower() in COOKIE_RESPONSE_HEADERS:
                headers[name] = [redact_cookie(v) for v in headers[name]]
            else:
                headers[name] = [self.scrub_text(v) if isinstance(v, str) else v
                                 for v in headers[name]]
        body = response.get("body", {})
        if "string" in body:
            body["string"] = self.scrub_body(body["string"])
            new_len = len(body["string"] if isinstance(body["string"], bytes)
                          else body["string"].encode("utf-8"))
            for name in headers:
                if name.lower() == "content-length":
                    headers[name] = [str(new_len)]
        return response

    def vcr_config(self) -> dict:
        return {
            "filter_headers": SECRET_HEADERS,
            "filter_query_parameters": SECRET_QUERY_PARAMS,
            "filter_post_data_parameters": SECRET_QUERY_PARAMS,
            "decode_compressed_response": True,  # else gzip bodies escape scrubbing
            "before_record_request": self.before_record_request,
            "before_record_response": self.before_record_response,
            # The body too: else a write test passes in replay while it sends
            # the wrong data.  vcrpy scrubs the live request the same way
            # before matching, so pseudonymized bodies still match.
            "match_on": ("method", "scheme", "host", "port", "path", "query", "body"),
        }


def scrub_form_secrets(text: str) -> str:
    """Redact secret fields in HTML forms and form-encoded bodies (SAML)."""
    def repl(m: re.Match) -> str:
        prefix = m.group(1) if m.group(1) is not None else m.group(3)
        return prefix + SECRET_PLACEHOLDER
    return SECRET_FORM_RE.sub(repl, text)


def redact_cookie(header: str) -> str:
    """name=value; attrs -> name=redacted; attrs (the name is kept)."""
    pair, sep, attributes = header.partition(";")
    name = pair.split("=", 1)[0].strip()
    return f"{name}={SECRET_PLACEHOLDER}{sep}{attributes}"


# -- leak scanning ------------------------------------------------------------

def redact(value: str, kind: str = "") -> str:
    """Describe a hit without repeating it.

    An email keeps its domain, which tells a placeholder or a staff
    address apart without showing whose it is.
    """
    if kind == "email" and "@" in value:
        local, domain = value.rsplit("@", 1)
        return f"{local[:2]}…({len(local)} chars)@{domain}"
    return f"{value[:2]}…({len(value)} chars)"


def read_list(path: str | os.PathLike | None) -> list[str]:
    if not path or not Path(path).exists():
        return []
    return [line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")]


URL_HOST_RE = re.compile(r"//(?:[^@/\s]*@)?([^/\s:?#'\"]+)")


WORD_RE = re.compile(r"\w+")


class Needles:
    """Whole-word, case-insensitive search for many strings at once.

    Thousands of originals make one regex alternation slow on every line,
    so each needle is indexed by its first word: only where a line has
    that word is the rest of the needle compared.  Build it once per scan.
    """

    def __init__(self, needles: Iterable[str]):
        self.by_first: dict[str, list[str]] = {}
        odd = []  # needles that do not start with a word character
        for n in sorted({n.lower() for n in needles if len(n) >= 3}, key=len, reverse=True):
            m = WORD_RE.match(n)
            if m:
                self.by_first.setdefault(m.group(0), []).append(n)
            else:
                odd.append(n)
        self.odd = (re.compile(r"(?<!\w)(?:" + "|".join(map(re.escape, odd)) + r")(?!\w)")
                    if odd else None)

    def __bool__(self):
        return bool(self.by_first or self.odd)

    def finditer(self, line: str) -> Iterator[tuple[int, int, str]]:
        """(start, end, matched text) of each needle in `line`."""
        lower = line.lower()
        if len(lower) != len(line):  # a case mapping changed the length
            lower, line = line, line
        for m in WORD_RE.finditer(lower):
            for needle in self.by_first.get(m.group(0), ()):  # longest first
                end = m.start() + len(needle)
                if lower.startswith(needle, m.start()) and not (
                        end < len(lower) and (lower[end].isalnum() or lower[end] == "_")):
                    yield m.start(), end, line[m.start():end]
                    break
        if self.odd:
            for m in self.odd.finditer(lower):
                yield m.start(), m.end(), line[m.start():m.end()]


def _needles(values) -> Needles:
    return values if isinstance(values, Needles) else Needles(values)


def allowed(value: str, allow: Iterable[str]) -> bool:
    """True if `value` is on the allowlist: exact (any case) or `re:` regex."""
    for entry in allow:
        if entry.startswith("re:"):
            if re.fullmatch(entry[3:], value):
                return True
        elif entry.lower() == value.lower():
            return True
    return False


def scan_text(text: str, originals: Iterable[str] | Needles = (),
              denylist: Iterable[str] | Needles = (),
              allow: Iterable[str] = ()) -> Iterator[tuple[int, str, str]]:
    """Yield (line number, kind, redacted hit) for every leak in `text`.

    Each line is also checked percent-decoded, so that an email in a query
    string (written name%40host) is found too.  Hits on the allowlist
    and well-known fictive personnummer (Tolvan) are not reported.
    """
    allow = list(allow)
    patterns = [(p, kind) for p, kind in ((_needles(originals), "original"),
                                          (_needles(denylist), "denylist")) if p]
    for no, raw in enumerate(text.splitlines(), 1):
        decoded = urllib.parse.unquote_plus(raw)
        seen = set()
        for line in (raw, decoded) if decoded != raw else (raw,):
            hosts = [m.span(1) for m in URL_HOST_RE.finditer(line)]
            hits = []
            for m in EMAIL_RE.finditer(line):
                if not is_placeholder_email(m.group(0)):
                    hits.append(("email", m.group(0)))
            hits += [("personnummer", line[a:b]) for a, b in personnummer_spans(line)
                     if re.sub(r"\D", "", line[a:b])[-10:] not in KNOWN_FICTIVE_PNR]
            hits += [("saml-response", m.group(1)) for m in SAML_RE.finditer(line)]
            hits += [("jwt", m.group(0)) for m in JWT_RE.finditer(line)]
            hits += [("bearer-token", m.group(0)) for m in BEARER_RE.finditer(line)]
            hits += [("assigned-secret", m.group(1)) for m in ASSIGNED_SECRET_RE.finditer(line)]
            for pattern, kind in patterns:  # a name part in a host is not a leak
                hits += [(kind, text) for start, end, text in pattern.finditer(line)
                         if not any(a <= start and end <= b for a, b in hosts)]
            for kind, value in hits:
                if allowed(value, allow):
                    continue
                if (kind, value.lower()) not in seen:
                    seen.add((kind, value.lower()))
                    yield no, kind, redact(value, kind)


def cassette_strings(path: Path) -> Iterator[str]:
    """URIs, header values and bodies of a cassette, as unfolded strings.

    vcrpy's YAML dumper folds long strings across lines, so a name can be
    split by a line break in the file; the parsed values have no folds.
    """
    try:
        interactions = load_cassette(path)
    except Exception:
        return
    for it in interactions:
        for part in (it.get("request") or {}, it.get("response") or {}):
            if part.get("uri"):
                yield str(part["uri"])
            for values in (part.get("headers") or {}).values():
                yield from (str(v) for v in (values if isinstance(values, list) else [values]))
            text = _body_text(part.get("body"))
            if text:
                yield text


def scan_file(path: Path, originals: Iterable[str] | Needles = (),
              denylist: Iterable[str] | Needles = (),
              allow: Iterable[str] = ()) -> Iterator[tuple[str, str, str]]:
    """Yield (location, kind, redacted hit) for a file; cassettes also unfolded."""
    originals, denylist, allow = _needles(originals), _needles(denylist), list(allow)
    text = path.read_text(encoding="utf-8", errors="replace")
    found = set()
    for no, kind, hit in scan_text(text, originals, denylist, allow):
        found.add((kind, hit))
        yield str(no), kind, hit
    if path.suffix in (".yaml", ".yml", ".json"):
        for value in cassette_strings(path):
            for _, kind, hit in scan_text(" ".join(value.split()), originals, denylist, allow):
                if (kind, hit) not in found:
                    found.add((kind, hit))
                    yield "unfolded", kind, hit


NAME_PAIR_RE = re.compile(r"\b[A-ZÅÄÖÉ][a-zåäöéü]+ [A-ZÅÄÖÉ][a-zåäöéü]+\b")


def name_like(text: str, allow: Iterable[str] = ()) -> Iterator[tuple[int, str]]:
    allowed = {a.lower() for a in allow}
    for no, line in enumerate(text.splitlines(), 1):
        for m in NAME_PAIR_RE.finditer(line):
            if m.group(0).lower() not in allowed:
                yield no, redact(m.group(0))


# "key": "value" in JSON or 'key': 'value' in a Python repr (PythonTeX output)
KEY_VALUE_RE = re.compile(
    r"""(["'])([A-Za-z_][\w-]*)\1\s*:\s*(["'])((?:\\.|(?!\3)[^\\])*)\3""")


def key_census(texts: Iterable[str]) -> list[tuple[str, int, int]]:
    """(key, distinct string values, longest value) over all texts.

    Finds free text and names that no pattern recognizes: a scrubbed key
    has one distinct value (its placeholder), a leaking one has many long
    ones.  Sorted with the longest values first; the values themselves
    are never returned."""
    values: dict[str, set[str]] = {}
    for text in texts:
        for m in KEY_VALUE_RE.finditer(text):
            values.setdefault(m.group(2), set()).add(m.group(4))
    rows = [(k, len(v), max(map(len, v))) for k, v in values.items()]
    return sorted(rows, key=lambda r: (-r[2], -r[1], r[0]))


def iter_files(paths: Iterable[str | os.PathLike]) -> Iterator[Path]:
    for p in map(Path, paths):
        if p.is_dir():
            yield from sorted(f for f in p.rglob("*") if f.is_file())
        elif p.is_file():
            yield p


# -- cassette shapes ----------------------------------------------------------

def _yaml_load(text: str) -> Any:
    try:  # vcrpy's own loader: safe, but accepts the tags vcrpy writes
        from vcr.serializers.yamlserializer import deserialize
    except ImportError:
        import yaml

        class Loader(getattr(yaml, "CSafeLoader", yaml.SafeLoader)):
            """Safe loading plus the benign !!python/tuple and !!python/str."""

        Loader.add_constructor("tag:yaml.org,2002:python/tuple",
                               lambda loader, node: tuple(loader.construct_sequence(node)))
        Loader.add_constructor("tag:yaml.org,2002:python/str",
                               lambda loader, node: loader.construct_scalar(node))
        return yaml.load(text, Loader=Loader)
    return deserialize(text)


def load_cassette(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    data = json.loads(text) if path.suffix == ".json" else _yaml_load(text)
    return (data or {}).get("interactions", [])


def _body_text(body: Any) -> str | None:
    raw = body.get("string") if isinstance(body, dict) else body
    if raw is None:
        return None
    if hasattr(raw, "getvalue"):  # a BytesIO request body
        raw = raw.getvalue()
    if isinstance(raw, bytes):
        if raw[:2] == b"\x1f\x8b":
            raw = gzip.decompress(raw)
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return None
    return str(raw)


def json_shape(obj: Any, path: str = "$") -> set[tuple[str, str]]:
    """Set of (key path, type name); list items merge under `[]`."""
    if isinstance(obj, dict):
        out = {(path, "object")}
        for k, v in obj.items():
            out |= json_shape(v, f"{path}.{k}")
        return out
    if isinstance(obj, list):
        out = {(path, "array")}
        for v in obj:
            out |= json_shape(v, f"{path}[]")
        return out
    kind = {bool: "bool", int: "number", float: "number", str: "string",
            type(None): "null"}.get(type(obj), type(obj).__name__)
    return {(path, kind)}


def request_key(request: dict) -> str:
    """Method plus path with volatile segments abstracted away."""
    uri = urllib.parse.urlsplit(request.get("uri", ""))
    segments = []
    for seg in uri.path.split("/"):
        if re.fullmatch(r"\d+", seg):
            seg = "{n}"
        elif re.fullmatch(r"(?:Person|user|person)-[0-9a-f]{6}", seg):
            seg = "{p}"
        elif re.fullmatch(r"[0-9a-f]{8}-[0-9a-f-]{27}", seg, re.I):
            seg = "{uuid}"
        segments.append(seg)
    return f"{request.get('method', '?')} {uri.netloc}{'/'.join(segments)}"


def path_counts(obj: Any, path: str = "$", out: dict | None = None) -> dict[str, int]:
    """How many times each key path occurs; `$[]` counts the list items."""
    out = {} if out is None else out
    out[path] = out.get(path, 0) + 1
    if isinstance(obj, dict):
        for k, v in obj.items():
            path_counts(v, f"{path}.{k}", out)
    elif isinstance(obj, list):
        for v in obj:
            path_counts(v, f"{path}[]", out)
    return out


def array_sizes(obj: Any, path: str = "$", out: dict | None = None) -> dict[str, int]:
    """Largest number of items seen at each array path."""
    out = {} if out is None else out
    if isinstance(obj, dict):
        for k, v in obj.items():
            array_sizes(v, f"{path}.{k}", out)
    elif isinstance(obj, list):
        out[path] = max(out.get(path, 0), len(obj))
        for v in obj:
            array_sizes(v, f"{path}[]", out)
    return out


def cassette_shape(interactions: list[dict]) -> dict[str, dict]:
    """Map request key -> {"status", "type", "body": {(path, type)}, "sizes"}."""
    shapes: dict[str, dict] = {}
    for it in interactions:
        key = request_key(it.get("request", {}))
        resp = it.get("response", {})
        entry = shapes.setdefault(key, {"status": set(), "type": set(), "body": set(),
                                        "sizes": {}, "counts": {}})
        entry["status"].add(resp.get("status", {}).get("code"))
        headers = {k.lower(): v for k, v in (resp.get("headers") or {}).items()}
        ctype = (headers.get("content-type") or [""])[0].split(";")[0].strip()
        entry["type"].add(ctype)
        text = _body_text(resp.get("body", {}))
        if text and "json" in ctype:
            try:
                data = json.loads(text)
                entry["body"] |= json_shape(data)
                for path, size in array_sizes(data).items():
                    entry["sizes"][path] = max(entry["sizes"].get(path, 0), size)
                for path, count in path_counts(data).items():
                    entry["counts"][path] = entry["counts"].get(path, 0) + count
            except ValueError:
                entry["body"].add(("$", "invalid-json"))
    return shapes


def _types_by_path(body: set[tuple[str, str]]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for path, kind in body:
        out.setdefault(path, set()).add(kind)
    return out


def _optional(path: str, counts: dict) -> bool:
    """True if the key at `path` was missing from some recorded objects."""
    parent = path.rsplit(".", 1)[0] if "." in path.split("[]")[-1] else None
    return parent is not None and counts.get(path, 0) < counts.get(parent, 0)


def _smaller_live_array(path: str, old_sizes: dict, new_sizes: dict) -> str | None:
    """The array enclosing `path` if the live run saw fewer of its items."""
    for array in sorted(old_sizes, key=len, reverse=True):
        if path.startswith(array + "[]"):
            return array if new_sizes.get(array, 0) < old_sizes[array] else None
    return None


def shape_diff(old: dict, new: dict) -> list[tuple[str, str, str]]:
    """Compare two cassette shapes; returns (severity, request key, message).

    severity is "drift" for removed or changed structure and "info" for
    additions.  A key that the recording already showed to be optional
    (missing from some objects at its path) is info when the live run
    never saw it.  A path that is only ever null on one side is not a change:
    optional fields are often null in one sample and set in another.  Nor is
    a path missing under an array that held fewer items in the live run:
    the live sample may simply not include an item with that optional key.
    """
    findings = []
    for key in sorted(set(old) | set(new)):
        if key not in new:
            findings.append(("drift", key, "request no longer made"))
            continue
        if key not in old:
            findings.append(("info", key, "new request"))
            continue
        o, n = old[key], new[key]
        if o["status"] != n["status"]:
            findings.append(("drift", key, f"status {sorted(o['status'], key=str)} -> "
                                           f"{sorted(n['status'], key=str)}"))
        if o["type"] != n["type"]:
            findings.append(("drift", key, f"content type {sorted(o['type'])} -> {sorted(n['type'])}"))
        ot, nt = _types_by_path(o["body"]), _types_by_path(n["body"])
        for path in sorted(set(ot) | set(nt)):
            a, b = ot.get(path, set()) - {"null"}, nt.get(path, set()) - {"null"}
            if path not in nt:
                array = _smaller_live_array(path, o.get("sizes", {}), n.get("sizes", {}))
                if _optional(path, o.get("counts", {})):
                    findings.append(("info", key, f"not seen {path} (optional: missing "
                                                  "from some recorded items)"))
                elif array:
                    findings.append(("info", key, f"not seen {path} "
                                                  f"(fewer items in {array} live)"))
                else:
                    findings.append(("drift", key, f"removed {path}"))
            elif path not in ot:
                findings.append(("info", key, f"added {path}"))
            elif a and b and a != b:
                findings.append(("drift", key, f"type of {path}: {sorted(a)} -> {sorted(b)}"))
    return findings


def directory_shapes(root: Path) -> dict[str, dict]:
    """Shapes of every cassette under `root`, keyed by relative path."""
    out = {}
    for f in sorted(root.rglob("*")):
        if f.is_file() and f.suffix in (".yaml", ".yml", ".json"):
            out[str(f.relative_to(root))] = cassette_shape(load_cassette(f))
    return out


def compare_directories(committed: Path, live: Path) -> list[tuple[str, str, str, str]]:
    """(severity, cassette, request key, message) for every difference.

    Only cassettes that the live run re-recorded are compared; a committed
    cassette without a live counterpart was not exercised and is reported
    as info, since a partial live run (-k) is normal.
    """
    old, new = directory_shapes(committed), directory_shapes(live)
    findings = []
    for name in sorted(set(old) | set(new)):
        if name not in new:
            findings.append(("info", name, "-", "not re-recorded in the live run"))
        elif name not in old:
            findings.append(("info", name, "-", "new cassette (not committed yet)"))
        else:
            findings += [(sev, name, key, msg) for sev, key, msg in shape_diff(old[name], new[name])]
    return findings
