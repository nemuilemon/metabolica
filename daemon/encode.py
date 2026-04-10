"""ENCODE Phase - Convert metabolism output to DNA base4 sequences"""

import base64
import logging

from lib.dna_codec import dna_encode

log = logging.getLogger("metabolica.encode")


def encode_dna(metabolism: dict) -> dict:
    """Build the DNA gene record from metabolism output."""
    log.info("Encoding metabolism output to DNA sequences...")

    genes = {
        "sentiment": dna_encode(metabolism["stomach"]),
        "topic": dna_encode(metabolism["liver"]),
        "entropy": dna_encode(metabolism["heart"]),
        "evolution": dna_encode(metabolism["brain_final"]),
    }

    log.info("DNA gene lengths: %s",
             {k: len(v) for k, v in genes.items()})

    return {
        "genes": genes,
        "cellular_automata_state": base64.b64encode(metabolism["brain_history"]).decode("ascii"),
    }
