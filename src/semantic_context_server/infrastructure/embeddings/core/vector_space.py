class VectorSpace:
    def __init__(self, target_dim: int):
        self.target_dim = target_dim

    def normalize(self, vec: list[float]) -> list[float]:
        if len(vec) == self.target_dim:
            return vec

        if len(vec) > self.target_dim:
            return vec[: self.target_dim]

        return vec + [0.0] * (self.target_dim - len(vec))
