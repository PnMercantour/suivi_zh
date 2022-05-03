with conv as (
select
	*
from
	(
values ('bon',
1.0),
('moyen',
0.5),
('mauvais',
0.25)) as t(etat_zh,
	coeff)),
total as (
select
	nom_site,
	sum(surface) surf
from
	eau_zh.zh
group by
	nom_site),
s as (
select
	nom_site,
	sum(surface * coeff) surf
from
	eau_zh.zh
join conv
		using(etat_zh)
group by
	nom_site)
select
	id id_site,
	total.surf surface,
	s.surf / total.surf ratio
from
	total
join s
		using(nom_site)
left join eau_zh.site using (nom_site)
order by
	ratio
