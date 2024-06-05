from .loader import main

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Load GeoJSON data to MongoDB')
    parser.add_argument('--env', type=str, default='.env', help='Path to the .env file')
    args = parser.parse_args()
    main(args.env)
