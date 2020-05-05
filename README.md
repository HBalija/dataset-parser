## KPI dataset parser

### Quickstart

Create Python 3 virtual environment.

Get the source from GitHub:

    git clone git@github.com:HBalija/dataset-parser.git

Navigate to project directory:

    cd dataset-parser

Install requirements:

    pip install -r requirements.txt

#### Command examples:

Run without passing kpi_list (all values are used):

    ./parser.py --start 2/2/15 --end 2/3/15

Run with providing kpi_list parameters:

    ./parser.py --start 2/2/15 --end 2/3/15 --kpi_list temperature co2
