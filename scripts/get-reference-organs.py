import requests

def fetch_reference_organs():
    url = 'https://apps.humanatlas.io/hra-api/v1/reference-organs'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        reference_organs = [item['label'] for item in data if 'label' in item]
        return reference_organs
    except requests.RequestException as e:
        return f"An error occurred while fetching data: {e}"

if __name__ == "__main__":
    reference_organs_list = fetch_reference_organs()
    print(reference_organs_list)