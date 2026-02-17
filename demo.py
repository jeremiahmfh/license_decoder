import argparse
import base64
import subprocess
import sys
from pathlib import Path

def read_source_file(path: str, source_type: int) -> bytes:
    """Read the license source file and return raw bytes."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Source file not found: {path}")

    if source_type == 2:  # Base64 text
        content = p.read_text(encoding="utf-8").strip()
        try:
            return base64.b64decode(content)
        except Exception as e:
            raise ValueError(f"Failed to decode Base64: {e}")
    elif source_type == 3:  # Raw bytes
        return p.read_bytes()
    else:
        raise ValueError(f"Unsupported source type {source_type}. Only 2 (Base64) and 3 (raw) are supported in this script.")

def decode_with_node(bytes_data: bytes) -> dict:
    """Call the Node.js script.js decoder with raw bytes."""
    hex_str = bytes_data.hex()
    try:
        result = subprocess.run(
            ["node", "script.js", hex_str],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if result.returncode != 0:
            print("Node.js error:")
            print(result.stderr)
            sys.exit(1)
        else:
            import json
            return json.loads(result.stdout)
    except FileNotFoundError:
        raise RuntimeError("Node.js not found. Install Node.js and ensure 'node' is in your PATH.")

def main():
    parser = argparse.ArgumentParser(description="Decode South African driving license (Base64 or raw).")
    parser.add_argument("source", help="Path to the source file (.txt Base64 or .raw binary)")
    parser.add_argument("-t", "--types", type=int, choices=[2,3], required=True,
                        help="Source type: 2=Base64 text file, 3=raw binary file")
    args = parser.parse_args()

    try:
        raw_bytes = read_source_file(args.source, args.types)
        decoded = decode_with_node(raw_bytes)
        print("Decoded License Data:")
        import json
        print(json.dumps(decoded, indent=4))
    except Exception as e:
        print("Error:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
