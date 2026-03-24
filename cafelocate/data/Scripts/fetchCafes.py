import os
import time
import pandas as pd

try:
    import googlemaps
except ImportError:
    googlemaps = None

# 1. Setup your API Key (replace with your own key)
API_KEY = 'AIzaSyBF6AjU5MsF11ygUVf65rfHWjzlmRKHRPw'

# 2. Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
input_csv = os.path.join(script_dir, '..', 'raw_data', 'kathmandu_cafes.csv')
output_csv = os.path.join(script_dir, '..', 'raw_data', 'kathmandu_cafes_updated.csv')

print(f"Input CSV: {input_csv}")
print(f"Output CSV: {output_csv}")

# 3. Read CSV
if not os.path.isfile(input_csv):
    raise FileNotFoundError(f"Input file not found: {input_csv}")

df = pd.read_csv(input_csv)

if googlemaps is None:
    print("WARNING: googlemaps package is not installed, skipping API lookups and writing nulls.")
    df['rating'] = None
    df['review_count'] = None
    df['price_level'] = None
    df.to_csv(output_csv, index=False)
    print("Saved output CSV with null metric columns.")
    raise SystemExit(0)

# 4. Initialize client
gmaps = googlemaps.Client(key=API_KEY)

# 5. Fetch function

def get_place_details(row):
    try:
        query = f"{row.get('name','')} Kathmandu"
        location = None
        if 'lat' in row and 'lng' in row and not pd.isna(row['lat']) and not pd.isna(row['lng']):
            location = (float(row['lat']), float(row['lng']))

        places_result = gmaps.places(query=query, location=location, radius=500)

        if places_result.get('status') == 'OK' and places_result.get('results'):
            place_id = places_result['results'][0].get('place_id')
            if place_id:
                details = gmaps.place(place_id=place_id, fields=['rating', 'user_ratings_total', 'price_level'])
                res = details.get('result', {})
                return pd.Series({
                    'rating': res.get('rating'),
                    'review_count': res.get('user_ratings_total'),
                    'price_level': res.get('price_level')
                })

    except Exception as e:
        print(f"Error fetching details for {row.get('name','<unknown>')}: {e}")

    return pd.Series({'rating': None, 'review_count': None, 'price_level': None})

# 6. Batch processing to respect rate limit
batch_size = 50
print(f"Total cafes: {len(df)}")

update_rows = []
for idx, row in df.iterrows():
    if idx > 0 and idx % batch_size == 0:
        print(f"Processed {idx} cafes, sleeping 240 seconds to respect rate limit...")
        time.sleep(240)

    result = get_place_details(row)
    df.at[idx, 'rating'] = result['rating']
    df.at[idx, 'review_count'] = result['review_count']
    df.at[idx, 'price_level'] = result['price_level']

    print(f"{idx+1}/{len(df)}: {row.get('name','<unknown>')} -> {result.to_dict()}")

# 7. Save output CSV
print(f"Saving to {output_csv}")
df.to_csv(output_csv, index=False)
print("Done")