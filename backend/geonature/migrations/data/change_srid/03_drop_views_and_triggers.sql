-- 03_drop_views_and_triggers.sql
-- DROP des vues avant les modifications de types
DROP VIEW IF EXISTS gn_profiles.v_consistancy_data;
DROP MATERIALIZED VIEW IF EXISTS gn_profiles.vm_cor_taxon_phenology;
DROP MATERIALIZED VIEW IF EXISTS gn_profiles.vm_valid_profiles;
DROP VIEW IF EXISTS gn_profiles.v_synthese_for_profiles;
DROP VIEW IF EXISTS gn_synthese.v_synthese_for_export;
DROP VIEW IF EXISTS pr_occhab.v_export_sinp;
-- on droppe le trigger qui dépend de the_geom_local
DROP TRIGGER IF EXISTS tri_update_calculate_sensitivity
  ON gn_synthese.synthese;

DROP TRIGGER IF EXISTS tri_update_cor_area_synthese ON gn_synthese.synthese;
DROP TRIGGER IF EXISTS tri_update_calculate_altitude on gn_monitoring.t_base_sites;

DROP TRIGGER tri_update_calculate_altitude ON gn_monitoring.t_sites_groups;
DROP TRIGGER tri_calculate_geom_local ON gn_monitoring.t_sites_groups;
DROP TRIGGER tri_t_sites_groups_calculate_alt ON gn_monitoring.t_sites_groups;
DROP TRIGGER tri_insert_calculate_altitude ON gn_monitoring.t_sites_groups;