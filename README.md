# FileTranslator

FileTranslator is **totally free** pure-python package for translating files of unlimited
size to different languages. It will be useful if you really want to read a book
in a foreign language unfamiliar to you, but you could not find its translation
into your native language (chances are this will be the case with recent
literature).
It is also suitable for translating articles and scientific papers
to help you understand the material faster.

[//]: # (######################################################################)

## Usage

To use the capabilities of the package, the user is provided with a script
`translate_file`.

It is accessible inside venv, so firstly you need to activate it
(for more information, see section [Installation](#installation)).
Move to the root directory of the project and write:
```bash
source venv/bin/activate
```

Next you just need to run script with required options. Full syntax and
possible options are listed [below](#translatefile).
Let's consider small example.
Suppose you are in the project root and want to translate file `book.pdf`,
which resides in folder `files` relative to your location (this folder has
already been created in the repository, so you can just copy your file to it
and use the following command).
Command to translate this file from english to russian:
```bash
translate_file -s files/book.pdf -c en -d ru 
```
By default, translated file will be created in the same folder as *source file*
(in previous example it is `files`).

**NOTE**: After translation finished don't forget to exit venv with command
`deactivate`.

### File formats
* pdf

### Languages
Script accepts languages code in format `ISO 639-1` as arguments.

| Language | ISO 639-1 | ISO 639-2 |
|:--------:|:---------:|:---------:|
| English  |    en     |    eng    |
| Russian  |    ru     |    rus    |
|  Polish  |    pl     |    pol    |
|  French  |    fr     |    fra    |
|  German  |    de     |    deu    |
| Chinese  |    zh     |    zho    |
| Spanish  |    es     |    spa    |
| Japanese |    ja     |    jpn    |

**NOTE**: For all of these languages except for *English* you need to manually
install some language packages for text recognition. Pattern for this package:
```bash
sudo apt-get install tesseract-ocr-<LANG_CODE>
```
where `LANG_CODE` is code of language in `ISO 639-2` (or `alpha-3`) format.
You can find codes [here](https://en.wikipedia.org/wiki/List_of_ISO_639-2_codes).
For instance, to be able to translate from *Russian* to *English*,
all we have to do is:
```bash
sudo apt-get install tesseract-ocr-rus
```

[//]: # (######################################################################)

## Command Line Script

### Syntax:
```
translate_file [-h] -s SOURCE_PATH [-e EXTENSION] -c CURRENT_LANGUAGE
                      -d DESIRED_LANGUAGE [-f FIRST] [-l LAST] [--font FONT]
                      [-m SAVE_CONTEXT] [-t TARGET_PATH]
```

### Options:
|       Option       | Short form | Required |                       Default                        | Description                                                                       |
|:------------------:|:----------:|:--------:|:----------------------------------------------------:|:----------------------------------------------------------------------------------|
|   --source-path    |     -s     |   yes    |                          -                           | Absolute or relative path to file that needs translation (`source file`).         |
|   --target-path    |     -t     |    no    | PATH/TO/SRC/<source_name>.<desired_lang>.<extension> | Absolute of relative path to translated file (`target file`).                     |
|    --extension     |     -e     |    no    |          <deduced from the source filename>          | Extension of `source file`.                                                       |
| --current-language |     -c     |   yes    |                          -                           | Language of source file.                                                          |
| --desired-language |     -d     |   yes    |                          -                           | Language of translated file.                                                      |
|      --first       |     -f     |    no    |                          1                           | Page number from which the translation begins.                                    |
|       --last       |     -l     |    no    |                  <number of pages>                   | Page number where the translation ends.                                           |
|       --font       |     -g     |    no    |                      arial.ttf                       | Name of font file[^1].                                                            |
|   --save-context   |     -m     |    no    |                         True                         | Script will try to save context in case of splitting sentence to different pages. |

[^1] You are able to use your own font. Just place file with font to
*PATH/TO/REPO/src/FileTranslator/data/fonts/* and specify name of file with font
in script options.

[//]: # (######################################################################)

## Examples

Translation of one page of *The Arabian Nights* from english to russian:

|                      before translation                      |                       after translation                        |
|:------------------------------------------------------------:|:--------------------------------------------------------------:|
| ![before translation](docs/data/TheArabianNightsEnPage.png)  | ![after translation](docs/data/TheArabianNightsEnPage.ru.png)  |

Some examples of translator work can be found [here](examples).

[//]: # (######################################################################)

## Installation

**Step 1**: It is better to use app in *isolated virtual environment (venv)*.
To set it up, you will need `virtualenv` tool.
It can be installed with:
```bash
sudo apt-get install virtualenv
```

**Step 2**: You have to manually install [ChromeDriver](https://chromedriver.chromium.org/getting-started).
You can find a lot of manuals in the internet how to do it for your system. 

**Step 3**: To install app, open terminal and follow steps below.

1) Clone repository and move to its root:
    ```bash
    git clone ... FileTranslator
    cd FileTranslator
    ```

2) Make virtual environment and activate it:
   ```bash
   virtualenv venv
   source venv/bin/activate
   ```

3) Install requirements and app:
   ```bash
   pip install -r requirements.txt
   pip install .
   ```

4) After installation deactivate environment by writing `deactivate` to the
console.
