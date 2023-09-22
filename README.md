<br/>
<p align="center">
  <a href="https://github.com/ChrisBuilds/terminaltexteffects">
    <img src="https://github.com/ChrisBuilds/terminaltexteffects/assets/57874186/66388e57-e95e-4619-b804-1d8d7ebd124f" alt="TTE" width="80" height="80">
  </a>

  <h3 align="center">Terminal Text Effects</h3>

  <p align="center">
    Inline Visual Effects in the Terminal
    <br/>
    <br/>
  </p>
</p>

[![PyPI - Version](https://img.shields.io/pypi/v/terminaltexteffects?style=flat&color=green)](http://https://pypi.org/project/terminaltexteffects/ "![PyPI - Version](https://img.shields.io/pypi/v/terminaltexteffects?style=flat&color=green)")  ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/terminaltexteffects) ![License](https://img.shields.io/github/license/ChrisBuilds/terminaltexteffects) 

## Table Of Contents

* [About](#tte)
* [Requirements](#requirements)
* [Installation](#installation)
* [Usage](#usage)
* [Options](#options)
* [Examples](#examples)
* [License](#license)


## TTE

![tte_terminal_header_optimized](https://github.com/ChrisBuilds/terminaltexteffects/assets/57874186/64600218-bdc3-4162-a522-77ca86d901b8)


TerminalTextEffects is a collection of visual effects that run inline in the terminal. The underlying visual effect framework supports the following:
- XTerm 256 Color
- RGB Hex Triplet Color
- Color Gradients
- Character Motion (Waypoints, Speed, Acceleration)
- UTF8 Character Set

## Requirements

TerminalTextEffects is written in Python and does not require any 3rd party modules. Terminal interactions use standard ANSI terminal sequences and should work in most modern terminals. 

## Installation


```pip install terminaltexteffects```

## Usage
```cat your_text | tte <effect> [options]```

OR

``` cat your_text | python -m terminaltexteffects <effect> [options]```

* All effects support adjustable animation speed using the ```-a``` option.
* Use ```<effect> -h``` to view options for a specific effect, such as color or movement direction.
  * Ex: ```tte decrypt -h```

## Options
```
options:
  -h, --help            show this help message and exit
  --xterm-colors        Convert any colors specified in RBG hex to the closest XTerm-256 color.

Effect:
  Name of the effect to apply. Use <effect> -h for effect specific help.

  {burn,columnslide,decrypt,expand,pour,rain,randomsequence,rowmerge,rowslide,scattered,shootingstar,spray,verticalslice}
                        Available Effects
    burn                Burns vertically in the output area.
    columnslide         Slides each column into place.
    decrypt             Display a movie style decryption effect.
    expand              Expands the text from a single point.
    pour                Pours the characters into position from the given direction.
    rain                Rain characters from the top of the output area.
    randomsequence      Prints the input data in a random sequence.
    rowmerge            Merges rows of characters.
    rowslide            Slides each row into place.
    scattered           Move the characters into place from random starting locations.
    shootingstar        Displays the text as a falling star toward the final coordinate of the character.
    spray               Draws the characters spawning at varying rates from a single point.
    verticalslice       Slices the input in half vertically and slides it into place from opposite directions.
```


## Examples
#### Fireworks
![fireworks_demo](https://github.com/ChrisBuilds/terminaltexteffects/assets/57874186/af5929b0-43e4-4ebd-80ec-32fd0deec7f8)

#### RAIN
![rain_demo](https://github.com/ChrisBuilds/terminaltexteffects/assets/57874186/ed94a21f-503d-46f3-8510-7a1e83b28314)

#### DECRYPT
![decrypt_demo](https://github.com/ChrisBuilds/terminaltexteffects/assets/57874186/586224f3-6a03-40ae-bdcf-067a6c96cbb5)

#### BURN
![burn_example](https://github.com/ChrisBuilds/terminaltexteffects/assets/57874186/8f0e96bc-5f09-419b-9d91-6edeb50d63c1)

#### ROWSLIDE
![rowslide_example](https://github.com/ChrisBuilds/terminaltexteffects/assets/57874186/ccac83da-743c-4936-93f4-ced68fefaa51)

#### EXPAND
![expand_example](https://github.com/ChrisBuilds/terminaltexteffects/assets/57874186/2753a76f-49a1-48b0-9c0d-aaa0b8ab1a3d)

## License

Distributed under the MIT License. See [LICENSE](https://github.com/ChrisBuilds/terminaltexteffects/blob/main/LICENSE.md) for more information.
