*******************
extract-flash-cards
*******************
Extract flash cards from a text using ChatGPT.

First extract the vocabulary from the text.

.. Help starts: python3 extractflashcards/main.py --help
.. code-block::

    usage: extract-flash-cards [-h] [--source_language SOURCE_LANGUAGE]
                               [--target_language TARGET_LANGUAGE] [--text TEXT]
                               [--text_path TEXT_PATH]
                               [--openai_key_path OPENAI_KEY_PATH]
                               [--output_path OUTPUT_PATH]

    Extract flash cards from a text using ChatGPT. The text is assumed to be
    already split in sentences by newlines, so every line is considered a phrase
    or a sentence in itself.

    options:
      -h, --help            show this help message and exit
      --source_language SOURCE_LANGUAGE
                            source language of the text
      --target_language TARGET_LANGUAGE
                            target language which we already master
      --text TEXT           Text that we want to extract the flash cards from
      --text_path TEXT_PATH
                            Path to the text file that we want to extract the
                            flash cards from. Either --text or --text_path needs
                            to be specified, but not both.
      --openai_key_path OPENAI_KEY_PATH
                            Path to the text file containing the OpenAI key
      --output_path OUTPUT_PATH
                            Path where to store the CSV. If not specified, output
                            to STDOUT

.. Help ends: python3 extractflashcards/main.py --help

Then convert the vocabulary into Anki flash cards.

.. Help starts: python3 extractflashcards/csv_to_anki.py --help
.. code-block::

    usage: csv-to-anki [-h] --csv_path CSV_PATH --anki_path ANKI_PATH --deck_name
                       DECK_NAME [--synthesize_audio SYNTHESIZE_AUDIO]

    Convert a CSV file to an anki deck.

    options:
      -h, --help            show this help message and exit
      --csv_path CSV_PATH   Path to the CSV file with the generated cards.
      --anki_path ANKI_PATH
                            Path to the file with the Anki deck
      --deck_name DECK_NAME
                            Name of the Anki deck
      --synthesize_audio SYNTHESIZE_AUDIO
                            Specify the language to synthesize source with Google
                            Text-to-speech. If not specified, the audio is not
                            synthesized

.. Help ends: python3 extractflashcards/csv_to_anki.py --help
