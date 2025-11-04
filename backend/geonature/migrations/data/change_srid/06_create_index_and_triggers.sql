-- 06_create_index_and_triggers.sql

-- recréation de l’index sur l_linears
CREATE INDEX ref_geo_l_linears_geom_idx
  ON ref_geo.l_linears
  USING GIST(geom);

CREATE INDEX idx_t_releves_occtax_geom_local
  ON pr_occtax.t_releves_occtax
  USING GIST(geom_local);

create trigger tri_update_calculate_sensitivity before
update
    of date_min,
    date_max,
    cd_nom,
    the_geom_local,
    id_nomenclature_bio_status,
    id_nomenclature_behaviour on
    gn_synthese.synthese for each row execute function gn_synthese.fct_tri_update_sensitivity_on_each_row();

create trigger tri_update_cor_area_synthese after
update
    of the_geom_local,
    the_geom_4326 on
    gn_synthese.synthese for each row execute function gn_synthese.fct_trig_update_in_cor_area_synthese();

create trigger tri_update_calculate_altitude before
update
    of geom_local,
    geom on
    gn_monitoring.t_base_sites for each row execute function ref_geo.fct_trg_calculate_alt_minmax('geom');


create trigger tri_calculate_geom_local before
insert
    or
update
    on
    gn_monitoring.t_sites_groups for each row execute function ref_geo.fct_trg_calculate_geom_local('geom',
    'geom_local');
create trigger tri_t_sites_groups_calculate_alt before
insert
    or
update
    on
    gn_monitoring.t_sites_groups for each row execute function ref_geo.fct_trg_calculate_alt_minmax('geom');
create trigger tri_insert_calculate_altitude before
insert
    on
    gn_monitoring.t_sites_groups for each row execute function ref_geo.fct_trg_calculate_alt_minmax('geom');
create trigger tri_update_calculate_altitude before
update
    of geom_local,
    geom on
    gn_monitoring.t_sites_groups for each row execute function ref_geo.fct_trg_calculate_alt_minmax('geom');