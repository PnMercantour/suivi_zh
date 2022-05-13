with feature as (
    select 
        code habitat, 
        libelle
    from eau_zh.ref_habitat)
select json_agg(row_to_json (feature.*)) from feature;
