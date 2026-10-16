#!/usr/bin/env python3
"""Caesar cipher encryption, decryption, and brute-force cracking."""
import argparse
import re
import urllib.request
import urllib.error
import json
from typing import Optional

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

def transform(text: str, shift: int) -> str:
    result = []
    for char in text:
        lower = char.lower()
        if lower in ALPHABET:
            index = ALPHABET.index(lower)
            encoded = ALPHABET[(index + shift) % 26]
            result.append(encoded.upper() if char.isupper() else encoded)
        else:
            result.append(char)
    return "".join(result)

def english_score(text: str) -> float:
    words = re.findall(r"[A-Za-z']+", text.lower())
    if not words:
        return 0.0
    common = {"the", "be", "to", "of", "and", "a", "in", "that", "have",
              "i", "it", "for", "not", "on", "with", "he", "as", "you",
              "do", "at", "this", "but", "his", "by", "from", "they",
              "we", "say", "her", "she", "or", "an", "will", "my", "one",
              "all", "would", "there", "their", "what", "so", "up", "out",
              "if", "about", "who", "get", "which", "go", "me", "hello", "world"}
    return sum(word in common for word in words) / len(words)

def dictionary_api_score(text: str, timeout: float = 3.0) -> Optional[float]:
    """Optional dictionary check using dictionaryapi.dev for individual candidate words."""
    words = re.findall(r"[A-Za-z]{3,}", text.lower())
    if not words:
        return None
    sample = list(dict.fromkeys(words))[:5]
    valid = 0
    checked = 0
    for word in sample:
        url = "https://api.dictionaryapi.dev/api/v2/entries/en/" + word
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            if isinstance(data, list) and data:
                valid += 1
            checked += 1
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            continue
    return valid / checked if checked else None

def crack(ciphertext: str, threshold: float = 0.90, use_api: bool = False):
    candidates = []
    for shift in range(26):
        plaintext = transform(ciphertext, -shift)
        score = english_score(plaintext)
        api_score = dictionary_api_score(plaintext) if use_api else None
        confidence = api_score if api_score is not None else score
        candidates.append((confidence, shift, plaintext, score, api_score))
    candidates.sort(reverse=True, key=lambda item: item[0])
    best = candidates[0]
    return {
        "shift": best[1],
        "plaintext": best[2],
        "confidence": best[0],
        "threshold_met": best[0] >= threshold,
        "method": "dictionary API" if use_api and best[4] is not None else "local word heuristic",
        "candidates": candidates
    }

def main():
    parser = argparse.ArgumentParser(description="Caesar cipher toolkit")
    sub = parser.add_subparsers(dest="command", required=True)
    enc = sub.add_parser("encrypt", help="Encrypt text")
    enc.add_argument("text")
    enc.add_argument("--shift", type=int, required=True)
    dec = sub.add_parser("decrypt", help="Decrypt text")
    dec.add_argument("text")
    dec.add_argument("--shift", type=int, required=True)
    crack_p = sub.add_parser("crack", help="Try all 26 shifts")
    crack_p.add_argument("text")
    crack_p.add_argument("--threshold", type=float, default=0.90)
    crack_p.add_argument("--api", action="store_true", help="Use optional dictionary API checks")
    args = parser.parse_args()

    if args.command == "encrypt":
        print(transform(args.text, args.shift))
    elif args.command == "decrypt":
        print(transform(args.text, -args.shift))
    else:
        result = crack(args.text, args.threshold, args.api)
        print(f"Shift: {result['shift']}")
        print(f"Plaintext: {result['plaintext']}")
        print(f"Confidence: {result['confidence']:.0%} ({result['method']})")
        print(f"Threshold met: {result['threshold_met']}")
        if not result["threshold_met"]:
            print("Warning: confidence threshold not reached; review candidates before trusting the result.")
        print("\nTop candidates:")
        for confidence, shift, plaintext, _, _ in result["candidates"][:5]:
            print(f"  shift={shift:2d} score={confidence:.0%} {plaintext}")

if __name__ == "__main__":
    main()
