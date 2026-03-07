import sys
import requests

def main():
    if len(sys.argv) < 2:
        print("Usage: python capture.py <text>")
        return

    text = " ".join(sys.argv[1:])
    url = "http://localhost:8000/capture"
    
    try:
        response = requests.post(url, json={"text": text, "source": "cli"})
        if response.status_code == 200:
            print(f"Captured: {text}")
        else:
            print(f"Error: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to capture service API. Is it running?")

if __name__ == '__main__':
    main()
