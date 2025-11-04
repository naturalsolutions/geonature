-- 04b_alter_types_no_srid.sql

ALTER TABLE gn_monitoring.t_base_sites 
  ALTER COLUMN geom_local 
    TYPE geometry(GEOMETRY, 0);

ALTER TABLE gn_monitoring.t_sites_groups 
  ALTER COLUMN geom_local 
    TYPE geometry(GEOMETRY, 0);

ALTER TABLE gn_synthese.synthese 
  ALTER COLUMN the_geom_local 
    TYPE geometry(GEOMETRY, 0);

ALTER TABLE pr_occhab.t_stations 
  ALTER COLUMN geom_local 
    TYPE geometry(GEOMETRY, 0);

ALTER TABLE pr_occtax.t_releves_occtax 
  ALTER COLUMN geom_local 
    TYPE geometry(GEOMETRY, 0);

ALTER TABLE ref_geo.dem_vector 
  ALTER COLUMN geom 
    TYPE geometry(GEOMETRY, 0);

ALTER TABLE ref_geo.l_areas 
  ALTER COLUMN centroid 
    TYPE geometry(POINT, 0);

ALTER TABLE ref_geo.l_areas 
  ALTER COLUMN geom 
    TYPE geometry(MULTIPOLYGON, 0);

ALTER TABLE ref_geo.l_linears 
  ALTER COLUMN geom 
    TYPE geometry(GEOMETRY, 0);

ALTER TABLE ref_geo.l_points 
  ALTER COLUMN geom 
    TYPE geometry(GEOMETRY, 0);


