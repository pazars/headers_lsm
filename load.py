import pickle
from pathlib import Path


if __name__ == "__main__":
    # Check file created by main.py
    file_path = Path("./articles.pkl").resolve()
    with open(file_path, "rb") as file:
        loaded_data = pickle.load(file)

    print(len(loaded_data))
    print(loaded_data[0])
