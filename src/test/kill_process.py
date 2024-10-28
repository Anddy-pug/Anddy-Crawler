import requests

tika_url = "http://localhost:9998"

# Attempt to shut down the Tika server gracefully
try:
    response = requests.delete(f"{tika_url}/shutdown")
    if response.status_code == 200:
        print("Tika server shut down successfully.")
    else:
        print("Failed to shut down Tika server. Status code:", response.status_code)
except requests.exceptions.RequestException as e:
    print("Error while trying to shut down Tika server:", e)
