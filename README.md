# MeMAD subtitle translation pipeline

This repository contains scripts that implement the subtitle translation pipeline developed as part of the [MeMAD project](https://memad.eu). The pipeline makes use of [subalign](https://github.com/Helsinki-NLP/subalign) and [OpusTools-perl](https://github.com/Helsinki-NLP/OpusTools-perl) for converting between subtitle and plain text formats, the [Moses](http://www.statmt.org/moses/) toolkit for pre- and post-processing, [SentencePiece](https://github.com/google/sentencepiece) for subword segmentation, and [Marian NMT](https://github.com/marian-nmt/marian) transformers trained as (1) restoration models, which substitute for normalizing punctuation and truecasing, and (2) translation models.

Pre-trained restoration, translation, and segmentation models for the pipeline are available for download from the [pipeline models](https://zenodo.org/record/4389209) repository on Zenodo. The translation models distributed from there are the default bilingual translation models. Multilingual translation models, other bilingual models fine-tuned on in-domain data, and further models that support guided alignment based on subword segments can all be found in the [supplementary models](https://zenodo.org/record/4556121) repository. These models collectively support Dutch, English, Finnish, French, German and Swedish, and allow subtitle translation between any two of these languages.

## Dependencies

* `perl >= 5.30`
* `python >= 3.0`
* [`marian >= 1.8.0`](https://github.com/marian-nmt/marian)
* Data processing scripts from [`moses`](https://github.com/moses-smt/mosesdecoder)
* Data processing scripts from [`OpusTools-perl`](https://github.com/Helsinki-NLP/OpusTools-perl)
  - Required Perl libraries listed in the repository
* Data processing scripts from [`subalign`](https://github.com/MeMAD-project/subalign)

To check for and install the required Python libraries, navigate to the directory where you cloned the repository, and run the following command:

```
pip install --user -r requirements.txt
```

## Models

* [MeMAD MT models](https://zenodo.org/record/4389209)
* [MeMAD Tatoeba and subtitle tuned models](https://zenodo.org/record/4556121)

## Usage

The pipeline requires segmentation models (`sentencepiece-models.tar.gz`), restoration models for the source language (`restore-xx.tar.gz`), and translation models from the source language to the target language (`xx-yy.tar.gz`). Download the desired pre-trained models from the [Zenodo](https://zenodo.org/record/4389209) repository, and extract the archives into the `models` folder.

Before you run the pipeline, make sure you edit the configuration file `paths.conf`, so that the variables point to the correct paths for your system.

The script `translate.py` runs the entire pipeline from source language subtitles to target language subtitles. Run `./translate.py --help` to read about supported options.

### Quickstart

##### Marian on CPU

```
./translate.py --src-lang de \
               --tgt-lang en \
               --input data/sample.de.srt \
               --output sample.en.srt \
               --cpu-threads 1 \
               --verbose \
               --log process.log \
               --strict-sentence-parsing
```

##### Marian on GPU

```
./translate.py --src-lang de \
               --tgt-lang en \
               --input data/sample.de.srt \
               --output sample.en.srt \
               --gpu-devices 4 \
               --verbose \
               --log process.log \
               --strict-sentence-parsing
```

##### Translating plain text data

If you need to circumvent the subtitle segmentation steps, and use the rest of the pipeline (restoration, translation, and other auxiliary processing) on plain text data, this is possible through the use of the `--plain-text-mode` option. Using this option requires an input file containing one sentence per line, rather than SRT-formatted subtitles. The output will be produced in the same format as the input.

```
./translate.py --src-lang de \
               --tgt-lang en \
               ...
               --plain-text-mode
```

When using the pipeline exclusively in this mode, the `OpusTools-perl` and `subalign` software dependencies are no longer required.

## Models

### Training and test data

The models provided for download have been trained on a snapshot of the entire [OPUS](http://opus.nlpl.eu/) collection from October 2020, except for a small portion of data held out as a test set. This test set was sampled from a multi-parallel selection of movie subtitles (~100k sentence pairs per language pair) from the [OpenSubtitles](https://www.opensubtitles.org/en) corpus.

### Translation model benchmarks

For reference, we provide some BLEU scores for the translation models in particular.

#### OpenSubtitles held-out test set

| src → tgt  | `→ de`  | `→ en`  | `→ fi`  | `→ fr`  | `→ nl`  | `→ sv`  |
|:----------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|
| **`de →`** |    —    |  25.60  |  16.07  |  19.20  |  21.20  |  19.20  |
| **`en →`** |  29.16  |    —    |  22.90  |  27.11  |  29.86  |  28.56  |
| **`fi →`** |  14.08  |  16.96  |    —    |  14.16  |  16.57  |  17.78  |
| **`fr →`** |  21.39  |  25.28  |  16.76  |    —    |  20.85  |  19.26  |
| **`nl →`** |  22.27  |  27.22  |  18.79  |  20.62  |    —    |  22.20  |
| **`sv →`** |  21.21  |  26.88  |  21.36  |  20.21  |  23.70  |    —    |

#### WMT news translation test sets

Test sets from WMT news translation tasks until 2019 were part of the training data for the pretrained translation models. We provide additional benchmarking results on the WMT 2020 news translation task test sets below.

##### WMT 2020

| src → tgt  | `→ de`  | `→ en`  | `→ fr`  |
|:----------:|:-------:|:-------:|:-------:|
| **`de →`** |    —    |  32.97  |  29.28  | 
| **`en →`** |  28.41  |    —    |    —    | 
| **`fr →`** |  24.31  |    —    |    —    | 


### Tatoeba-MT challenge models

[Additional models](https://zenodo.org/record/4556121) have been trained on the [Tatoeba-MT challenge datasets](https://github.com/Helsinki-NLP/Tatoeba-Challenge/). Those models cover the same six language pairs and have been benchmarked with MeMAD-internal test sets including translations between Finnish (FIN) and Swedish (SWE) subtitles from selected YLE TV programs with variants for the hearing impaired (indicated by the label FIH and SWH, espectively). We have also fine-tuned each model with disjoint training data from general movie subtitles (OpenSubtitles) and MeMAD-internal YLE data. The results are listed below:


| tune / test         | FIN-SWE   | FIH-SWE   | FIN-SWH   | SWE-FIN   | SWH-FIN   | SWE-FIH |
|:-------------------:|:---------:|:---------:|:---------:|:---------:|:---------:|:-------:|
| baseline            | 22.3      | 17.0      | 18.2      | 20.8      | 15.9      | 12.2 |
| OpenSubtitles (1M)  | 22.0      | 16.8      | 17.9      | 20.9      | 15.7      | 12.5 |
| YLE-all       (2M)  | 24.7      | 19.6      | 19.5      | 22.7      | 17.4      | 13.6 |
| YLE-FIN-SWE (1.1M)  | 24.9      | 18.9      | 19.5      | 23.1      | 17.3      | 13.9 |
| YLE-FIH-SWE (47k)   | 23.6      | 19.7      | 18.4      | 21.5      | 16.0      | 14.8 |
| YLE-FIN-SWH (850k)  | 23.8      | 18.5      | 19.5      | 23.0      | 17.7      | 13.9 |


## Publications

* [MT for Subtitling: Investigating professional translators’ user experience and feedback](https://researchportal.helsinki.fi/en/publications/mt-for-subtitling-investigating-professional-translators-user-exp)

```
@inproceedings{koponen-etal-2020-mt,
    title = "{MT} for Subtitling: Investigating professional translators{'} user experience and feedback",
    author = {Koponen, Maarit  and
      Sulubacak, Umut  and
      Vitikainen, Kaisa  and
      Tiedemann, J{\"o}rg},
    booktitle = "Proceedings of 1st Workshop on Post-Editing in Modern-Day Translation",
    month = oct,
    year = "2020",
    address = "Virtual",
    publisher = "Association for Machine Translation in the Americas",
    url = "https://www.aclweb.org/anthology/2020.amta-pemdt.6",
    pages = "79--92",
}
```

* [MT for subtitling: User evaluation of post-editing productivity](https://researchportal.helsinki.fi/en/publications/mt-for-subtitling-user-evaluation-of-post-editing-productivity)

```
@inproceedings{koponen-etal-2020-mt-subtitling,
    title = "{MT} for subtitling: User evaluation of post-editing productivity",
    author = {Koponen, Maarit  and
      Sulubacak, Umut  and
      Vitikainen, Kaisa  and
      Tiedemann, J{\"o}rg},
    booktitle = "Proceedings of the 22nd Annual Conference of the European Association for Machine Translation",
    month = nov,
    year = "2020",
    address = "Lisboa, Portugal",
    publisher = "European Association for Machine Translation",
    url = "https://www.aclweb.org/anthology/2020.eamt-1.13",
    pages = "115--124",
}
```
