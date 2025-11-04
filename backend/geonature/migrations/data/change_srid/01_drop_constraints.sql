-- 01_drop_constraints.sql
-- l_areas
ALTER TABLE ref_geo.l_areas
  DROP CONSTRAINT IF EXISTS enforce_srid_l_areas_geom;
ALTER TABLE ref_geo.l_areas
  DROP CONSTRAINT IF EXISTS enforce_srid_l_areas_centroid;
-- synthese
ALTER TABLE gn_synthese.synthese
  DROP CONSTRAINT IF EXISTS enforce_srid_the_geom_local;

-- pr_occhab.t_stations
ALTER TABLE pr_occhab.t_stations
  DROP CONSTRAINT IF EXISTS enforce_srid_geom_local;

-- pr_occtax.t_releves_occtax
ALTER TABLE pr_occtax.t_releves_occtax
  DROP CONSTRAINT IF EXISTS enforce_srid_geom_local;

-- Supprime *toutes* les contraintes enforce_* en une fois
SET search_path = ref_geo, public;
SELECT DropRasterConstraints('dem','rast');