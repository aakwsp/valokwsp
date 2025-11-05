# !/usr/bin/env python3

"""this is the dev build of valokwsp. this is just to test out how to get 
all the info from riots api, more specifically the from the...

/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine} endpoint.

it is planned to work with the other endpoints as well in the future.

:3
"""
# imports :D
import json  # json file handling
import os  # getting system files 
import sys  # for exiting code
import urllib.error  # exceptions raised by urllib
import urllib.parse  # for safely escaping path components in URLs
import urllib.request  # for making HTTP requests without third-party libs
from typing import Optional, Tuple, Any  # typing helpers for function signatures

puuid_regions = ["americas", "asia", "europe"] # regions for puuid lookup
valorant_regions = ["na", "ap", "eu", "br", "kr", "latam"] # regions for valorant api

def print_art() -> None:
    """Print ASCII art banner for the script."""
    print("\n____   _________  .____    ________   ____  __.__      __  ___________________")
    print("\\   \\ /   /  _  \\ |    |   \\_____  \\ |    |/ _/  \\    /  \\/   _____/\\______   \\ ")
    print(" \\   Y   /  /_\\  \\|    |    /   |   \\|      < \\   \\/\\/   /\\_____  \\  |     ___/")
    print("  \\     /    |    \\    |___/    |    \\    |  \\ \\        / /        \\ |    |    ")
    print("   \\___/\\____|__  /_______ \\_____  /____|__ \\ \\__/\\  / /_______  / |____|")
    print("                \\/        \\/       \\/        \\/      \\/          \\/")
    print("    .___          ___.         .__.__       .___  ____  ")
    print("  __| _/_______  _\\_ |__  __ __|__|  |    __| _/ /_   |")
    print(" / __ |/ __ \\  \\/ /| __ \\|  |  \\  |  |   / __ |   |   |")
    print("/ /_/ \\  ___/\\   / | \\_\\ \\  |  /  |  |__/ /_/ |   |   |")
    print("\\____ |\\___  >\\_/  |___  /____/|__|____/\\____ |   |___|")
    print("     \\/    \\/          \\/                    \\/\n")


def load_env(path: str = ".env") -> None:
    """load environment variables from a .env file.
    
    behavior of this loader:
    - ignores blank lines and lines starting with `#` (comments).
    - takes the first `=` as the separator (KEY=VALUE).
    - strips optional surrounding quotes from the value.
    - only sets the environment variable if it's not already present in
        `os.environ` (so explicit environment variables override .env).
    """

    # list of keys to look for
    allowed_keys = {"RIOT_API_KEY", 
                    "RIOT_API_BASE", 
                    "DISCORD_TOKEN", 
                    "DISCORD_GUILD_ID"} 

    # try to open the .env file
    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()

                # skip empty lines and comment lines
                if not line or line.startswith("#"):
                    continue

                # Must contain an equals sign to be a key=value pair
                if "=" not in line:
                    continue

                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip()
                # Remove optional surrounding single or double quotes
                # Only set the environment variable if it's not already set
                if key in allowed_keys and key not in os.environ:
                    os.environ[key] = val

    except FileNotFoundError:
        # Missing .env is not an error for this script; we just won't load
        # any values from it.
        print(f".env file not found at {path}, skipping loading environment variables.", file=sys.stderr)
        return


def split_riot_id(riot_id: str) -> Optional[tuple[str, str]]:
    """Parse an riot_id string of the form 'name#tag' into a tuple.

    Return value is (name, tag) or None if the input doesn't match the
    expected format. We split on the last '#' so that (rare) display names
    containing '#' are handled sensibly.
    """
    # check for whitespace only, missing input, or none
    if not riot_id:
        return None
    if "#" not in riot_id:
        return None
    
    # splits at # and removed whitespaces
    name, tag = riot_id.rsplit("#", 1)

    # replaces whitespaces with nothing, even in the middle of the string
    name = name.replace(" ", "")
    tag = tag.replace(" ", "")

    # if name or tag is empty after stripping, return None
    if not name or not tag:
        return None

    # returns the name and tag in a tuple
    return name, tag


def from_endpoint(region: str, name: str, tag: str, base: str, endpoint: str, api_key: str, timeout: float = 5.0) -> dict | str | None:  
    """currently just get puuid from riot id via endpoint:
    /riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}

    but planning to make it work with other endpoints too.

    parameters:
    - region: the subdomain for riot api
    - name, tag: makeup of the riot id
    - base: base url from .env
    - endpoint: specific endpoint to call
    - api_key: api key from .env
    - timeout: network timeout in seconds

        Returns:
        - on success: the data parsed from JSON (often a dict) or raw text if JSON
            parsing fails.
        - on failure: a dict with error details (e.g. {"error": True, "type": ..., "message": ...}).

    Important details:
    - We URL-quote the name and tag to make them safe for use in
      a URL path segment. This prevents issues if the display name contains
      spaces, special characters, or non-ASCII characters.
    - We use urllib.request.Request and urlopen to perform the HTTP GET.
    - The Riot API requires the API key to be supplied in the
      X-Riot-Token header.
    """

    # Quote user-supplied path components so the URL is safe
    n = urllib.parse.quote(name, safe="")
    t = urllib.parse.quote(tag, safe="")

    # Construct the full endpoint URL. This is the exact path you asked for.
    url = f"https://{region}.{base}/{endpoint}/{n}/{t}"

    # Build a Request object and include headers. User-Agent is polite; some
    # servers require or log it. X-Riot-Token is how Riot authenticates requests.
    req = urllib.request.Request(url, headers={"User-Agent": "valokwsp_a1.02", "X-Riot-Token": api_key})

    # i got no clue whats happening here
    try:
        # urlopen performs the network request. We use a context manager so
        # the response object is automatically closed when we're done.
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()  # bytes

            # Try decoding as UTF-8 first, fall back to latin-1 with replacement
            # for any unexpected byte sequences. This ensures we always get
            # a string back even for broken responses.
            try:
                text = raw.decode("utf-8")
            except Exception:
                text = raw.decode("latin-1", errors="replace")

            # Attempt to parse JSON. If parsing fails we return the raw text;
            # sometimes APIs return human-readable error pages instead of JSON.
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text

    except urllib.error.HTTPError as e:
        # HTTP errors (4xx/5xx). Read the response body and return it. Riot
        # commonly returns a JSON body like {"status": {"message": "Forbidden", "status_code": 401}}
        # — we want to return that parsed JSON directly so callers get the
        # same structure the API provided.
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""

        # Try to parse the body as JSON and return the resulting object.
        try:
            parsed = json.loads(body) if body else {"body": body}
            # Also log a short message to stderr for visibility.
            print(f"HTTP error {getattr(e, 'code', '')}: {getattr(e, 'reason', '')}", file=sys.stderr)
            return parsed
        except json.JSONDecodeError:
            # If parsing fails, return a dict containing the raw body so
            # callers always receive a dict/object rather than None or raw text.
            print(f"HTTP error {getattr(e, 'code', '')}: {getattr(e, 'reason', '')} - non-JSON body", file=sys.stderr)
            return {"body": body}
    except urllib.error.URLError as e:
        # Network-level errors (DNS failures, refused connections, etc.).
        # There's no HTTP response body to parse here, but return a dict
        # with a 'body' key so callers receive the same shape as the
        # HTTPError path (i.e., a dict/object).
        reason = getattr(e, "reason", "")
        msg = f"Network error: {reason}"
        print(msg, file=sys.stderr)
        # If reason is a bytes/JSON-like string, try parsing; otherwise
        # return a dict with 'body' to keep the return type consistent.
        try:
            parsed = json.loads(str(reason)) if reason else {"body": str(reason)}
            return parsed
        except Exception:
            return {"body": str(reason)}
    except Exception as e:
        # Fallback for any other unexpected error. Return a dict with a
        # 'body' key containing the exception message so callers get a
        # consistent dict/object response shape.
        msg = f"Unexpected error: {e}"
        print(msg, file=sys.stderr)
        return {"body": str(e)}

def get_user_input() -> Tuple[str, str, str]:
    """asks for region, riot id (name#tag), and returns them as a tuple.

    tuple format is (region, name, tag).
    """
    # region prompt loop, only accepts americas, asia, europe
    while True:
        try:
            region = input(f"what is the region {puuid_regions}: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n\nprogram was aborted.\n")
            raise SystemExit(1)
        if region in puuid_regions:
            break
        print(f"\n{region} is an invalid region. expected {puuid_regions}")

    print()  # add a blank line between prompts

    # riot id prompt loop
    while True:
        try:
            riot_id = input("what is your riot id ['name#tag']: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nprogram was aborted.\n")
            raise SystemExit(1)
        parsed = split_riot_id(riot_id)

        # if parse != None, we got valid input
        if parsed:
            name, tag = parsed
            return region, name, tag
        print(f"{riot_id} is an invalid riot id format. expected ['name#tag']")


def main() -> int:
    """Main entry point for the script. Returns an exit code (0 = success).

    Steps performed:
    1. Load `.env` file to populate environment variables (if present).
    2. Read an API key from the environment.
    3. Prompt the user for region and ign.
    4. Query the Riot API and print the result.
    """
    # print welcome ascii art
    print_art()

    # get the vars we need from .env
    load_env()

    # get api key
    api_key = os.environ.get("RIOT_API_KEY")
    base = os.environ.get("RIOT_API_BASE")
    endpoint = "riot/account/v1/accounts/by-riot-id" 

    # get ign and region
    region, name, tag = get_user_input()

    # perform api call
    print(f"Searching for {name}#{tag} on region {region}...")
    raw = from_endpoint(region, name, tag, base, endpoint, api_key)
    if raw is None:
        print("No result or an error occurred.")
        return 1

    print(raw)


if __name__ == "__main__":
    # When run as a script, call main() and exit with its return code. This
    # pattern makes it easy to import functions from this module in other
    # code without executing the CLI portion.
    raise SystemExit(main())

