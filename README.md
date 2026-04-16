Gifz Alfred Workflow
=====================

An [Alfred](https://www.alfredapp.com/) Workflow that searches my personal collection of gifs, hosted on Netlify at [gifz.netlify.app](https://gifz.netlify.app/).

## Install

Double-click `Gifz.alfredworkflow`.

## Usage

Type `gifz <query>` in Alfred. Press Enter to copy the selected gif's URL to your clipboard.

## Implementation

Single Python 3 script (`gifz.py`) using only the standard library — no `npm install`, no `pip install`. Runs against the system `/usr/bin/python3` that ships with macOS.
