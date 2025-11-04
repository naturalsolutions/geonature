-- 04a_alter_types_with_srid.sql

ALTER TABLE ref_geo.l_linears
  ALTER COLUMN geom
    TYPE Geometry(Geometry, :new_srid)
    USING ST_Transform(geom, :new_srid);

ALTER TABLE ref_geo.l_points
  ALTER COLUMN geom
    TYPE Geometry(Geometry, :new_srid)
    USING ST_Transform(geom, :new_srid);

ALTER TABLE ref_geo.l_areas
  ALTER COLUMN geom
    TYPE Geometry(MultiPolygon, :new_srid)
    USING ST_Transform(geom, :new_srid);

ALTER TABLE ref_geo.l_areas
  ALTER COLUMN centroid
    TYPE Geometry(Point, :new_srid)
    USING ST_Transform(centroid, :new_srid);

ALTER TABLE gn_synthese.synthese
  ALTER COLUMN the_geom_local
    TYPE Geometry(Geometry, :new_srid)
    USING ST_Transform(the_geom_local, :new_srid);


-- Monitoring.t_base_sites.geom_local
ALTER TABLE gn_monitoring.t_base_sites
  ALTER COLUMN geom_local
    TYPE Geometry(Geometry, :new_srid)
    USING ST_Transform(geom_local, :new_srid);

-- Monitoring.t_sites_groups.geom_local
ALTER TABLE gn_monitoring.t_sites_groups 
  ALTER COLUMN geom_local 
    TYPE Geometry(Geometry, :new_srid)
    USING ST_Transform(geom_local, :new_srid);

-- dem_vector
ALTER TABLE ref_geo.dem_vector
  ALTER COLUMN geom
    TYPE Geometry(Geometry, :new_srid)
    USING ST_Transform(geom, :new_srid);

-- pr_occhab.t_stations.geom_local
ALTER TABLE pr_occhab.t_stations
  ALTER COLUMN geom_local
    TYPE Geometry(Geometry, :new_srid)
    USING ST_Transform(geom_local, :new_srid);


-- pr_occtax.t_releves_occtax.geom_local
ALTER TABLE pr_occtax.t_releves_occtax
  ALTER COLUMN geom_local
    TYPE Geometry(Geometry, :new_srid)
    USING ST_Transform(geom_local, :new_srid);

