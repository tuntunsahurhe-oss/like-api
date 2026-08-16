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
from concurrent.futures import ThreadPoolExecutor, as_completed

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
TOKEN_GEN_API = "https://frexy-jwt-gen.vercel.app/token"
TOKEN_REFRESH_INTERVAL_HOURS = 7  # 7 ঘণ্টা পর পর রিফ্রেশ

# Global token cache
all_tokens = []
refresh_lock = threading.Lock()
refresh_in_progress = False
last_refresh_time = None
first_refresh_done = False

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
        resp = requests.post(url, data=edata, headers=headers, verify=False, timeout=30)
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
            async with session.post(url, data=edata, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
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
    for idx, t in enumerate(token_list):
        info = make_request(encrypted_uid, server_name, t["token"])
        if info is not None:
            return info, idx
    return None, -1

# ========================== TOKEN CONVERSIONS ==========================
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
        resp = requests.post(url, data=encrypted_payload, headers=headers, verify=False, timeout=30)
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
    inspect_url = f"https://100067.connect.garena.com/oauth/token/inspect?token={access_token}"
    try:
        insp_resp = requests.get(inspect_url, timeout=30)
        if insp_resp.status_code != 200:
            return None
        insp_data = insp_resp.json()
        open_id = insp_data.get('open_id')
        if not open_id:
            return None
    except Exception as e:
        app.logger.error(f"Inspect request failed: {e}")
        return None

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

def guest_to_jwt(uid: str, password: str) -> dict:
    """শুধু নতুন API ব্যবহার করবে - ধীরে কিন্তু ১০০% সফল"""
    try:
        params = {
            "uid": uid,
            "password": password
        }
        
        # বেশি টাইমআউট দিচ্ছি যেন API রেসপন্স দিতে পারে
        resp = requests.get(TOKEN_GEN_API, params=params, timeout=180)  # 3 মিনিট টাইমআউট
        resp.raise_for_status()
        data = resp.json()
        
        # চেক করি সফল হয়েছে কিনা
        if data.get("status") == "success" or data.get("Status") == "success":
            account_uid = data.get("uid") or data.get("account_id") or data.get("accountId") or uid
            jwt_token = data.get("jwt") or data.get("token") or data.get("Token") or data.get("access_token")
            region = data.get("region") or data.get("lock_region") or data.get("lockRegion") or "BD"
            
            if jwt_token:
                return {
                    "uid": str(account_uid),
                    "token": jwt_token,
                    "region": region,
                    "type": "guest"
                }
        
        # যদি সফল না হয়
        error_msg = data.get('message') or data.get('error') or 'Unknown error'
        app.logger.error(f"API error for UID {uid}: {error_msg}")
        
    except requests.exceptions.Timeout:
        app.logger.error(f"Timeout for UID {uid} - API taking too long")
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Request error for UID {uid}: {str(e)}")
    except Exception as e:
        app.logger.error(f"Error for UID {uid}: {str(e)}")
    
    return None

# ========================== TOKEN REFRESH - ধীরে কিন্তু ১০০% সফল ==========================
def process_account_line(line):
    """Process a single account line - ধীরে কিন্তু সফল"""
    line = line.strip()
    if not line or line.startswith('#'):
        return None
    if ':' not in line:
        return None
    uid, pwd = line.split(':', 1)
    uid = uid.strip()
    pwd = pwd.strip()
    
    # প্রতিটি অ্যাকাউন্টের জন্য ৩ বার চেষ্টা করবে
    for attempt in range(1, 4):
        result = guest_to_jwt(uid, pwd)
        if result:
            return result
        if attempt < 3:
            time.sleep(2)  # ২ সেকেন্ড অপেক্ষা করে আবার চেষ্টা
    return None

def refresh_all_tokens():
    global all_tokens, refresh_in_progress, last_refresh_time, first_refresh_done
    with refresh_lock:
        if refresh_in_progress:
            return
        refresh_in_progress = True

    app.logger.info("="*60)
    app.logger.info("STARTING TOKEN REFRESH (7 Hours Interval)")
    app.logger.info("="*60)
    
    new_tokens = []
    success_count = 0
    fail_count = 0
    
    # Process guest accounts - ধীরে কিন্তু সফল
    if os.path.exists("accounts.txt"):
        with open("accounts.txt", "r") as f:
            lines = f.readlines()
        
        total_accounts = len([l for l in lines if l.strip() and not l.startswith('#') and ':' in l])
        app.logger.info(f"Total accounts to process: {total_accounts}")
        
        # প্রতিটি অ্যাকাউন্ট আলাদাভাবে প্রসেস করি (ধীরে)
        for idx, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ':' not in line:
                continue
                
            uid = line.split(':', 1)[0].strip()
            app.logger.info(f"[{idx}/{total_accounts}] Processing UID: {uid}")
            
            # ৩ বার চেষ্টা করব
            token = None
            for attempt in range(1, 4):
                result = guest_to_jwt(uid, line.split(':', 1)[1].strip())
                if result:
                    token = result
                    break
                if attempt < 3:
                    app.logger.info(f"  Retry {attempt}/3 for UID {uid}...")
                    time.sleep(3)  # ৩ সেকেন্ড অপেক্ষা
            
            if token:
                new_tokens.append(token)
                success_count += 1
                app.logger.info(f"  ✓ SUCCESS for UID: {uid}")
            else:
                fail_count += 1
                app.logger.info(f"  ✗ FAILED for UID: {uid}")
            
            # প্রতিটি অ্যাকাউন্টের মধ্যে ২ সেকেন্ড গ্যাপ (API লোড কমাতে)
            time.sleep(2)
    else:
        app.logger.warning("accounts.txt not found")

    # Process Eat tokens
    if os.path.exists("eat.txt"):
        with open("eat.txt", "r") as f:
            eat_lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
        app.logger.info(f"Processing {len(eat_lines)} eat tokens...")
        for line in eat_lines:
            jwt = eat_token_to_jwt(line)
            if jwt:
                new_tokens.append(jwt)
                success_count += 1
                app.logger.info(f"✓ SUCCESS for eat token: {line[:20]}...")
            else:
                fail_count += 1
                app.logger.info(f"✗ FAILED for eat token: {line[:20]}...")
            time.sleep(1)
    else:
        app.logger.warning("eat.txt not found")

    # Process Access tokens
    if os.path.exists("access.txt"):
        with open("access.txt", "r") as f:
            access_lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
        app.logger.info(f"Processing {len(access_lines)} access tokens...")
        for line in access_lines:
            jwt = access_token_to_jwt(line)
            if jwt:
                new_tokens.append(jwt)
                success_count += 1
                app.logger.info(f"✓ SUCCESS for access token: {line[:20]}...")
            else:
                fail_count += 1
                app.logger.info(f"✗ FAILED for access token: {line[:20]}...")
            time.sleep(1)
    else:
        app.logger.warning("access.txt not found")

    # Replace global list
    all_tokens = new_tokens
    last_refresh_time = datetime.now()
    first_refresh_done = True

    with refresh_lock:
        refresh_in_progress = False
    
    app.logger.info("="*60)
    app.logger.info(f"TOKEN REFRESH COMPLETED")
    app.logger.info(f"✓ Success: {success_count}")
    app.logger.info(f"✗ Failed: {fail_count}")
    app.logger.info(f"Total tokens: {len(all_tokens)}")
    app.logger.info("="*60)

def scheduled_refresh():
    """Background thread - ৭ ঘণ্টা পর পর রিফ্রেশ"""
    while True:
        time.sleep(TOKEN_REFRESH_INTERVAL_HOURS * 3600)
        app.logger.info(f"⏰ Auto-refresh triggered after {TOKEN_REFRESH_INTERVAL_HOURS} hours")
        refresh_all_tokens()

def start_background_scheduler():
    if os.environ.get("VERCEL") != "1":
        t = threading.Thread(target=scheduled_refresh, daemon=True)
        t.start()
        app.logger.info("Background token refresher started (7 hours interval).")
        app.logger.info("Use /jwt endpoint for manual first refresh.")

# ========================== FLASK ROUTES ==========================
@app.route('/like', methods=['GET'])
def handle_requests():
    global refresh_in_progress, all_tokens, first_refresh_done
    
    if not first_refresh_done:
        return jsonify({
            "error": "Please call /jwt first to generate tokens",
            "status": "initialization_required"
        }), 503
    
    uid = request.args.get("uid")
    server_name = request.args.get("server_name", "").upper()
    if not uid or not server_name:
        return jsonify({"error": "UID and server_name are required"}), 400

    if refresh_in_progress:
        return jsonify({"error": "Token refresh in progress. Please wait..."}), 503

    tokens = all_tokens.copy()
    if not tokens:
        return jsonify({"error": "No tokens available. Call /jwt first."}), 503

    try:
        encrypted_uid = enc(int(uid))
        if not encrypted_uid:
            raise Exception("Failed to encrypt UID")

        before_info, before_idx = get_player_info(encrypted_uid, server_name, tokens)
        if before_info is None:
            raise Exception("Could not retrieve player info before like")

        jsone = MessageToJson(before_info)
        data_before = json.loads(jsone)
        before_like = int(data_before.get('AccountInfo', {}).get('Likes', 0))

        if server_name == "IND":
            url = "https://client.ind.freefiremobile.com/LikeProfile"
        elif server_name in {"BR", "US", "SAC", "NA"}:
            url = "https://client.us.freefiremobile.com/LikeProfile"
        else:
            url = "https://clientbp.ggpolarbear.com/LikeProfile"

        asyncio.run(send_multiple_requests(int(uid), server_name, url, tokens))

        after_info, after_idx = get_player_info(encrypted_uid, server_name, tokens)
        if after_info is None:
            raise Exception("Could not retrieve player info after like")

        jsone_after = MessageToJson(after_info)
        data_after = json.loads(jsone_after)
        after_like = int(data_after.get('AccountInfo', {}).get('Likes', 0))
        player_uid = int(data_after.get('AccountInfo', {}).get('UID', 0))
        player_name = str(data_after.get('AccountInfo', {}).get('PlayerNickname', ''))
        like_given = after_like - before_like
        status = 1 if like_given != 0 else 2

        result = {
            "LikesGivenByAPI": like_given,
            "LikesafterCommand": after_like,
            "LikesbeforeCommand": before_like,
            "PlayerNickname": player_name,
            "UID": player_uid,
            "status": status,
            "tokens_used": len(tokens)
        }
        return jsonify(result)

    except Exception as e:
        app.logger.error(f"Main request processing failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/jwt', methods=['GET', 'POST'])
def refresh():
    global refresh_in_progress
    if refresh_in_progress:
        return jsonify({
            "message": "Token refresh already in progress. Please wait...",
            "status": "in_progress"
        }), 202

    def refresh_task():
        refresh_all_tokens()
    
    threading.Thread(target=refresh_task, daemon=True).start()
    return jsonify({
        "message": "Token refresh started. This will take time but will be 100% successful.",
        "status": "started",
        "refresh_interval": f"{TOKEN_REFRESH_INTERVAL_HOURS} hours (auto-refresh)",
        "note": "Each account will be retried 3 times if failed"
    }), 202

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "refresh_in_progress": refresh_in_progress,
        "total_tokens": len(all_tokens),
        "last_refresh": str(last_refresh_time) if last_refresh_time else "never",
        "first_refresh_done": first_refresh_done,
        "auto_refresh_interval": f"{TOKEN_REFRESH_INTERVAL_HOURS} hours"
    })

@app.route('/ch', methods=['GET'])
def status_old():
    return status()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "service": "FreeFire Token & Like API",
        "endpoints": {
            "/jwt": "Generate tokens from accounts.txt (GET/POST)",
            "/like?uid=UID&server_name=REGION": "Send likes",
            "/status": "Check token status"
        },
        "auto_refresh": f"Every {TOKEN_REFRESH_INTERVAL_HOURS} hours",
        "note": "First time: Call /jwt to generate tokens (takes time but 100% successful)"
    })

# ========================== ENTRY POINT ==========================
if __name__ == '__main__':
    start_background_scheduler()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)), debug=False)
