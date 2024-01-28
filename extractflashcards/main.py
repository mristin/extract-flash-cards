"""
Extract flash cards from a text using ChatGPT.

The text is assumed to be already split in sentences by newlines, so every line is
considered a phrase or a sentence in itself.
"""

import argparse
import csv
import io
import pathlib
import sys
from typing import List, Tuple, Optional, Set

import openai
from icontract import require, ensure


# fmt: off
@require(lambda max_batch_length: max_batch_length > 0)
@ensure(lambda result: (result[0] is not None) ^ (result[1] is not None))
@ensure(
    lambda text, result:
    not (result[0] is not None)
    or "".join(result[0]) == text
)
@ensure(
    lambda text, max_batch_length, result:
    not (result[0] is not None)
    or all(
        len(part) <= max_batch_length
        for part in result[0]
    )
)
# fmt: on
def split_text_into_batches(
    text: str, max_batch_length: int = 3000
) -> Tuple[Optional[List[str]], Optional[str]]:
    """
    Split the text into batches so that they can be fed into ChatGPT context.

    Return batches, or an error, if any.

    >>> split_text_into_batches('hello\\nworld\\nearly\\nin the\\nmorning', 12)
    (['hello\\nworld\\n', 'early\\n', 'in the\\n', 'morning'], None)
    """
    result = []  # type: List[str]

    batch_parts = []  # type: List[str]
    current_len = 0

    for i, line in enumerate(text.splitlines(keepends=True)):
        if len(line) > max_batch_length:
            return None, (
                f"The line {i + 1} is too long "
                f"(got {len(line)}, max. is {max_batch_length})."
            )

        if current_len + len(line) > max_batch_length:
            result.append("".join(batch_parts))
            batch_parts = []
            current_len = 0

        batch_parts.append(line)
        current_len += len(line)

    if len(batch_parts) > 0:
        result.append("".join(batch_parts))

    return result, None


def main(prog: str) -> int:
    """
    Execute the main routine.

    :param prog: name of the program to be displayed in the help
    :return: exit code
    """
    parser = argparse.ArgumentParser(prog=prog, description=__doc__)
    parser.add_argument(
        "--source_language", help="source language of the text", default="Russian"
    )
    parser.add_argument(
        "--target_language",
        help="target language which we already master",
        default="English",
    )
    parser.add_argument(
        "--text",
        help="Text that we want to extract the flash cards from",
    )
    parser.add_argument(
        "--text_path",
        help=(
            "Path to the text file that we want to extract the flash cards from. "
            "Either --text or --text_path needs to be specified, but not both."
        ),
    )
    parser.add_argument(
        "--openai_key_path",
        help="Path to the text file containing the OpenAI key",
        default="openai-key.txt",
    )

    args = parser.parse_args()

    source_language = str(args.source_language)
    target_language = str(args.target_language)
    text = args.text if args.text is not None else None
    text_path = pathlib.Path(args.text_path) if args.text_path is not None else None
    openai_key_path = pathlib.Path(args.openai_key_path)

    if text is not None and text_path is not None:
        print(
            "Both --text and --text_path has been specified. You must specify only "
            "either one of them.",
            file=sys.stderr,
        )
        return 1

    if text is None and text_path is None:
        print("Neither --text nor --text_path has been specified.", file=sys.stderr)
        return 1

    if text_path is not None:
        text_source = f"--text_path {text_path}"
        text = text_path.read_text(encoding="utf-8")
    else:
        text_source = "--text"

    assert text is not None

    if not openai_key_path.exists():
        print(f"--openai_key_path does not exist: {openai_key_path}", file=sys.stderr)
        return 1

    if not openai_key_path.is_file():
        print(f"--openai_key_path is not a file: {openai_key_path}", file=sys.stderr)
        return 1

    try:
        openai_key = openai_key_path.read_text(encoding="utf-8").strip()
    except Exception as exception:
        print(f"Failed to read {openai_key_path}: {exception}", file=sys.stderr)
        return 1

    openai.api_key = openai_key
    model = "gpt-4-turbo-preview"

    batches, error = split_text_into_batches(text=text, max_batch_length=500)
    if error is not None:
        print(
            f"{text_source} could not be split into batches "
            f"for ChatGPT prompts: {error}",
            file=sys.stderr,
        )
        return 1

    assert batches is not None

    writer = csv.writer(sys.stdout)
    writer.writerow(
        [
            source_language,
            target_language,
            f"Phrase in {source_language}",
            f"Phrase in {target_language}",
        ]
    )

    observed_set = set()  # type: Set[str]

    for batch in batches:
        for prompt in [
            (
                f"""\
Please extract from the following text lines in {source_language} all the verbs.
Write them in a four column CSV:
one column for the {source_language} verbs in infinitive present tense,
one column for the translation in {target_language},
one column with the line content where the word appears in,
and one column with the translation of the line in {target_language}.

Do not forget to escape the commas with double-quotes as the output is a CSV.

Make sure that the verb really appears in the line in the third column!
Make sure the verb in the first column in {source_language} is indeed given in present tense!

Do not output the CSV header!

Output only valid CSV, no text before or after!

Here are the text lines:
{batch}"""
            ),
            (
                f"""\
Please extract from the following text lines in {source_language} all the nouns.
Write them in a four column CSV:
one column for the {source_language} noun in nominative singular (not plural!),
one column for the translation in {target_language},
one column with the line content where the word appears in,
and one column with the translation of the line in {target_language}.

Do not forget to escape the commas with double-quotes as the output is a CSV.

Make sure that the noun really appears in the line in the third column!
Make sure the noun in the first column in {source_language} is indeed given in nominative singular!
The noun in the first column in {source_language} must NOT be given in nominative plural!

Do not output the CSV header!

Output only valid CSV, no text before or after!

Here are the text lines:
{batch}"""
            ),
            # pylint: disable=line-too-long
            (
                f"""\
Please extract from the following text lines in {source_language} all the adjectives in {source_language}.
Do not output any adverbs, only adjectives!

Write them in a four column CSV:
one column for the {source_language} adjective transformed in nominative singular masculine (not plural! masculine! nominative!),
one column for the translation in {target_language},
one column with the line content where the word appears in,
and one column with the translation of the line in {target_language}.

Do not forget to escape the commas with double-quotes as the output is a CSV.

Make sure that the adjective really appears in the line in the third column!
Transform the adjective in the first column in {source_language} to nominative singular masculine (masculine! nominative! not plural)!
The adjective in the first column must be in masculine!
The adjective in the first column must NOT be in plural!
The adjective in the first column must NOT be in any other case than nominative!

Adjective, not adverb!

Do not output the CSV header!

Output only valid CSV, no text before or after!

Here are the text lines:
{batch}"""
            ),
            (
                f"""\
Please extract from the following text lines in {source_language} all the adverbs in {source_language}.
Write them in a four column CSV:
one column for the {source_language} adverb,
one column for the translation in {target_language},
one column with the line content where the word appears in,
and one column with the translation of the line in {target_language}.

Do not forget to escape the commas with double-quotes as the output is a CSV.

Make sure that the adverb really appears in the line in the third column!

Make sure that the first column is really an adverb and not an adjective!

Do not output the CSV header!

Output only valid CSV, no text before or after!

Here are the text lines:
{batch}"""
            ),
            # pylint: enable=line-too-long
        ]:
            try:
                completion = openai.ChatCompletion.create(  # type: ignore
                    model=model, messages=[{"role": "user", "content": prompt}]
                )
            except openai.error.AuthenticationError as exception:
                print(
                    f"Failed to authenticate with OpenAI: {exception}", file=sys.stderr
                )
                return 1

            answer = completion.choices[0].message.content
            reader = csv.reader(io.StringIO(answer))
            for row in reader:
                word = row[0]

                if word in observed_set:
                    continue

                observed_set.add(word)

                writer.writerow(row)

    print()
    return 0


def entry_point() -> int:
    """Provide an entry point for a console script."""
    return main(prog="extract-flash-cards")


if __name__ == "__main__":
    sys.exit(main(prog="extract-flash-cards"))
