# County Election Mapper
 Turns a spreadsheet into an SVG county election map using Python 3. The example is the 1968 Presidential election with Humphrey's and Nixon's votes combined. This has not been tested on Linux or Max. Please report any issues, thank you! You're not required to credit me if you use this, but it's definitely appreciated! You can either link to this repo or tag @AmeliaMakesMaps on Twitter.

# How to Use

## Set Up Your Input File
 You can either edit the default `input.csv` file (recommended) or create your own, but it must meet these criteria to function properly:
 1. Saved as a CSV file
 2. In the same directory as `mapper.py`
 3. Must conform to the same format


 The input file has four sections (denoted in all caps):
 1. SETTINGS
 2. COLORS
 3. CANDIDATES
 4. COUNTIES


### Warning
 Do NOT use commas anywhere in the input file! This will cause the program to read it improperly.

### Settings
 The first column is the setting name and the second column is the value. Here's a list of settings you can change:

 | Setting | Purpose | Note |
 |---------|---------|------|
 | Filename | The name of the output file without `.svg` | Defaults to `output` if not provided or left empty |
 | Vote type | Indicate if you're providing raw votes or percentage values | Mandatory, only accepts `Raw` or `Percent` |
 | Color type | Are the colors for margins or percentage values? | Optional, can be `Margin` (default) or `Percent` |
 | Isolate | Only show counties in these states. Provide 2-letter, capital abbreviations and separate with spaces | Optional, will show every state by default
 | Borders | Show state borders? | Optional, can be `TRUE` (default) or `FALSE` |
 | Separator | Show the AK/HI separator? | Optional, can be `TRUE` (default) or `FALSE` |

### Colors
 The first column is the color name, the second column is the numeric value (margin or percent depending on the value of `Color type`), and the third column is the hex code. To find which color to use, the program will floor the value. Use 0 for <+1/<10%. Ties use stripes, the colors of which are either the percentage of each candidate or the middle color (+20 in the example), according to the value of `Color type`.

### Candidates
 The first column is the candidate's name and the second column is the candidate's color, which must match one of the colors in the `COLORS` section. You must have at least one candidate.

### Counties
 This section contains a list of every county in the United States. The first column is the county's name, the second column is the state, and after that, there's one column for every candidate (in the order defined in the `CANDIDATES` section). You don't have to label each candidate's column, but it's recommended for readability.

 If you're using raw votes, you must add a column at the end titled `TOTAL` with the total number of votes in each county. You can change the order of the counties, but do *not* modify the name or state.

 If a county has no votes, you can write `NV` in the first candidate's column and it will be colored light gray. If data is not available, or there's another issue, write `NA` and it will be colored dark gray. If nothing is provided, the county will be skipped and remain black.

## Run the Mapper (Windows)
 First, open a command prompt window and `cd` into the directory where `mapper.py` is located. Next, run `python mapper.py`. If your input file is not `input.csv`, provide the filename as `-i=filename.csv`. If there's no errors, it'll create a new SVG file for you!
