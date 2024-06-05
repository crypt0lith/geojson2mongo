import os
import zipfile


def extract_zip(archive_path, extract_dir):
    if not os.path.exists(archive_path):
        return
    try:
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            zipf.extractall(extract_dir)
    except Exception as e:
        raise e from None


def main():
    archives = [{
        "path": os.path.join(os.path.dirname(__file__), 'geojson2mongo/archives', 'src_json.zip'),
        "extract_to": os.path.join(os.path.dirname(__file__), 'geojson2mongo')
    }, {
        "path": os.path.join(os.path.dirname(__file__), 'geojson2mongo/archives', 'rwanda-2015-geojson.zip'),
        "extract_to": os.path.join(os.path.dirname(__file__), 'geojson2mongo/json_data')
    }]
    for archive in archives:
        extract_zip(archive["path"], archive["extract_to"])


if __name__ == "__main__":
    main()
