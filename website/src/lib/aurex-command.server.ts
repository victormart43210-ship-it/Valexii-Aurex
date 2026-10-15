import { createAurexClient, type ClientConfig } from "./aurex-client.server";
import { isOwner, createRateLimiter } from "./aurex-control";
const limit = createRateLimiter(60, 60_000);
/** userId must come exclusively from validated session middleware, never request data. */
export function ownerCommandClient(
  userId: string,
  config: ClientConfig & { ownerId?: string | undefined },
) {
  if (!isOwner(userId, config.ownerId)) throw new Error("Forbidden");
  if (!limit(userId)) throw new Error("Too many requests");
  return createAurexClient(config);
}
