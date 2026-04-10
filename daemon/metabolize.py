"""METABOLIZE Phase - Four organs, intentional computational cost"""

import hashlib
import logging
import time

import numpy as np
from argon2.low_level import Type, hash_secret_raw

log = logging.getLogger("metabolica.metabolize")

# Tunable cost parameters
HASHCHAIN_ITERATIONS = 100_000
ARGON2_TIME_COST = 3
ARGON2_MEMORY_KIB = 65536  # 64 MiB
GA_GENERATIONS = 80
GA_POP_SIZE = 24
CA_STEPS = 128
CA_WIDTH = 256


def stomach_hashchain(seed: bytes, iterations: int = HASHCHAIN_ITERATIONS) -> bytes:
    """Stomach - SHA-256 iterated. Time-is-proof digest."""
    current = seed
    for _ in range(iterations):
        current = hashlib.sha256(current).digest()
    return current


def liver_argon2(seed: bytes, salt: bytes) -> bytes:
    """Liver - Memory-hard KDF. GPU-resistant compression."""
    return hash_secret_raw(
        secret=seed,
        salt=salt,
        time_cost=ARGON2_TIME_COST,
        memory_cost=ARGON2_MEMORY_KIB,
        parallelism=2,
        hash_len=32,
        type=Type.ID,
    )


def heart_genetic_algorithm(seed: bytes) -> bytes:
    """Heart - Evolve a 32-byte chromosome toward matching the seed's bit pattern."""
    rng = np.random.default_rng(int.from_bytes(seed[:8], "big"))
    chrom_len = 32
    target_bits = np.unpackbits(np.frombuffer(seed, dtype=np.uint8))

    pop = rng.integers(0, 256, (GA_POP_SIZE, chrom_len), dtype=np.uint8)

    def fitness(chrom: np.ndarray) -> int:
        return int(np.sum(np.unpackbits(chrom) == target_bits))

    for _ in range(GA_GENERATIONS):
        scores = np.array([fitness(c) for c in pop])
        order = np.argsort(-scores)
        parents = pop[order[: GA_POP_SIZE // 2]]
        children = []
        for _ in range(GA_POP_SIZE - len(parents)):
            a, b = parents[rng.integers(0, len(parents), 2)]
            mask = rng.integers(0, 2, chrom_len, dtype=bool)
            child = np.where(mask, a, b).astype(np.uint8)
            if rng.random() < 0.15:
                idx = int(rng.integers(0, chrom_len))
                child[idx] ^= int(rng.integers(1, 256))
            children.append(child)
        pop = np.vstack([parents, np.array(children, dtype=np.uint8)])

    scores = np.array([fitness(c) for c in pop])
    best = pop[int(np.argmax(scores))]
    return bytes(best)


def brain_cellular_automata(seed: bytes, rule: int = 110) -> tuple[bytes, bytes]:
    """Brain - Rule 110 cellular automaton. Returns (final_state_bytes, history_bytes)."""
    state = np.zeros(CA_WIDTH, dtype=np.uint8)
    seed_bits = np.unpackbits(np.frombuffer(seed, dtype=np.uint8))
    state[: min(len(seed_bits), CA_WIDTH)] = seed_bits[:CA_WIDTH]

    rule_bits = np.array([(rule >> i) & 1 for i in range(8)], dtype=np.uint8)
    history = np.zeros((CA_STEPS + 1, CA_WIDTH), dtype=np.uint8)
    history[0] = state

    for step in range(CA_STEPS):
        left = np.roll(state, 1)
        right = np.roll(state, -1)
        idx = (left << 2) | (state << 1) | right
        state = rule_bits[idx]
        history[step + 1] = state

    return bytes(np.packbits(state)), bytes(np.packbits(history.flatten()))


def metabolize(seed: bytes) -> dict:
    """Run all four organs sequentially. Returns intermediate states + proof."""
    log.info("Metabolizing seed (%d bytes)...", len(seed))
    start = time.time()

    stomach = stomach_hashchain(seed)
    log.info("  Stomach (hashchain) done: %s", stomach.hex()[:16])

    liver = liver_argon2(stomach, salt=seed[:16])
    log.info("  Liver (argon2id) done: %s", liver.hex()[:16])

    heart = heart_genetic_algorithm(liver)
    log.info("  Heart (GA) done: %s", heart.hex()[:16])

    brain_final, brain_history = brain_cellular_automata(heart)
    log.info("  Brain (CA) done: %s", brain_final.hex()[:16])

    elapsed = time.time() - start
    log.info("Metabolism complete in %.2fs", elapsed)

    return {
        "stomach": stomach,
        "liver": liver,
        "heart": heart,
        "brain_final": brain_final,
        "brain_history": brain_history,
        "proof": {
            "hashchain_iterations": HASHCHAIN_ITERATIONS,
            "argon2_time_cost": ARGON2_TIME_COST,
            "argon2_memory_kib": ARGON2_MEMORY_KIB,
            "ga_generations": GA_GENERATIONS,
            "ca_rule": 110,
            "ca_steps": CA_STEPS,
            "time_sec": round(elapsed, 3),
        },
    }
