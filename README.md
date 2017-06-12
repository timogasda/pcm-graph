# pcm-graph
Tool that plots graphs from the CSV output of Intel PCM (Processor Counter Monitor)

## Requirements
This script has been tested with Python 2.7, but should also work with Python 3.

The `matplotlib` library is required. Either install it with `pip install matplotlib` or use the `requirements.txt` file in this repository:

```
pip install -r requirements.txt
```

## Usage
You can generate CSV output with the Intel PCM tool like so:

```
sudo ./pcm.x -csv=results.csv -- ./my_benchmark
```

This CSV file can then be plotted with this tool like this:

```
./pcm_graph.py -o output.png results.csv
```

The file extension of the output file will determine the file type. So if you want to generate a PDF, simply use something like `output.pdf`.

Further command line arguments can be inquired with `./pcm_graph.py --help`:

```
usage: pcm_graph.py [-h] [-o OUTPUT] [-n NODES] [-p] [-q] [-s STYLE] [-t TITLE] input

positional arguments:
  input                 Path to the CSV file that contains the PCM results

optional arguments:
  -h, --help            show this help message and exit

  -o OUTPUT, --output OUTPUT
                        Path to output file. Defaults to %input%.png

  -n NODES, --nodes NODES
                        List of nodes to plot (e.g., 0,1,2,3)

  -p, --percentages     Use the percentage values for traffic instead of absolute values

  -q, --separate-qpi    Plot traffic for all QPI links separately

  -s STYLE, --style STYLE
                        Define a custom matplotlib style to use, see `matplotlib.style`

  -t TITLE, --title TITLE
                        Title of the figure
```

## Styling
If you would like to customize the style of the output plot, I would recommand using the `--style` parameter with a [matplotlib stylesheet](http://matplotlib.org/users/customizing.html).

For example, create a style sheet named `custom.mplstyle` with the following content:

```
figure.figsize : 10, 4
xtick.labelsize : 16
ytick.labelsize : 16
```

And this style sheet can then be invoked with `--style`:

```
./pcm_graph.py results.csv --style=custom.mplstyle
```
