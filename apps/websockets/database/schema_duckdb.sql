CREATE OR REPLACE MACRO GET_DATA(SELECTED_CODESPACE_ID) AS TABLE (
    WITH
    vehicles_tbl AS MATERIALIZED (
        WITH messages_unnested AS (
            SELECT
                insert_time,
                codespace_id,
                UNNEST(message -> '$.payload.data.vehicles[*]') message
            FROM db.entur_raw
        )

        SELECT
            insert_time,
            codespace_id,
            (message ->> '$.line.lineRef') as line_ref,
            (message ->> '$.line.lineName') as line_name,
            (message ->> '$.line.publicCode') as line_code,
            (message ->> '$.vehicleId') as vehicle_id,
            (message ->> '$.originName') as destination,
            (message ->> '$.destinationName') as origin,
            (message ->> '$.mode') as mode,
            (message ->> '$.lastUpdated')::TIMESTAMPTZ as last_updated,
            (message ->> '$.location.longitude')::DOUBLE as longitude,
            (message ->> '$.location.latitude')::DOUBLE as latitude
        FROM messages_unnested
        WHERE
            TRUE
            AND codespace_id = SELECTED_CODESPACE_ID
    ),

    vehicles_latest_tbl AS (
        SELECT *
        FROM vehicles_tbl
        QUALIFY ROW_NUMBER() OVER (PARTITION BY vehicle_id ORDER BY last_updated DESC) = 1
    ),

    -- Stats
    vehicles AS (
        SELECT
            JSON_GROUP_ARRAY(JSON(vehicles_latest_tbl)) as vehicles
        FROM vehicles_latest_tbl
    ),

    vehicles_per_second_tbl AS (
        SELECT
            DATE_TRUNC('second', insert_time) AS datetime,
            COUNT(*) AS n
        FROM vehicles_tbl
        GROUP BY datetime
        ORDER BY datetime DESC
    ),

    vehicles_per_second AS (
        SELECT
            JSON_GROUP_ARRAY(JSON(vehicles_per_second_tbl)) as vehicles_per_second
        FROM vehicles_per_second_tbl
    ),

    vehicles_last_second AS (
        SELECT
            DATE_TRUNC('second', insert_time) AS datetime,
            COUNT(*) AS vehicles_last_second
        FROM vehicles_tbl
        GROUP BY datetime
        ORDER BY datetime DESC
        LIMIT 1 OFFSET 1
    ),

    vehicles_total AS (
        SELECT
            COUNT(*) AS vehicles_total
        FROM vehicles_tbl
    ),

    messages_per_second_tbl AS (
        SELECT
            DATE_TRUNC('second', insert_time) AS datetime,
            COUNT(*) as n
        FROM db.entur_raw
        GROUP BY datetime
    ),

    messages_per_second AS (
        SELECT
            JSON_GROUP_ARRAY(JSON(messages_per_second_tbl)) as messages_per_second
        FROM messages_per_second_tbl
    ),

    messages_last_second AS (
        SELECT
            DATE_TRUNC('second', insert_time) AS datetime,
            COUNT(*) as messages_last_second
        FROM db.entur_raw
        GROUP BY insert_time
        ORDER BY insert_time
        LIMIT 1 OFFSET 1
    ),

    messages_total AS (
        SELECT
            COUNT(*) AS messages_total
        FROM db.entur_raw
    )

    SELECT
        vehicles,
        vehicles_last_second,
        vehicles_total,
        vehicles_per_second,
        messages_per_second,
        messages_last_second,
        messages_total
    FROM
        vehicles,
        vehicles_last_second,
        vehicles_total,
        vehicles_per_second,
        messages_per_second,
        messages_last_second,
        messages_total
)