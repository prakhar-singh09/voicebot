import { Room, RoomEvent } from "livekit-client";

export async function connectRoom(name) {
  const res = await fetch(
    `http://localhost:8001/token?name=${encodeURIComponent(name)}`
  );

  if (!res.ok) {
    throw new Error("Could not fetch LiveKit token");
  }

  const data = await res.json();

  const room = new Room({
    adaptiveStream: true,
    dynacast: true,
  });

  await room.connect(
    data.url,
    data.token
  );
  await fetch(
    "http://localhost:8001/agent/start",
    {
      method: "POST",
    }
  );

  return { room, roomName: data.room };
}

export { RoomEvent };
