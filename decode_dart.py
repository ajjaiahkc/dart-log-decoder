import os
import json
import subprocess


def find_token_path(base_folder, product_name):
    """Find folder matching product name (case-insensitive) with at least one file."""
    product_name_lower = product_name.lower()
    for root, dirs, _ in os.walk(base_folder):
        for d in dirs:
            if d.lower() == product_name_lower:
                full_path = os.path.join(root, d)
                for _, _, files in os.walk(full_path):
                    if files:
                        return full_path
    return None


def main():
    print("Hi ESRVT team...")
    print("=== Dart Logs Decoder ===")

    config_path = "Config_decode.json"
    if not os.path.isfile(config_path):
        print(f"❌ Config file not found: {config_path}")
        return

    with open(config_path, "r") as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse config JSON: {e}")
            return

    token_base = config.get("TokenBasePath")
    dart_folder = config.get("DartFolderPath")
    glogg_path = config.get("GloggPath")

    if not token_base or not dart_folder or not glogg_path:
        print("❌ Config is missing required paths: TokenBasePath, DartFolderPath, or GloggPath")
        return

    product = input("Enter product name: ").strip()
    token_path = find_token_path(token_base, product)

    if not token_path:
        print(f"❌ Token folder for '{product}' not found or contains no files.")
        return
    print(f"✅ Found token path: {token_path}")

    dart_bin = os.path.join(dart_folder, "dart.bin")
    if not os.path.isfile(dart_bin):
        print(f"❌ dart.bin file not found: {dart_bin}")
        return

    systrace_exe = os.path.join(dart_folder, "SysTraceParser.exe")
    if not os.path.isfile(systrace_exe):
        print(f"❌ SysTraceParser executable not found: {systrace_exe}")
        return

    # Get device type
    device_type = ""
    while device_type.lower() not in ["jedi", "jolt"]:
        device_type = input("Enter device type (jedi/jolt): ").strip().lower()

    output_file = os.path.join(dart_folder, f"{product}_decode.txt")

    # Build decode command
    cmd = [
        systrace_exe,
        "-i", dart_bin,
        "-o", output_file,
        "-t", token_path
    ]

    if device_type == "jolt":
        cmd += ["-slotconfig", "Tron", "-showslot", "true", "-showslotabbr", "true"]

    print(f"\n🚀 Running command:\n{' '.join(cmd)}\n")

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Decode completed! Output saved to:\n{output_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running SysTraceParser: {e}")
        return

    # Try to open with glogg
    try:
        subprocess.Popen([glogg_path, output_file])
        print(f"📂 Opening with Glogg...")
    except Exception as e:
        print(f"❌ Could not open with Glogg: {e}")


if __name__ == "__main__":
    main()
