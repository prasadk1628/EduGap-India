import pandas as pd
import requests

df = pd.read_csv("education_analysis_ready.csv")

r = requests.get("https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson")
geojson = r.json()

geo_states = set(f["properties"]["ST_NM"] for f in geojson["features"])
csv_states = set(df["India/State/UT"].unique())

print("=== GeoJSON state names ===")
for s in sorted(geo_states):
    print(f'  "{s}"')

print("\n=== NOT MATCHING (need mapping) ===")
for s in sorted(csv_states):
    if s not in geo_states:
        print(f'  "{s}"')
