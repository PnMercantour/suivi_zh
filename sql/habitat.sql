with feature as (
    select 
        habitat.id id, 
        id_zh, 
        site.id id_site, 
        code habitat, 
        proportion
    from eau_zh.habitat 
        join eau_zh.zh on (habitat.id_zh = zh.id)
        join eau_zh.site using(nom_site))
select json_agg(row_to_json (feature.*)) from feature;
