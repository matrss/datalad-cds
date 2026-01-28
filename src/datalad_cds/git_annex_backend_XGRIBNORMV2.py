import functools
import subprocess
import sys
import typing


@functools.wraps(print)
def send_message(*args: typing.Any, **kwargs: typing.Any) -> None:
    print(*args, **kwargs)
    sys.stdout.flush()


def generate_key_for_file(file: str) -> str:
    with subprocess.Popen(
        [
            "grib_copy",
            "-B",
            "date asc, time:i asc, step:i asc, level:i asc, name asc",
            file,
            "/dev/stdout",
        ],
        stdout=subprocess.PIPE,
    ) as grib_copy_proc:
        assert grib_copy_proc.stdout is not None, (
            "this can never happen, but mypy needs it to realize that stdout is set"
        )
        md5sum_result = subprocess.run(
            ["md5sum", "-"],
            capture_output=True,
            stdin=grib_copy_proc.stdout,
            text=True,
            check=True,
        )
    if grib_copy_proc.returncode != 0:
        raise Exception("failed to run grib_copy")
    md5_hexdigest = md5sum_result.stdout.split()[0]
    return "XGRIBNORMV2--{}".format(md5_hexdigest)


def main() -> None:
    for line in sys.stdin:
        match line.strip().split():
            case ["GETVERSION"]:
                send_message("VERSION 1")
            case ["CANVERIFY"]:
                send_message("CANVERIFY-YES")
            case ["ISSTABLE"]:
                send_message("ISSTABLE-YES")
            case ["ISCRYPTOGRAPHICALLYSECURE"]:
                # MD5 is not cryptographically secure, but even if a cryptographically secure
                # hash was used the fact that this backend deliberately assigns the same hash
                # to different files would make me hesitate to call it secure.
                send_message("ISCRYPTOGRAPHICALLYSECURE-NO")
            case ["GENKEY", file]:
                try:
                    key = generate_key_for_file(file)
                    send_message("GENKEY-SUCCESS", key)
                except Exception as e:
                    send_message("GENKEY-FAILURE", e)
            case ["VERIFYKEYCONTENT", key_to_verify, file]:
                try:
                    key = generate_key_for_file(file)
                    if key_to_verify.split("-")[-1] == key.split("-")[-1]:
                        send_message("VERIFYKEYCONTENT-SUCCESS")
                    else:
                        send_message("VERIFYKEYCONTENT-FAILURE")
                except Exception:
                    send_message("VERIFYKEYCONTENT-FAILURE")
