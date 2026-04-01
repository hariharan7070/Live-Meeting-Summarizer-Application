const sessionChunks = new Map<number, Buffer[]>();
const sessionChunkCount = new Map<number, number>();

export function initSession(sessionId: number): void {
  sessionChunks.set(sessionId, []);
  sessionChunkCount.set(sessionId, 0);
}

export function addChunk(sessionId: number, chunk: Buffer): number {
  const chunks = sessionChunks.get(sessionId);
  if (!chunks) throw new Error(`Session ${sessionId} not found in store`);
  chunks.push(chunk);
  const count = (sessionChunkCount.get(sessionId) ?? 0) + 1;
  sessionChunkCount.set(sessionId, count);
  return count - 1;
}

export function getChunks(sessionId: number): Buffer[] {
  return sessionChunks.get(sessionId) ?? [];
}

export function clearSession(sessionId: number): Buffer[] {
  const chunks = sessionChunks.get(sessionId) ?? [];
  sessionChunks.delete(sessionId);
  sessionChunkCount.delete(sessionId);
  return chunks;
}

export function hasSession(sessionId: number): boolean {
  return sessionChunks.has(sessionId);
}
