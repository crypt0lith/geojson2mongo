import os
import rarfile


def extract_rar(archive_path):
    if not os.path.exists(archive_path):
        return
    extract_dir = os.path.dirname(archive_path)
    with rarfile.RarFile(archive_path) as rf:
        rf.extractall(extract_dir)


def main():
    archives = [os.path.join(os.path.dirname(__file__), 'geojson2mongo', 'src_json.rar'),
                os.path.join(os.path.dirname(__file__), 'json', 'rwanda-2015-geojson.rar')]
    for archive in archives:
        extract_rar(archive)


if __name__ == "__main__":
    main()
