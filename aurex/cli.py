"""Local AUREX CLI."""

import argparse
import json

from aurex.challengers.rules import EvidencePresenceChallenger
from aurex.engine import AurexEngine
from aurex.protocol import ChallengeRequest


def main() -> None:
    parser = argparse.ArgumentParser(prog="aurex")
    parser.add_argument("claim")
    parser.add_argument("--request-id", default="local")
    args = parser.parse_args()
    request = ChallengeRequest(request_id=args.request_id, claim=args.claim)
    results = AurexEngine([EvidencePresenceChallenger()]).evaluate(request)
    print(json.dumps([item.model_dump(mode="json") for item in results], indent=2))


if __name__ == "__main__":
    main()
