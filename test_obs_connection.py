"""
Test script to verify OBS WebSocket connection
Run this to troubleshoot OBS connectivity issues
"""

import os
import sys
from dotenv import load_dotenv
from obswebsocket import obsws, requests as obs_requests

# Load environment variables
load_dotenv()

OBS_HOST = os.getenv('OBS_HOST', 'localhost')
OBS_PORT = int(os.getenv('OBS_PORT', 4455))
OBS_PASSWORD = os.getenv('OBS_PASSWORD', '')

print("=" * 50)
print("OBS WebSocket Connection Test")
print("=" * 50)
print(f"Host: {OBS_HOST}")
print(f"Port: {OBS_PORT}")
print(f"Password: {'*' * len(OBS_PASSWORD) if OBS_PASSWORD else '(none)'}")
print()

try:
    print("Attempting to connect to OBS...")
    client = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
    client.connect()
    print("✓ Connected successfully!")
    print()

    # Get OBS version
    print("Getting OBS version...")
    version = client.call(obs_requests.GetVersion())
    print(f"✓ OBS Version: {version.datain['obsVersion']}")
    print(f"✓ WebSocket Version: {version.datain['obsWebSocketVersion']}")
    print()

    # Get scenes
    print("Getting scenes...")
    scenes = client.call(obs_requests.GetSceneList())
    scene_names = [s['sceneName'] for s in scenes.datain['scenes']]
    print(f"✓ Found {len(scene_names)} scenes:")
    for scene in scene_names:
        print(f"  - {scene}")
    print()

    # Get sources from first scene (if available)
    if scene_names:
        first_scene = scene_names[0]
        print(f"Getting sources from '{first_scene}'...")
        sources = client.call(obs_requests.GetSceneItemList(sceneName=first_scene))
        source_names = [s['sourceName'] for s in sources.datain['sceneItems']]
        print(f"✓ Found {len(source_names)} sources:")
        for source in source_names[:5]:  # Show first 5
            print(f"  - {source}")
        if len(source_names) > 5:
            print(f"  ... and {len(source_names) - 5} more")
        print()

        # Get filters from first source (if available)
        if source_names:
            first_source = source_names[0]
            print(f"Getting filters from '{first_source}'...")
            filters = client.call(obs_requests.GetSourceFilterList(sourceName=first_source))
            filter_list = filters.datain['filters']
            print(f"✓ Found {len(filter_list)} filters:")
            for f in filter_list:
                status = "✓" if f['filterEnabled'] else "✗"
                print(f"  {status} {f['filterName']} ({f['filterType']})")
            print()

    print("=" * 50)
    print("✓ All tests passed! OBS is ready to use.")
    print("=" * 50)

    client.disconnect()

except ConnectionRefusedError:
    print("✗ Connection refused!")
    print()
    print("Troubleshooting:")
    print("1. Is OBS Studio running?")
    print("2. Is WebSocket server enabled in OBS?")
    print("   (Tools → WebSocket Server Settings)")
    print("3. Is the port correct? (default: 4455)")
    sys.exit(1)

except Exception as e:
    print(f"✗ Error: {e}")
    print()
    print("Troubleshooting:")
    print("1. Check OBS WebSocket password in .env file")
    print("2. Verify WebSocket server is enabled in OBS")
    print("3. Check firewall settings")
    sys.exit(1)
