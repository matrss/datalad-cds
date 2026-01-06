import functools
import hashlib
import subprocess
import sys


def generate_key_for_file(file: str) -> str:
    size = 0
    hash_md5 = hashlib.md5()
    with subprocess.Popen(
        ["grib_copy", file, "/dev/stdout"], stdout=subprocess.PIPE
    ) as grib_copy_proc:
        assert (
            grib_copy_proc.stdout is not None
        ), "this can never happen, but mypy needs it to realize that stdout is set"
        for chunk in iter(
            functools.partial(grib_copy_proc.stdout.read, 128 * 1024), b""
        ):
            size += len(chunk)
            hash_md5.update(chunk)
    if grib_copy_proc.returncode != 0:
        raise Exception("failed to run grib_copy")
    return "XGRIBNORMV1-s{}--{}".format(size, hash_md5.hexdigest())


def main() -> None:
    for line in sys.stdin:
        match line.strip().split():
            case ["GETVERSION"]:
                print("VERSION 1")
            case ["CANVERIFY"]:
                print("CANVERIFY-YES")
            case ["ISSTABLE"]:
                print("ISSTABLE-YES")
            case ["ISCRYPTOGRAPHICALLYSECURE"]:
                # MD5 is not cryptographically secure, but even if a cryptographically secure
                # hash was used the fact that this backend deliberately assigns the same hash
                # to different files would make me hesitate to call it secure.
                print("ISCRYPTOGRAPHICALLYSECURE-NO")
            case ["GENKEY", file]:
                try:
                    key = generate_key_for_file(file)
                    print("GENKEY-SUCCESS", key)
                except Exception as e:
                    print("GENKEY-FAILURE", e)
            case ["VERIFYKEYCONTENT", key_to_verify, file]:
                try:
                    key = generate_key_for_file(file)
                    if key_to_verify.split("-")[-1] == key.split("-")[-1]:
                        print("VERIFYKEYCONTENT-SUCCESS")
                    else:
                        print("VERIFYKEYCONTENT-FAILURE")
                except Exception:
                    print("VERIFYKEYCONTENT-FAILURE")
