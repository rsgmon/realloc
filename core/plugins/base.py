class ExportPlugin:
    def export(self, trades: dict, output_path: str) -> None:
        raise NotImplementedError("Plugin must implement `export` method.")
