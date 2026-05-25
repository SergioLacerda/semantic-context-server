class VectorStoreConfig:
    def __init__(
        self,
        rotation_size: int = 1024,
        max_entries_per_file: int = 1000,
        enable_rotation: bool = True,
    ):
        self.rotation_size = rotation_size
        self.max_entries_per_file = max_entries_per_file
        self.enable_rotation = enable_rotation
