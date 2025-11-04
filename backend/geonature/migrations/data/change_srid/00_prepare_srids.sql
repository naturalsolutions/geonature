-- 00_prepare_srids.sql
-- Passe tout en :old_srid avant re-projection
UPDATE ref_geo.l_linears
   SET geom = ST_SetSRID(geom, :old_srid)
 WHERE ST_SRID(geom) <> :old_srid;

UPDATE ref_geo.l_points
   SET geom = ST_SetSRID(geom, :old_srid)
 WHERE ST_SRID(geom) <> :old_srid;

UPDATE ref_geo.l_areas
   SET geom = ST_SetSRID(geom, :old_srid)
 WHERE ST_SRID(geom) <> :old_srid;

UPDATE ref_geo.l_areas
   SET centroid = ST_SetSRID(centroid, :old_srid)
 WHERE ST_SRID(centroid) <> :old_srid;

UPDATE gn_synthese.synthese
    SET the_geom_local = ST_SetSRID(the_geom_local, :old_srid)
WHERE ST_SRID(the_geom_local) <> :old_srid;

UPDATE gn_monitoring.t_base_sites
SET geom_local = ST_SetSRID(geom_local, :old_srid)
WHERE ST_SRID(geom_local) <> :old_srid;

UPDATE pr_occhab.t_stations
   SET geom_local = ST_SetSRID(geom_local, :old_srid)
 WHERE ST_SRID(geom_local) <> :old_srid;

 UPDATE pr_occtax.t_releves_occtax
   SET geom_local = ST_SetSRID(geom_local, :old_srid)
 WHERE ST_SRID(geom_local) <> :old_srid;