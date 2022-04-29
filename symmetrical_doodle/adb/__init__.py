import asyncio
import asyncio.subprocess
import dataclasses
import shutil
from typing import Optional


def get_executable():
    path = shutil.which('adb')
    assert path is not None
    return path


@dataclasses.dataclass
class CompletedProcess:
    returncode: int
    program: str
    args: list[str]
    stdout: Optional[bytes]
    stderr: Optional[bytes]
    pid: int


@dataclasses.dataclass
class SimpleADB:
    program: str = dataclasses.field(default_factory=get_executable)
    global_options: list[str] = dataclasses.field(default_factory=list)

    def get_args(self, command: list[str]):
        return self.global_options + command

    def run_command(
        self,
        command: list[str],
        stdin=None,
        stdout=None,
        stderr=None,
        limit=None,
        **kwds
    ):
        args = self.get_args(command)
        if limit is None:
            return asyncio.create_subprocess_exec(
                self.program,
                *args,
                stdin=stdin,
                stdout=stdout,
                stderr=stderr,
                **kwds
            )
        else:
            return asyncio.create_subprocess_exec(
                self.program,
                *args,
                stdin=stdin,
                stdout=stdout,
                stderr=stderr,
                limit=limit,
                **kwds
            )

    async def check(
        self,
        command: list[str],
        stdin=None,
        stdout=None,
        stderr=None,
        limit=None,
        **kwds
    ):
        process = await self.run_command(
            command,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            limit=limit,
            **kwds
        )
        args = self.get_args(command)
        stdout, stderr = await process.communicate()
        completed_process = CompletedProcess(
            process.returncode, self.program, args, stdout, stderr, process.pid
        )
        if process.returncode:
            raise CalledProcessError(completed_process)
        return completed_process


@dataclasses.dataclass
class Transport:
    id: int
    state: bytes

    # Used to identify transports for clients.
    serial: bytes
    product: bytes
    model: bytes
    device: bytes
    devpath: bytes


def extract_transport_info(result: bytes, key: bytes):
    result, sep, value = result.rpartition(b' ' + key)
    if not sep:
        raise ValueError
    return result, value


PERMISSIONS_HELP_URL = b'http://developer.android.com/tools/device.html'

CONNECTION_STATES = (
    b'offline', b'bootloader', b'device', b'host', b'recovery', b'rescue',
    b'sideload', b'unauthorized', b'authorizing', b'connecting', b'unknown'
)


# https://cs.android.com/android/platform/superproject/+/master:packages/modules/adb/transport.cpp;l=1414;drc=713f665af47e943a378b818c3056cb30e0f786e6
def parse_device(line: bytes):
    if line.startswith(
        b'(no serial number)' + b' ' * (22 - len(b'(no serial number)'))
    ):
        serial = b''
    else:
        serial = line[:22].rstrip()
    line = line[22:]
    line, transport_id = extract_transport_info(line, b'transport_id:')
    transport_id = int(transport_id)
    try:
        line, device = extract_transport_info(line, b'device:')
    except ValueError:
        device = b''
    try:
        line, model = extract_transport_info(line, b'model:')
    except ValueError:
        model = b''
    try:
        line, product = extract_transport_info(line, b'product:')
    except ValueError:
        product = b''
    assert line.startswith(b' ')
    line = line[len(b' '):]
    if line.startswith(b'no permissions'):
        index = line.index(PERMISSIONS_HELP_URL)
        assert index == line.rindex(PERMISSIONS_HELP_URL)
        state_length = index + len(PERMISSIONS_HELP_URL) + len(b']')
        state = line[:state_length]
        line = line[state_length:]
        devpath = line.removeprefix(b' ')
    else:
        state, _, devpath = line.partition(b' ')
        assert state in CONNECTION_STATES
    return Transport(
        transport_id, state, serial, product, model, device, devpath
    )


class Error(Exception):
    pass


@dataclasses.dataclass
class CalledProcessError(Error):
    completed_process: CompletedProcess


# https://cs.android.com/android/platform/superproject/+/master:packages/modules/adb/client/commandline.cpp;l=1493;drc=179de72e9d5236d99369f480b8503c07c8ae4b9c
def adb_query_command_remove_trailing_newline(s: bytes):
    assert s.endswith(b'\n')
    return s[:-len(b'\n')]


@dataclasses.dataclass
class ADB(SimpleADB):

    def use_usb_device(self, value: bool):
        if value:
            self.use_tcpip_device(False)
            del self.serial
            del self.transport_id
            try:
                self.global_options.index('-d')
            except ValueError:
                self.global_options.append('-d')
        else:
            try:
                self.global_options.remove('-d')
            except ValueError:
                pass

    def use_tcpip_device(self, value: bool):
        if value:
            self.use_usb_device(False)
            del self.serial
            del self.transport_id
            try:
                self.global_options.index('-e')
            except ValueError:
                self.global_options.append('-e')
        else:
            try:
                self.global_options.remove('-e')
            except ValueError:
                pass

    @property
    def serial(self):
        index = self.global_options.index('-s')
        return self.global_options[index + 1]

    @serial.setter
    def serial(self, value: str):
        self.use_usb_device(False)
        self.use_tcpip_device(False)
        del self.transport_id
        try:
            index = self.global_options.index('-s')
        except ValueError:
            self.global_options.extend(['-s', value])
            return
        self.global_options[index + 1] = value

    @serial.deleter
    def serial(self):
        try:
            index = self.global_options.index('-s')
        except ValueError:
            return
        self.global_options = self.global_options[:index] + self.global_options[
            index + 2:]

    @property
    def transport_id(self):
        index = self.global_options.index('-t')
        return int(self.global_options[index + 1])

    @transport_id.setter
    def transport_id(self, value: int):
        self.use_usb_device(False)
        self.use_tcpip_device(False)
        del self.serial
        value = str(value)
        try:
            index = self.global_options.index('-t')
        except ValueError:
            self.global_options.extend(['-t', value])
            return
        self.global_options[index + 1] = value

    @transport_id.deleter
    def transport_id(self):
        try:
            index = self.global_options.index('-t')
        except ValueError:
            return
        self.global_options = self.global_options[:index] + self.global_options[
            index + 2:]

    async def list_connected_devices(self):
        process = await self.check(
            ['devices', '-l'],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        assert process.stdout is not None
        assert process.stdout.startswith(b'List of devices attached\n')
        result = adb_query_command_remove_trailing_newline(
            process.stdout[len(b'List of devices attached\n'):]
        )
        return [parse_device(line) for line in result.splitlines()]

    # https://cs.android.com/android/platform/superproject/+/master:packages/modules/adb/client/transport_local.cpp;l=81;drc=c354ca76a14d3bc5bfe8d95b08046580eb0a7036
    async def connect(self, host: str, port: Optional[int] = None):
        if port is None:
            command = ['connect', host]
        else:
            command = ['connect', f'{host}:{port}']
        process = await self.check(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        assert process.stdout is not None
        return adb_query_command_remove_trailing_newline(process.stdout)

    # https://cs.android.com/android/platform/superproject/+/master:packages/modules/adb/adb.cpp;l=1297;drc=5703eb352612566e8e5d099c99c2cecfaf22429d
    async def disconnect(
        self, host: Optional[str] = None, port: Optional[int] = None
    ):
        if host is None:
            assert port is None
            command = ['disconnect']
        else:
            if port is None:
                command = ['disconnect', host]
            else:
                command = ['disconnect', f'{host}:{port}']
        process = await self.check(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        assert process.stdout is not None
        return adb_query_command_remove_trailing_newline(process.stdout)

    def forward(self, local: str, remote: str, stdout=None):
        return self.run_command(['forward', local, remote], stdout=stdout)

    def forward_remove(self, local: str):
        return self.check(
            ['forward', '--remove', local],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

    def reverse(self, remote: str, local: str):
        return self.run_command(['reverse', remote, local])

    def reverse_remove(self, remote: str):
        return self.run_command(['reverse', '--remove', remote])

    def push(self, locals: list[str], remote: str):
        return self.run_command(['push', *locals, remote])

    async def get_serialno(self):
        process = await self.check(
            ['get-serialno'],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        assert process.stdout is not None
        result = adb_query_command_remove_trailing_newline(process.stdout)
        if result == b'unknown':
            return b''
        else:
            return result

    def start_server(self):
        return self.run_command(['start-server'])
