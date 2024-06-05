import os
import zipfile


def _extract_zip(archive_path, extract_dir):
    if not os.path.exists(archive_path):
        return
    try:
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            zipf.extractall(extract_dir)
    except Exception as e:
        raise e from None


def main():
    archives = [{
        'path': os.path.join(os.path.dirname(__file__), 'archives/src-json.zip'),
        'extract_to': os.path.join(os.path.dirname(__file__), 'geojson2mongo/json_data')
    }, {
        'path': os.path.join(os.path.dirname(__file__), 'archives/rwanda2015-json.zip'),
        'extract_to': os.path.join(os.path.dirname(__file__), 'geojson2mongo/json_data')
    }]
    for archive in archives:
        _extract_zip(archive['path'], archive['extract_to'])


if __name__ == '__main__':
    main()