import tiktoken
import utils


def compare_encodings(example_string: str) -> None:
    """Prints a comparison of string encodings."""

    # encoding_names = ["gpt2", "p50k_base", "cl100k_base"]
    encoding_names = ["gpt2"]
    for encoding_name in encoding_names:
        encoding = tiktoken.get_encoding(encoding_name)
        token_integers = encoding.encode(example_string)
        num_tokens = len(token_integers)
        print(f"{encoding_name}: {num_tokens} tokens")

        # token_bytes = [
        #     encoding.decode_single_token_bytes(token) for token in token_integers
        # ]
        # print(f"token integers: {token_integers}")
        # print(f"token bytes: {token_bytes}")


if __name__ == "__main__":
    cfg = utils.load_config()
    wiki_dump_text_path = cfg["wiki-dump-text-path"]
    with open(wiki_dump_text_path, encoding="utf-8") as file:
        full_text = "".join(file.readlines())

    compare_encodings(full_text)
