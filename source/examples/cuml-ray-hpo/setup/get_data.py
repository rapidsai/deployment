import argparse
import os
from urllib.request import urlretrieve

# If script is in setup/, use parent directory; otherwise use script directory or cwd
_script_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(_script_dir) == "setup":
    # Script is in setup/ directory, use parent directory
    _data_dir = os.path.join(os.path.dirname(_script_dir), "data")
else:
    # Script is not in expected location, use current working directory
    _data_dir = os.path.join(os.getcwd(), "data")


def prepare_dataset(use_full_dataset=False):
    """
    Download the airline dataset.

    Parameters
    ----------
    use_full_dataset : bool, default=False
        If True, downloads the full dataset (20M rows).
        If False, downloads the small dataset.
    """
    data_dir = _data_dir

    # Set filename based on dataset size
    if use_full_dataset:
        file_name = "airlines.parquet"
        url = "https://data.rapids.ai/cloud-ml/airline_20000000.parquet"
    else:
        file_name = "airlines_small.parquet"
        url = "https://data.rapids.ai/cloud-ml/airline_small.parquet"

    parquet_name = os.path.join(data_dir, file_name)

    if os.path.isfile(parquet_name):
        print(f" > File already exists. Ready to load at {parquet_name}")
    else:
        # Ensure folder exists
        os.makedirs(data_dir, exist_ok=True)

        def data_progress_hook(block_number, read_size, total_filesize):
            if (block_number % 1000) == 0:
                print(
                    f" > percent complete: { 100 * ( block_number * read_size ) / total_filesize:.2f}\r",
                    end="",
                )
            return

        urlretrieve(
            url=url,
            filename=parquet_name,
            reporthook=data_progress_hook,
        )

        print(f" > Download complete {file_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download airline dataset for cuML Ray HPO example"
    )
    parser.add_argument(
        "--full-dataset",
        action="store_true",
        help="Download the full dataset (20M rows) instead of the small dataset",
    )
    args = parser.parse_args()

    prepare_dataset(use_full_dataset=args.full_dataset)
