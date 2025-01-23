import os
import duckdb
import requests
import json

def duckdb_connect(db_path):
    # To make this work with shinylive.io, we create the database from csv
    # if it does not exist, otherwise we are bloating the shinylive url with
    # a large binary object. Since there is no pyodide extension for httpfs, we 
    # download the csv using requests.
    con = duckdb.connect(db_path)
    url = "https://huggingface.co/datasets/WorkWithData/cities/raw/main/Cities.csv"
    table_exists = 'cities' in con.execute("SHOW TABLES").df().values
    if not table_exists:
        shinylive = (os.environ.get("USER") == "web_user")
        if shinylive:
            tempfile = "temp.csv"
            response = requests.get(url)
            with open(f"{tempfile}", 'w') as f:
                f.write(response.text)
            con.execute(f"CREATE TABLE cities AS SELECT * FROM READ_CSV('{tempfile}')")
            os.remove(tempfile)
        else: 
            con.execute(f"CREATE TABLE cities AS FROM '{url}'")
    return con

def get_search_result_db(search_query, con):
    sql_query = """
        WITH result_tbl AS (
            SELECT
                country,
                city,
                population,
                -- Create index for searching both city and country
                CONCAT(country, city) as search_index
            FROM cities
            WHERE search_index ILIKE '%' || replace(?, ' ', '%') || '%'
            ORDER BY population desc
            LIMIT 20
        )
        SELECT
            ARRAY_AGG(
              STRUCT_PACK(
                value := city,
                label := city,
                optgroup := null,
                country := country,
                population := population,
                search_index := search_index
              )
            ORDER BY population desc)::JSON as json
        FROM result_tbl
        """
    choices = con.execute(sql_query, [search_query]).df()["json"][0]
    # Do we have results?
    if choices:
        # JSONResponse expects a dict, look into avoiding JSON-roundtrip later
        choices_dict = json.loads(choices)
        # Insert empty first entry: https://github.com/posit-dev/py-shiny/issues/1074
        choices_dict.insert(0, {"value": None, "label": "", "optGroup": None})
        return choices_dict

