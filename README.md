# REDCap Testing

This program performs various non-destructive tests against a REDCap system to ensure that is working correctly before a new version is installed.  The tests work in 2 ways:

1. Ensures that common functions of REDCap work without causing an error.
1. Outputs data scraped from REDCap to text files so that outputs of different versions can be compared using diff.

## Setup

## Installation

1. Checkout the code from the repository.
1. `cd` into the project directory
1. Create and activate a virtual environment by running the code:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
1. Install dependencies using the command:
    ```bash
    pip install -r requirements.txt
    ```

### Requirements

#### REDCap Installations

This application tests a separately install version of REDCap.  Therefore, you will have to be able to install REDCap of however many different versions of REDCap you want to test.

Although the tests this tool runs should be non-destructive, that is not guaranteed.  Therefore, do not run these tool against a live instance of REDCap.

Also, it can be helpful to take a backup of each version of REDCap prior to running the tool.  As you will see below, the tool often requires small tweaks to be able to run against different version and produce a comparable out, so it it is often necessary re-run many times.

#### Selenium

This application uses Selenium to interact with the REDCap instances and scrape their data.  You will therefore need Selenium Grid to be installed separately.

### Configuration

This application is configured by copying the file `example.env` to `.env` and setting appropriate values.  Advice on what values to set are described in the example.env file.

## Running

Run the tool using the command:
```bash
python run_non_destructive_tests.py
```

This takes a while to run and sometime fails because of Selenium problems.  However, the tool can be restarted and it will pick up from where it left off.

The expected use case is to run the tool against two versions of REDCap and checking that a comparison of the outputs are reasonable.

## Output

Values extracted from the tested REDCap are stored in the output directory in a subdirectory named after the REDCap version number in the configuration.

The data is stored in JSON line files to facilitate comparison with `diff` or other text comparison tool.

The output of amended to more closely match previous versions using the 'COMPARE_VERSION' configuration setting.

## Testing a new Version

Testing a new version of REDCap requires the tool to be run several times.  It is probable that changes will have to made to the code to accommodate changes made to REDCap.  Such as:

1. The navigation and inspection codce no longer works with the new version of the REDCap
1. The values outputted no longer match values outputted from previous versions

Therefore, start testing using a `SAMPLING_TYPE` of `first`, because it's quicker, and then increase the sampling for a more thorough test.
