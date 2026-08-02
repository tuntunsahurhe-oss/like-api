# ========================== IMPORTS ==========================
import os
import sys
import json
import time
import threading
import asyncio
import logging
import warnings
import binascii
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

import requests
import aiohttp
from flask import Flask, request, jsonify
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
from google.protobuf.message import DecodeError
from google.protobuf.json_format import MessageToJson

warnings.simplefilter('ignore', requests.packages.urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# ========================== PROTOBUF DEFINITIONS ==========================
# Embedded from original pb2 files to avoid extra imports
_sym_db = _symbol_database.Default()

# like_pb2
DESC_LIKE = _descriptor_pool.Default().AddSerializedFile(b'\n\nlike.proto\"#\n\x04like\x12\x0b\n\x03uid\x18\x01 \x01(\x03\x12\x0e\n\x06region\x18\x02 \x01(\tb\x06proto3')
_globals_like = globals()
_builder.BuildMessageAndEnumDescriptors(DESC_LIKE, _globals_like)
_builder.BuildTopDescriptorsAndMessages(DESC_LIKE, 'like_pb2', _globals_like)
like_pb2 = type('like_pb2', (), {})
like_pb2.like = _globals_like['like']

# like_count_pb2
DESC_LIKE_COUNT = _descriptor_pool.Default().AddSerializedFile(b'\n\x10like_count.proto\"?\n\tBasicInfo\x12\x0b\n\x03UID\x18\x01 \x01(\x03\x12\x16\n\x0ePlayerNickname\x18\x03 \x01(\t\x12\r\n\x05Likes\x18\x15 \x01(\x03\"\'\n\x04Info\x12\x1f\n\x0b\x41\x63\x63ountInfo\x18\x01 \x01(\x0b\x32\n.BasicInfob\x06proto3')
_globals_like_count = globals()
_builder.BuildMessageAndEnumDescriptors(DESC_LIKE_COUNT, _globals_like_count)
_builder.BuildTopDescriptorsAndMessages(DESC_LIKE_COUNT, 'like_count_pb2', _globals_like_count)
like_count_pb2 = type('like_count_pb2', (), {})
like_count_pb2.Info = _globals_like_count['Info']
like_count_pb2.BasicInfo = _globals_like_count['BasicInfo']

# uid_generator_pb2
DESC_UID_GEN = _descriptor_pool.Default().AddSerializedFile(b'\n\x13uid_generator.proto\"0\n\ruid_generator\x12\x0f\n\x07saturn_\x18\x01 \x01(\x03\x12\x0e\n\x06garena\x18\x02 \x01(\x03\x62\x06proto3')
_globals_uid_gen = globals()
_builder.BuildMessageAndEnumDescriptors(DESC_UID_GEN, _globals_uid_gen)
_builder.BuildTopDescriptorsAndMessages(DESC_UID_GEN, 'uid_generator_pb2', _globals_uid_gen)
uid_generator_pb2 = type('uid_generator_pb2', (), {})
uid_generator_pb2.uid_generator = _globals_uid_gen['uid_generator']

# MajorLoginReq
DESC_MAJOR_LOGIN_REQ = _descriptor_pool.Default().AddSerializedFile(b'\n\x13MajorLoginReq.proto\"\xfa\n\n\nMajorLogin\x12\x12\n\nevent_time\x18\x03 \x01(\t\x12\x11\n\tgame_name\x18\x04 \x01(\t\x12\x13\n\x0bplatform_id\x18\x05 \x01(\x05\x12\x16\n\x0e\x63lient_version\x18\x07 \x01(\t\x12\x17\n\x0fsystem_software\x18\x08 \x01(\t\x12\x17\n\x0fsystem_hardware\x18\t \x01(\t\x12\x18\n\x10telecom_operator\x18\n \x01(\t\x12\x14\n\x0cnetwork_type\x18\x0b \x01(\t\x12\x14\n\x0cscreen_width\x18\x0c \x01(\r\x12\x15\n\rscreen_height\x18\r \x01(\r\x12\x12\n\nscreen_dpi\x18\x0e \x01(\t\x12\x19\n\x11processor_details\x18\x0f \x01(\t\x12\x0e\n\x06memory\x18\x10 \x01(\r\x12\x14\n\x0cgpu_renderer\x18\x11 \x01(\t\x12\x13\n\x0bgpu_version\x18\x12 \x01(\t\x12\x18\n\x10unique_device_id\x18\x13 \x01(\t\x12\x11\n\tclient_ip\x18\x14 \x01(\t\x12\x10\n\x08language\x18\x15 \x01(\t\x12\x0f\n\x07open_id\x18\x16 \x01(\t\x12\x14\n\x0copen_id_type\x18\x17 \x01(\t\x12\x13\n\x0b\x64\x65vice_type\x18\x18 \x01(\t\x12\'\n\x10memory_available\x18\x19 \x01(\x0b\x32\r.GameSecurity\x12\x14\n\x0c\x61\x63\x63\x65ss_token\x18\x1d \x01(\t\x12\x17\n\x0fplatform_sdk_id\x18\x1e \x01(\x05\x12\x1a\n\x12network_operator_a\x18) \x01(\t\x12\x16\n\x0enetwork_type_a\x18* \x01(\t\x12\x1c\n\x14\x63lient_using_version\x18\x39 \x01(\t\x12\x1e\n\x16\x65xternal_storage_total\x18< \x01(\x05\x12\"\n\x1a\x65xternal_storage_available\x18= \x01(\x05\x12\x1e\n\x16internal_storage_total\x18> \x01(\x05\x12\"\n\x1ainternal_storage_available\x18? \x01(\x05\x12#\n\x1bgame_disk_storage_available\x18@ \x01(\x05\x12\x1f\n\x17game_disk_storage_total\x18\x41 \x01(\x05\x12%\n\x1d\x65xternal_sdcard_avail_storage\x18\x42 \x01(\x05\x12%\n\x1d\x65xternal_sdcard_total_storage\x18\x43 \x01(\x05\x12\x10\n\x08login_by\x18I \x01(\x05\x12\x14\n\x0clibrary_path\x18J \x01(\t\x12\x12\n\nreg_avatar\x18L \x01(\x05\x12\x15\n\rlibrary_token\x18M \x01(\t\x12\x14\n\x0c\x63hannel_type\x18N \x01(\x05\x12\x10\n\x08\x63pu_type\x18O \x01(\x05\x12\x18\n\x10\x63pu_architecture\x18Q \x01(\t\x12\x1b\n\x13\x63lient_version_code\x18S \x01(\t\x12\x14\n\x0cgraphics_api\x18V \x01(\t\x12\x1d\n\x15supported_astc_bitset\x18W \x01(\r\x12\x1a\n\x12login_open_id_type\x18X \x01(\x05\x12\x18\n\x10\x61nalytics_detail\x18Y \x01(\x0c\x12\x14\n\x0cloading_time\x18\\ \x01(\r\x12\x17\n\x0frelease_channel\x18] \x01(\t\x12\x12\n\nextra_info\x18^ \x01(\t\x12 \n\x18\x61ndroid_engine_init_flag\x18_ \x01(\r\x12\x0f\n\x07if_push\x18\x61 \x01(\x05\x12\x0e\n\x06is_vpn\x18\x62 \x01(\x05\x12\x1c\n\x14origin_platform_type\x18\x63 \x01(\t\x12\x1d\n\x15primary_platform_type\x18\x64 \x01(\t\"5\n\x0cGameSecurity\x12\x0f\n\x07version\x18\x06 \x01(\x05\x12\x14\n\x0chidden_value\x18\x08 \x01(\x04\x62\x06proto3')
_globals_major_req = globals()
_builder.BuildMessageAndEnumDescriptors(DESC_MAJOR_LOGIN_REQ, _globals_major_req)
_builder.BuildTopDescriptorsAndMessages(DESC_MAJOR_LOGIN_REQ, 'MajorLoginReq_pb2', _globals_major_req)
MajorLogin = _globals_major_req['MajorLogin']
GameSecurity = _globals_major_req['GameSecurity']

# MajorLoginRes
DESC_MAJOR_LOGIN_RES = _descriptor_pool.Default().AddSerializedFile(b'\n\x13MajorLoginRes.proto\"|\n\rMajorLoginRes\x12\x13\n\x0b\x61\x63\x63ount_uid\x18\x01 \x01(\x04\x12\x0e\n\x06region\x18\x02 \x01(\t\x12\r\n\x05token\x18\x08 \x01(\t\x12\x0b\n\x03url\x18\n \x01(\t\x12\x11\n\ttimestamp\x18\x15 \x01(\x03\x12\x0b\n\x03key\x18\x16 \x01(\x0c\x12\n\n\x02iv\x18\x17 \x01(\x0c\x62\x06proto3')
_globals_major_res = globals()
_builder.BuildMessageAndEnumDescriptors(DESC_MAJOR_LOGIN_RES, _globals_major_res)
_builder.BuildTopDescriptorsAndMessages(DESC_MAJOR_LOGIN_RES, 'MajorLoginRes_pb2', _globals_major_res)
MajorLoginRes = _globals_major_res['MajorLoginRes']

# ========================== CONFIGURATION ==========================
AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])   # "Yg&tc%DEuh6%Zc^8"
AES_IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])  # "6oyZDr22E3ychjM%"
GUEST_API_URL = "https://sheihk-jwt.up.railway.app/token"
TOKEN_REFRESH_INTERVAL_HOURS = 6

# Global token cache (in‑memory, persists across requests within the same instance)
all_tokens = []                 # list of dicts: {"uid":str, "token":str, "region":str, "type":str}
refresh_lock = threading.Lock()
refresh_in_progress = False
last_refresh_time = None

# ========================== HELPER FUNCTIONS ==========================
def encrypt_aes(data: bytes) -> bytes:
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(data, AES.block_size))

def encrypt_message(plaintext: bytes) -> str:
    try:
        return binascii.hexlify(encrypt_aes(plaintext)).decode('utf-8')
    except Exception as e:
        app.logger.error(f"Encryption failed: {e}")
        return None

def create_protobuf_message(user_id: int, region: str) -> bytes:
    try:
        msg = like_pb2.like()
        msg.uid = user_id
        msg.region = region
        return msg.SerializeToString()
    except Exception as e:
        app.logger.error(f"Protobuf creation failed: {e}")
        return None

def create_protobuf(uid: int) -> bytes:
    try:
        msg = uid_generator_pb2.uid_generator()
        msg.saturn_ = uid
        msg.garena = 1
        return msg.SerializeToString()
    except Exception as e:
        app.logger.error(f"UID protobuf creation failed: {e}")
        return None

def enc(uid: int) -> str:
    proto = create_protobuf(uid)
    return encrypt_message(proto) if proto else None

def make_request(encrypted_uid: str, server_name: str, token: str):
    try:
        if server_name == "IND":
            url = "https://client.ind.freefiremobile.com/GetPlayerPersonalShow"
        elif server_name in {"BR", "US", "SAC", "NA"}:
            url = "https://client.us.freefiremobile.com/GetPlayerPersonalShow"
        else:
            url = "https://clientbp.ggpolarbear.com/GetPlayerPersonalShow"
        edata = bytes.fromhex(encrypted_uid)
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Authorization': f"Bearer {token}",
            'Content-Type': "application/x-www-form-urlencoded",
            'Expect': "100-continue",
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': "OB54"
        }
        resp = requests.post(url, data=edata, headers=headers, verify=False)
        hex_data = resp.content.hex()
        binary = bytes.fromhex(hex_data)
        info = like_count_pb2.Info()
        info.ParseFromString(binary)
        return info
    except Exception as e:
        app.logger.error(f"make_request exception: {e}")
        return None

async def send_request(encrypted_uid: str, token: str, url: str):
    try:
        edata = bytes.fromhex(encrypted_uid)
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Authorization': f"Bearer {token}",
            'Content-Type': "application/x-www-form-urlencoded",
            'Expect': "100-continue",
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': "OB54"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=edata, headers=headers) as response:
                return await response.text() if response.status == 200 else None
    except Exception as e:
        app.logger.error(f"send_request exception: {e}")
        return None

async def send_multiple_requests(uid: int, server_name: str, url: str, token_list: list):
    protobuf_msg = create_protobuf_message(uid, server_name)
    if not protobuf_msg:
        return
    encrypted_uid = encrypt_message(protobuf_msg)
    if not encrypted_uid:
        return
    tasks = []
    for i in range(100):
        token = token_list[i % len(token_list)]["token"]
        tasks.append(send_request(encrypted_uid, token, url))
    await asyncio.gather(*tasks, return_exceptions=True)

def get_player_info(encrypted_uid: str, server_name: str, token_list: list):
    """Return (info, index_of_token_used) or (None, -1)"""
    for idx, t in enumerate(token_list):
        info = make_request(encrypted_uid, server_name, t["token"])
        if info is not None:
            return info, idx
    return None, -1

# ========================== TOKEN CONVERSIONS ==========================
def decode_jwt(token: str) -> dict:
    import base64
    parts = token.split('.')
    if len(parts) != 3:
        return {}
    try:
        header = json.loads(base64.urlsafe_b64decode(parts[0] + '==').decode())
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + '==').decode())
        return {"header": header, "payload": payload}
    except Exception:
        return {}

def build_major_login(open_id: str, access_token: str, platform_type: int) -> bytes:
    major = MajorLogin()
    major.event_time = "2025-03-23 12:00:00"
    major.game_name = "free fire"
    major.platform_id = 1
    major.client_version = "1.128.2"
    major.system_software = "Android OS 9 / API-28 (PQ3B.190801.10101846/G9650ZHU2ARC6)"
    major.system_hardware = "Handheld"
    major.telecom_operator = "Verizon"
    major.network_type = "WIFI"
    major.screen_width = 1920
    major.screen_height = 1080
    major.screen_dpi = "280"
    major.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
    major.memory = 3003
    major.gpu_renderer = "Adreno (TM) 640"
    major.gpu_version = "OpenGL ES 3.1 v1.46"
    major.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    major.client_ip = "223.191.51.89"
    major.language = "en"
    major.open_id = open_id
    major.open_id_type = "4"
    major.device_type = "Handheld"
    major.memory_available.version = 55
    major.memory_available.hidden_value = 81
    major.access_token = access_token
    major.platform_sdk_id = 1
    major.network_operator_a = "Verizon"
    major.network_type_a = "WIFI"
    major.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    major.external_storage_total = 36235
    major.external_storage_available = 31335
    major.internal_storage_total = 2519
    major.internal_storage_available = 703
    major.game_disk_storage_available = 25010
    major.game_disk_storage_total = 26628
    major.external_sdcard_avail_storage = 32992
    major.external_sdcard_total_storage = 36235
    major.login_by = 3
    major.library_path = "/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64"
    major.reg_avatar = 1
    major.library_token = "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk"
    major.channel_type = 3
    major.cpu_type = 2
    major.cpu_architecture = "64"
    major.client_version_code = "2019118695"
    major.graphics_api = "OpenGLES2"
    major.supported_astc_bitset = 16383
    major.login_open_id_type = 4
    major.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWA0FUgsvA1snWlBaO1kFYg=="
    major.loading_time = 13564
    major.release_channel = "android"
    major.extra_info = "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY="
    major.android_engine_init_flag = 110009
    major.if_push = 1
    major.is_vpn = 1
    major.origin_platform_type = str(platform_type)
    major.primary_platform_type = str(platform_type)
    return major.SerializeToString()

def try_major_login(open_id: str, access_token: str, platform_type: int):
    payload = build_major_login(open_id, access_token, platform_type)
    encrypted_payload = encrypt_aes(payload)
    url = "https://loginbp.ggpolarbear.com/MajorLogin"
    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; ASUS_Z01QD Build/PI)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB54"
    }
    try:
        resp = requests.post(url, data=encrypted_payload, headers=headers, verify=False, timeout=10)
        if resp.status_code != 200:
            return None
        major_res = MajorLoginRes()
        major_res.ParseFromString(resp.content)
        if major_res.token:
            return {
                "account_uid": str(major_res.account_uid),
                "region": major_res.region,
                "token": major_res.token,
                "url": major_res.url,
                "timestamp": major_res.timestamp
            }
    except Exception as e:
        app.logger.error(f"MajorLogin error for platform {platform_type}: {e}")
    return None

def access_token_to_jwt(access_token: str) -> dict:
    # Inspect token to get open_id
    inspect_url = f"https://100067.connect.garena.com/oauth/token/inspect?token={access_token}"
    try:
        insp_resp = requests.get(inspect_url, timeout=10)
        if insp_resp.status_code != 200:
            return None
        insp_data = insp_resp.json()
        open_id = insp_data.get('open_id')
        if not open_id:
            return None
    except Exception as e:
        app.logger.error(f"Inspect request failed: {e}")
        return None

    # Try all platform types
    for pt in [2, 3, 4, 6, 8]:
        result = try_major_login(open_id, access_token, pt)
        if result:
            return {
                "uid": result["account_uid"],
                "token": result["token"],
                "region": result["region"],
                "type": "access"
            }
    return None

def eat_token_to_jwt(eat_token: str) -> dict:
    # Convert eat token to access token
    target_url = "https://api-otrss.garena.com/support/callback/"
    try:
        session = requests.Session()
        response = session.get(target_url, params={'access_token': eat_token}, allow_redirects=False, timeout=30)
        while response.status_code in (301, 302, 303, 307, 308):
            location = response.headers.get('Location')
            if not location:
                break
            if not location.startswith(('http://', 'https://')):
                base = urlparse(target_url)
                location = base._replace(path=location).geturl()
            response = session.get(location, allow_redirects=False, timeout=30)
        parsed = urlparse(response.url)
        query_params = parse_qs(parsed.query)
        access_token = query_params.get('access_token', [None])[0]
        if access_token:
            return access_token_to_jwt(access_token)
    except Exception as e:
        app.logger.error(f"eat_token_to_jwt failed: {e}")
    return None

def guest_to_jwt(uid: str, pass: str) -> dict:
    try:
        params = {"uid": uid, "pass": password}
        resp = requests.get(GUEST_API_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("status") == "success":
            # 🎯 এপিআই থেকে সরাসরি মেইন অ্যাকাউন্ট আইডি এবং রেডিমেড টোকেন নিন
            account_uid = data.get("account_id") or data.get("uid")
            jwt_token = data.get("token")  # 👈 ওল্ড কোডে এখানে jwt_token ছিল, এখন ডিরেক্ট "token" ফিল্ডটি নিলাম
            region = data.get("region", "BD")
            
            if account_uid and jwt_token:
                app.logger.info(f"Successfully loaded token for UID: {account_uid}")
                return {
                    "uid": str(account_uid),
                    "token": jwt_token,     # এই টোকেনটাই সরাসরি লাইক মারতে চলে যাবে
                    "region": region,
                    "type": "guest"
                }
    except Exception as e:
        app.logger.error(f"Guest token fetch failed for {uid}: {e}")
    return None


# ========================== TOKEN REFRESH ==========================
def refresh_all_tokens():
    global all_tokens, refresh_in_progress, last_refresh_time
    with refresh_lock:
        if refresh_in_progress:
            return
        refresh_in_progress = True

    app.logger.info("Starting full token refresh...")
    new_tokens = []

    # Guest accounts (accounts.txt)
    if os.path.exists("accounts.txt"):
        with open("accounts.txt", "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if ':' not in line:
                    continue
                uid, pwd = line.split(':', 1)
                jwt = guest_to_jwt(uid.strip(), pwd.strip())
                if jwt:
                    new_tokens.append(jwt)
                time.sleep(0.5)
    else:
        app.logger.warning("accounts.txt not found")

    # Eat tokens (eat.txt)
    if os.path.exists("eat.txt"):
        with open("eat.txt", "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                jwt = eat_token_to_jwt(line)
                if jwt:
                    new_tokens.append(jwt)
                time.sleep(0.5)
    else:
        app.logger.warning("eat.txt not found")

    # Access tokens (access.txt)
    if os.path.exists("access.txt"):
        with open("access.txt", "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                jwt = access_token_to_jwt(line)
                if jwt:
                    new_tokens.append(jwt)
                time.sleep(0.5)
    else:
        app.logger.warning("access.txt not found")

    # Replace global list
    all_tokens = new_tokens
    last_refresh_time = datetime.now()

    with refresh_lock:
        refresh_in_progress = False
    app.logger.info(f"Token refresh completed. Total tokens: {len(all_tokens)}")

def scheduled_refresh():
    """Background thread – will be ignored on Vercel."""
    while True:
        time.sleep(TOKEN_REFRESH_INTERVAL_HOURS * 3600)
        refresh_all_tokens()

def start_background_scheduler():
    """Start a background thread only if not running on Vercel."""
    if os.environ.get("VERCEL") != "1":
        t = threading.Thread(target=scheduled_refresh, daemon=True)
        t.start()
        app.logger.info("Background token refresher started.")
    else:
        app.logger.info("Running on Vercel – background scheduler disabled. Use /refresh endpoint manually.")

# ========================== FLASK ROUTES ==========================
@app.route('/like', methods=['GET'])
def handle_requests():
    global refresh_in_progress, all_tokens
    uid = request.args.get("uid")
    
    # ইউজার যদি server_name না দেয়, তবে এপিআই অটোমেটিক ডিফল্ট 'BD' সার্ভার ধরে নেবে
    server_name = request.args.get("server_name", "BD").upper()
    
    if not uid:
        return jsonify({
            "error": "UID is strictly required!"
        }), 400

    if refresh_in_progress:
        return jsonify({
            "status": "refreshing",
            "message": "Token refresh in progress. Please wait a few moments."
        }), 503

    tokens = all_tokens.copy()
    if not tokens:
        return jsonify({
            "status": "empty",
            "message": "No active tokens found. Please trigger /refresh first."
        }), 503

    try:
        encrypted_uid = enc(int(uid))
        if not encrypted_uid:
            raise Exception("Failed to encrypt player UID safely.")

        # Get player info before like
        before_info, before_idx = get_player_info(encrypted_uid, server_name, tokens)
        if before_info is None:
            raise Exception("Could not retrieve player info before like using any token")

        jsone = MessageToJson(before_info)
        data_before = json.loads(jsone)
        before_like = int(data_before.get('AccountInfo', {}).get('Likes', 0))
        app.logger.info(f"⚡ Initial likes tracked: {before_like}")

        # Dynamic Garena Server URL Routing (Optimized for BD/SG)
        if server_name == "IND":
            url = "https://client.ind.freefiremobile.com/LikeProfile"
        elif server_name in {"BR", "US", "SAC", "NA"}:
            url = "https://client.us.freefiremobile.com/LikeProfile"
        elif server_name in {"BD", "SG"}:
            url = "https://client.sg.freefiremobile.com/LikeProfile"
        else:
            url = "https://clientbp.ggpolarbear.com/LikeProfile"

        # Fire likes using all valid tokens asynchronously
        asyncio.run(send_multiple_requests(int(uid), server_name, url, tokens))

        # Get player info after like
        after_info, after_idx = get_player_info(encrypted_uid, server_name, tokens)
        if after_info is None:
            raise Exception("Could not retrieve player info after like using any token")

        jsone_after = MessageToJson(after_info)
        data_after = json.loads(jsone_after)
        
        after_like = int(data_after.get('AccountInfo', {}).get('Likes', 0))
        player_uid = int(data_after.get('AccountInfo', {}).get('UID', 0))
        player_name = str(data_after.get('AccountInfo', {}).get('PlayerNickname', 'Unknown'))
        
        like_given = after_like - before_like

        # ইউজার রিকোয়েস্ট অনুযায়ী কাস্টমাইজড প্রিমিয়াম রেসপন্স ফরম্যাট
        return jsonify({
            "Name": player_name,
            "UID": player_uid,
            "Server": server_name,
            "Before like": before_like,
            "Givenby api": like_given,
            "After like": after_like,
            "Channel": "@FREXY_LIKE",
            "Owner": "@Frexy1only"
        }), 200

    except Exception as e:
        app.logger.error(f"❌ Main request processing failed: {e}")
        return jsonify({
            "status": "failed",
            "error_log": str(e),
            "hint": f"Please verify if your tokens support the '{server_name}' region and are fully active."
        }), 500


@app.route('/jwt', methods=['GET', 'POST'])
def refresh():
    global refresh_in_progress
    if refresh_in_progress:
        return jsonify({"message": "Okay boss.. Please wait a minute..."}), 202

    def refresh_task():
        refresh_all_tokens()
    threading.Thread(target=refresh_task, daemon=True).start()
    return jsonify({"message": "Token refresh started. It may take a few minutes. Check status later."}), 202

@app.route('/ch', methods=['GET'])
def status():
    return jsonify({
        "refresh_in_progress": refresh_in_progress,
        "total_tokens": len(all_tokens),
        "last_refresh": str(last_refresh_time) if last_refresh_time else "never"
    })

# ========================== ENTRY POINT ==========================
if __name__ == '__main__':
    start_background_scheduler()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)), debug=False)
