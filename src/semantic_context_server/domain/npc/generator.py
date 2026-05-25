# usecases/generate_npc.py

import random


class GenerateNPCUseCase:
    def execute(self, desc: str) -> dict:
        names = ["Arkan", "Velra", "Doran", "Selith"]
        traits = ["frio", "calculista", "irônico"]

        return {
            "name": random.choice(names),
            "description": desc,
            "trait": random.choice(traits),
        }
