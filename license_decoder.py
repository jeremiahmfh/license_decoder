import json
from typing import Dict
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

# ===============================
# CONFIGURATION — official SA keys (PEM format)
# ===============================
SA_PUBLIC_KEY_128 = """-----BEGIN RSA PUBLIC KEY-----

-----END RSA PUBLIC KEY-----"""

SA_PUBLIC_KEY_74 = """-----BEGIN RSA PUBLIC KEY-----

-----END RSA PUBLIC KEY-----"""

# ===============================
# HARDCODED BARCODE HEX
# ===============================
barcode_hex = """019b094500007a224356ca1f01824a279616ef6003eddbaa86b248ea7cc4735847db86eedba4a63aa4801d2db535e32a039cddd40dcd73f2ed92d582afbf4cddfc34b9437e908f70ffbd6fb600cbe224592e25072640624cc4fcca994b39e67d823680ad389ec15e8ec3d7dfd14ee8cbf39f2deda93778bba5e214eeff12ba3265d2de4857a304ae3ebdcd0e5fd32576fb1f47ee4b9241ee2e84414301134b32ad1e697cc7d339523a68412d7b92832d8ceadead5bd4c0d4a501d0fe0208d267c0df42e5103381784c6c4bd5df30c8bcf4dc842da0b5dc88827bc4137926af254d0015fced7fd252d19699e0aca20ce1b077ccee0034623bd317adb26289adfffaa54b5ceee1311283b7a3d0eb96cc78d638ff071b1abc414d31d4af14dac43a71c331e377fa44a6feb0f1e927e15401fe6b9f1c3477b7562e770c5ff7457b51897c790b1ab825d880a2a50a988eae2626d3b638dc6b54896647ed1634dba34cdfa93cbd923814645320370075d5e2505573d82cf2b1e2a9577c0bfa76fa84dc425734184b0b151694720dcc1610a5e242ef23c22e3c1754e559cae63d9b83acfc74a5ed4e0f670e93342f4e15ba1a16d9b78c2591826b240c8c1876581e67e73c9f0c4387128c646df8f283e00b859bf5ce755a0675367456820a185d6a45934ea752616481919eeee0efaed54d152b049348c687ebb49ab470077ee0867fb38241f3e6f6d7135bedacf222a499a28f0a136d4d7219466ccfe56412723a8eec82d3dce75dcd3b520654b65eb0d856b7a3fc1a291cca76c4c4d4a77e80703af6e4aa02f204c382ee47e6af942227825b1f632ab428875391b9a09fa8261c1f7c03cee7a39fa595042e59837e79815487fdf84989994247c04dbb2c4f46cbaffaaa4561173a3a06964442d69db93ebfca12871457410e6e964fac6ff39fc029835553473808031f49af4ce6d155893d4871eb29110c99913aff8d89118620acb6ce104c7c010c7d98d498de08b0b680fe"""
barcode_bytes = bytes.fromhex(barcode_hex.strip())

# ===============================
# SPLIT RSA BLOCKS
# ===============================
def split_blocks(data: bytes):
    blocks = [data[i*128:(i+1)*128] for i in range(5)]
    blocks.append(data[640:])  # last 74 bytes
    return blocks

# ===============================
# DECRYPT BLOCKS
# ===============================
def decrypt_blocks(blocks):
    all_bytes = bytearray()

    # First 5 blocks with 128-byte key
    key128 = RSA.import_key(SA_PUBLIC_KEY_128)
    cipher128 = PKCS1_v1_5.new(key128)
    for block in blocks[:5]:
        decrypted = cipher128.decrypt(block, None)
        if decrypted is None:
            raise Exception("RSA decryption failed for 128-byte block.")
        all_bytes += decrypted

    # Last block with 74-byte key
    key74 = RSA.import_key(SA_PUBLIC_KEY_74)
    cipher74 = PKCS1_v1_5.new(key74)
    decrypted = cipher74.decrypt(blocks[5], None)
    if decrypted is None:
        raise Exception("RSA decryption failed for 74-byte block.")
    all_bytes += decrypted

    return bytes(all_bytes)

# ===============================
# PARSE STRING SECTION
# ===============================
def parse_strings(data: bytes):
    index = 0
    for i, b in enumerate(data):
        if b == 0x82:
            index = i + 2
            break

    strings = []
    while index < len(data):
        value = ""
        while index < len(data):
            b = data[index]
            index += 1
            if b in (0xe0, 0xe1):
                break
            value += chr(b)
        strings.append(value)
        if len(strings) >= 12:
            break

    return {
        "vehicle_codes": strings[0] if len(strings) > 0 else "",
        "surname": strings[1] if len(strings) > 1 else "",
        "initials": strings[2] if len(strings) > 2 else "",
        "id_country_of_issue": strings[3] if len(strings) > 3 else "",
        "license_country_of_issue": strings[4] if len(strings) > 4 else "",
        "vehicle_restrictions": strings[5] if len(strings) > 5 else "",
        "license_number": strings[6] if len(strings) > 6 else "",
        "id_number": strings[7] if len(strings) > 7 else "",
    }

# ===============================
# PARSE BINARY SECTION
# ===============================
def parse_binary(data: bytes):
    offset = 400
    return {
        "issue_date_raw": data[offset:offset+4].hex(),
        "expiry_date_raw": data[offset+4:offset+8].hex(),
        "vehicle_codes_raw": data[offset+8:offset+20].hex(),
    }

# ===============================
# MAIN PROCESSOR
# ===============================
def decode_license() -> Dict:
    blocks = split_blocks(barcode_bytes)
    decrypted_bytes = decrypt_blocks(blocks)
    string_data = parse_strings(decrypted_bytes)
    binary_data = parse_binary(decrypted_bytes)

    return {
        "string_fields": string_data,
        "binary_fields": binary_data
    }

# ===============================
# CLI ENTRY
# ===============================
if __name__ == "__main__":
    try:
        parsed = decode_license()
        print(json.dumps(parsed, indent=4))
    except Exception as e:
        print("ERROR:", str(e))
