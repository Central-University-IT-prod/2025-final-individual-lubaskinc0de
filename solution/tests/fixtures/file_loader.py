from dataclasses import dataclass
from importlib.resources.abc import Traversable
from pathlib import Path


@dataclass(slots=True, frozen=True)
class ImportLibResourceLoader:
    resources_dir: Traversable

    def get_full_path(self, relative_path: Path) -> Path:
        traversable_path = self.resources_dir / str(relative_path)
        path = Path(str(traversable_path))

        if not path.exists():
            raise FileNotFoundError

        return path
