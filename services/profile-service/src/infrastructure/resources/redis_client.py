from redis.asyncio import Redis
from typing import Optional


class RedisClient:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        decode_responses: bool = True,
    ):
        self._client: Optional[Redis] = None
        self._host = host
        self._port = port
        self._db = db
        self._password = password
        self._decode_responses = decode_responses

    async def connect(self) -> None:
        self._client = Redis(
            host=self._host,
            port=self._port,
            db=self._db,
            password=self._password,
            decode_responses=self._decode_responses,
        )

    async def disconnect(self) -> None:
        if self._client:
            await self._client.close()

    @property
    def client(self) -> Redis:
        if not self._client:
            raise RuntimeError("Redis client is not connected")
        return self._client
