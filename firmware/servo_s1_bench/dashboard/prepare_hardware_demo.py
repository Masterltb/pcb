#!/usr/bin/env python3
"""Prepare local TLS MQTT credentials/certificates and ignored secrets.h for ESP32 test."""
from __future__ import annotations

import getpass
import ipaddress
import os
import secrets
import socket
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

ROOT = Path(__file__).resolve().parent
LOCAL = ROOT / ".local-hardware"
SECRETS = ROOT.parent / "secrets.h"
DEVICE_ID = "rev-s3-s1-bench-01"


def local_route_ip() -> str:
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("192.0.2.1", 80))
        return probe.getsockname()[0]
    except OSError:
        return ""
    finally:
        probe.close()


def pem_private_key(key) -> bytes:
    return key.private_bytes(serialization.Encoding.PEM,
                             serialization.PrivateFormat.TraditionalOpenSSL,
                             serialization.NoEncryption())


def c_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("\r", "").replace("\n", "\\n") + '"'


def write_certs(host_ip: str) -> None:
    now = datetime.now(timezone.utc)
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "FreshVend Local MQTT Test CA")])
    ca_cert = (x509.CertificateBuilder().subject_name(ca_name).issuer_name(ca_name)
               .public_key(ca_key.public_key()).serial_number(x509.random_serial_number())
               .not_valid_before(now - timedelta(minutes=5)).not_valid_after(now + timedelta(days=3650))
               .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
               .add_extension(x509.KeyUsage(digital_signature=True, key_encipherment=False,
                            key_cert_sign=True, key_agreement=False, content_commitment=False,
                            data_encipherment=False, crl_sign=True, encipher_only=False,
                            decipher_only=False), critical=True)
               .add_extension(x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()),
                              critical=False)
               .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
                              critical=False).sign(ca_key, hashes.SHA256()))

    server_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    server_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, host_ip)])
    sans = [x509.IPAddress(ipaddress.ip_address(host_ip)), x509.DNSName("mqtt"),
            x509.DNSName("localhost")]
    server_cert = (x509.CertificateBuilder().subject_name(server_name).issuer_name(ca_name)
                   .public_key(server_key.public_key()).serial_number(x509.random_serial_number())
                   .not_valid_before(now - timedelta(minutes=5)).not_valid_after(now + timedelta(days=397))
                   .add_extension(x509.SubjectAlternativeName(sans), critical=False)
                   .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
                   .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
                   .add_extension(x509.SubjectKeyIdentifier.from_public_key(server_key.public_key()),
                                  critical=False)
                   .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
                                  critical=False)
                   .sign(ca_key, hashes.SHA256()))

    (LOCAL / "ca.crt").write_bytes(ca_cert.public_bytes(serialization.Encoding.PEM))
    (LOCAL / "server.crt").write_bytes(server_cert.public_bytes(serialization.Encoding.PEM))
    (LOCAL / "server.key").write_bytes(pem_private_key(server_key))


def write_password_file(device_password: str, dashboard_password: str) -> None:
    mount_path = f"{LOCAL.resolve()}:/certs"
    (LOCAL / "passwd").unlink(missing_ok=True)
    subprocess.run(["docker", "run", "--rm", "-v", mount_path,
                    "eclipse-mosquitto:2", "mosquitto_passwd", "-b", "-c",
                    "/certs/passwd", "fv-device", device_password],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["docker", "run", "--rm", "-v", mount_path,
                    "eclipse-mosquitto:2", "mosquitto_passwd", "-b",
                    "/certs/passwd", "fv-dashboard", dashboard_password],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # mosquitto drops privileges before opening password_file. The file created
    # by mosquitto_passwd is mode 0600, so make the hash-only file readable.
    subprocess.run(["docker", "run", "--rm", "-v", mount_path,
                    "eclipse-mosquitto:2", "chmod", "0644", "/certs/passwd"],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main() -> int:
    if not shutil_which("docker"):
        print("Không tìm thấy Docker CLI.", file=sys.stderr)
        return 2
    check = subprocess.run(["docker", "info", "--format", "{{.ServerVersion}}"],
                           capture_output=True, text=True)
    if check.returncode:
        print("Hãy khởi động Docker Desktop rồi chạy lại script.", file=sys.stderr)
        return 2

    if SECRETS.exists():
        print(f"Script sẽ thay thế file cấu hình cục bộ: {SECRETS}")
        if input("Gõ REPLACE để tiếp tục: ").strip() != "REPLACE":
            print("Đã hủy; không thay đổi cấu hình.")
            return 1
    if LOCAL.exists() and any(LOCAL.iterdir()):
        print(f"Script sẽ tạo lại chứng chỉ và tài khoản trong: {LOCAL}")
        if input("Gõ REGENERATE để tiếp tục: ").strip() != "REGENERATE":
            print("Đã hủy; không thay đổi cấu hình.")
            return 1
    LOCAL.mkdir(parents=True, exist_ok=True)

    detected = local_route_ip()
    host_ip = input(f"IPv4 của PC trên cùng LAN với board [{detected}]: ").strip() or detected
    try:
        host_ip = str(ipaddress.IPv4Address(host_ip))
    except ipaddress.AddressValueError:
        print("Địa chỉ IPv4 không hợp lệ.", file=sys.stderr)
        return 2

    ssid = input("Tên Wi-Fi 2.4 GHz cho ESP32: ").strip()
    if not ssid:
        print("SSID không được để trống.", file=sys.stderr)
        return 2
    wifi_password = getpass.getpass("Mật khẩu Wi-Fi (không hiển thị khi nhập): ")
    if getpass.getpass("Nhập lại mật khẩu Wi-Fi: ") != wifi_password:
        print("Hai lần nhập mật khẩu không khớp.", file=sys.stderr)
        return 2

    device_password = secrets.token_urlsafe(32)
    dashboard_password = secrets.token_urlsafe(32)
    admin_token = secrets.token_urlsafe(32)
    try:
        write_certs(host_ip)
        write_password_file(device_password, dashboard_password)
    except Exception as error:
        print(f"Không tạo được tài khoản/chứng chỉ cục bộ: {error}", file=sys.stderr)
        return 2

    acl = (f"user fv-device\ntopic read freshvend/{DEVICE_ID}/admin/command\n"
           f"topic write freshvend/{DEVICE_ID}/admin/ack\n"
           f"topic write freshvend/{DEVICE_ID}/status\n"
           f"topic write freshvend/{DEVICE_ID}/availability\n\n"
           f"user fv-dashboard\ntopic write freshvend/{DEVICE_ID}/admin/command\n"
           f"topic read freshvend/{DEVICE_ID}/admin/ack\n"
           f"topic read freshvend/{DEVICE_ID}/status\n"
           f"topic read freshvend/{DEVICE_ID}/availability\n")
    (LOCAL / "acl").write_text(acl, encoding="utf-8")
    env_text = (f"FV_BROKER_BIND_IP={host_ip}\n"
                f"FV_DEVICE_MQTT_PASSWORD={device_password}\n"
                f"FV_DASHBOARD_MQTT_PASSWORD={dashboard_password}\n"
                f"FV_ADMIN_TOKEN={admin_token}\n")
    (ROOT / ".env.hardware").write_text(env_text, encoding="utf-8")
    (ROOT / "admin-token.txt").write_text(admin_token + "\n", encoding="utf-8")

    cert = (LOCAL / "ca.crt").read_text(encoding="ascii").strip()
    secret_header = f'''#pragma once

#define WIFI_SSID {c_string(ssid)}
#define WIFI_PASSWORD {c_string(wifi_password)}
#define MQTT_HOST {c_string(host_ip)}
#define MQTT_PORT 8883
#define MQTT_USERNAME "fv-device"
#define MQTT_PASSWORD {c_string(device_password)}

static const char MQTT_CA_CERT[] PROGMEM = R"FVCERT(
{cert}
)FVCERT";
'''
    SECRETS.write_text(secret_header, encoding="utf-8")
    print("Đã tạo cấu hình broker TLS cục bộ và firmware secrets.h.")
    print(f"Địa chỉ broker cho ESP32: {host_ip}:8883")
    print(f"Mã đăng nhập dashboard lưu trong: {ROOT / 'admin-token.txt'}")
    print("Chưa mở firewall; nếu board không kết nối, chỉ cho phép TCP 8883 trên Private network.")
    return 0


def shutil_which(name: str) -> str | None:
    from shutil import which
    return which(name)


if __name__ == "__main__":
    raise SystemExit(main())
