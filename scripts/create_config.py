import shutil
from pathlib import Path

if __name__ == "__main__":
    config_example = Path("config.example.yaml")
    config = Path("config.yaml")
    
    if not config.exists() and config_example.exists():
        shutil.copy(config_example, config)
        print(f"created {config} from {config_example}")
    else:
        print(f"{config} already exists or {config_example} not found")
