with raw_data as (
    select
        id_numero,
        id_nom,
        longitude,
        latitude,
        altitude,
        emission,
        installation,
        type_stati,
        lcz,
        ville,
        bati,
        veg_haute,
        geopoint
    from raw.station
)

select
    id_numero,
    id_nom,
    longitude,
    latitude,
    altitude,
    emission,
    to_date(installation, 'YYYY-MM-dd'),
    type_stati,
    lcz,
    ville,
    bati,
    veg_haute,
    geopoint
from raw_data
