import subprocess

# ===============================
# LOAD BARCODE
# ===============================

barcode_hex = """019b094500007a224356ca1f01824a279616ef6003eddbaa86b248ea7cc4735847db86eedba4a63aa4801d2db535e32a039cddd40dcd73f2ed92d582afbf4cddfc34b9437e908f70ffbd6fb600cbe224592e25072640624cc4fcca994b39e67d823680ad389ec15e8ec3d7dfd14ee8cbf39f2deda93778bba5e214eeff12ba3265d2de4857a304ae3ebdcd0e5fd32576fb1f47ee4b9241ee2e84414301134b32ad1e697cc7d339523a68412d7b92832d8ceadead5bd4c0d4a501d0fe0208d267c0df42e5103381784c6c4bd5df30c8bcf4dc842da0b5dc88827bc4137926af254d0015fced7fd252d19699e0aca20ce1b077ccee0034623bd317adb26289adfffaa54b5ceee1311283b7a3d0eb96cc78d638ff071b1abc414d31d4af14dac43a71c331e377fa44a6feb0f1e927e15401fe6b9f1c3477b7562e770c5ff7457b51897c790b1ab825d880a2a50a988eae2626d3b638dc6b54896647ed1634dba34cdfa93cbd923814645320370075d5e2505573d82cf2b1e2a9577c0bfa76fa84dc425734184b0b151694720dcc1610a5e242ef23c22e3c1754e559cae63d9b83acfc74a5ed4e0f670e93342f4e15ba1a16d9b78c2591826b240c8c1876581e67e73c9f0c4387128c646df8f283e00b859bf5ce755a0675367456820a185d6a45934ea752616481919eeee0efaed54d152b049348c687ebb49ab470077ee0867fb38241f3e6f6d7135bedacf222a499a28f0a136d4d7219466ccfe56412723a8eec82d3dce75dcd3b520654b65eb0d856b7a3fc1a291cca76c4c4d4a77e80703af6e4aa02f204c382ee47e6af942227825b1f632ab428875391b9a09fa8261c1f7c03cee7a39fa595042e59837e79815487fdf84989994247c04dbb2c4f46cbaffaaa4561173a3a06964442d69db93ebfca12871457410e6e964fac6ff39fc029835553473808031f49af4ce6d155893d4871eb29110c99913aff8d89118620acb6ce104c7c010c7d98d498de08b0b680fe"""

barcode_hex = barcode_hex.strip().replace("\n", "").replace(" ", "")
barcode_bytes = bytes.fromhex(barcode_hex)

print("TOTAL BYTES:", len(barcode_bytes))

# ===============================
# HEADER
# ===============================

version = barcode_bytes[0:4]
reserved = barcode_bytes[4:6]

print("\n--- HEADER ---")
print("Version:", version.hex())
print("Reserved:", reserved.hex())

# ===============================
# REMAINING 714 BYTES
# ===============================

remaining = barcode_bytes[6:]
print("\nRemaining Length:", len(remaining))

if len(remaining) != 714:
    print("Unexpected remaining length. Check barcode input.")
    exit()

# ===============================
# SPLIT INTO BLOCKS
# ===============================

blocks = []
offset = 0

# First 5 blocks (128 bytes each)
for i in range(5):
    block = remaining[offset:offset + 128]
    blocks.append(block)
    offset += 128

# Last block (74 bytes)
block6 = remaining[offset:offset + 74]
blocks.append(block6)

print("Total Blocks:", len(blocks))

for i, b in enumerate(blocks):
    print(f"Block {i+1} size:", len(b))


combined = remaining  # still encrypted — for structure testing only

print("\nCombined Length:", len(combined))

# ===============================
# VALIDATE LENGTH
# ===============================

if len(combined) < 100:
    print("Decryption likely failed — payload too small.")
    exit()

# ===============================
# SKIP FIRST 10 BYTES
# ===============================

payload = combined[10:]
print("Payload Length (after skip 10):", len(payload))

# ===============================
# CALL NODE DECODER
# ===============================

print("\n--- CALLING NODE DECODER ---")

try:
    result = subprocess.run(
        ["node", "script.js", payload.hex()],
        capture_output=True,
        text=True,          
        encoding="utf-8"    
    )

    if result.returncode != 0:
        print("Node Error:")
        print(result.stderr)
    else:
        print("Decoded JSON:")
        print(result.stdout)

except FileNotFoundError:
    print("Node.js not found. Install Node and ensure it's in PATH.")
