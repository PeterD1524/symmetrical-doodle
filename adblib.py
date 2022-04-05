import asyncio
import asyncio.subprocess
import dataclasses


def get_executable():
    return 'adb'


@dataclasses.dataclass
class ADB:
    program: str

    async def start_server(self) -> asyncio.subprocess.Process:
        return await self.run_command(['start-server'])

    async def forward(
        self,
        local: str,
        remote: str,
        stdout=None
    ) -> asyncio.subprocess.Process:
        return await self.run_command(
            ['forward', local, remote], stdout=stdout
        )

    async def forward_remove(self, local: str) -> asyncio.subprocess.Process:
        return await self.run_command(['forward', '--remove', local])

    async def reverse(
        self, remote: str, local: str
    ) -> asyncio.subprocess.Process:
        return await self.run_command(['reverse', remote, local])

    async def reverse_remove(self, remote: str) -> asyncio.subprocess.Process:
        return await self.run_command(['reverse', '--remove', remote])

    async def push(
        self, locals: list[str], remote: str
    ) -> asyncio.subprocess.Process:
        return await self.run_command(['push', *locals, remote])

    async def run_command(
        self, command: list[str], stdout=None
    ) -> asyncio.subprocess.Process:
        print('[adb]', command)
        return await asyncio.create_subprocess_exec(
            self.program, *command, stdout=stdout
        )
