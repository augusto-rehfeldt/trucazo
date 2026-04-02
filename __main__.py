"""Entry point for Trucazo."""
import sys
import os

# Ensure the trucazo package directory is importable
sys.path.insert(0, os.path.dirname(__file__))

from game import main_menu

def main():
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n")
        sys.exit(0)

if __name__ == "__main__":
    main()