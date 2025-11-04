-- 05_create_views.sql
-- Crée (ou recrée) toutes les vues après avoir migré tous les SRID

-- ─── 1) Vue v_synthese_for_profiles ────────────────────────────────────────────
CREATE OR REPLACE VIEW gn_profiles.v_synthese_for_profiles
AS WITH excluded_live_stage AS (
         SELECT ref_nomenclatures.get_id_nomenclature('STADE_VIE'::character varying, '0'::character varying) AS id_n_excluded
        UNION
         SELECT ref_nomenclatures.get_id_nomenclature('STADE_VIE'::character varying, '1'::character varying) AS id_n_excluded
        )
 SELECT s.id_synthese,
    s.cd_nom,
    s.nom_cite,
    t.cd_ref,
    t.nom_valide,
    t.id_rang,
    s.date_min,
    s.date_max,
    s.the_geom_local,
    s.the_geom_4326,
    s.altitude_min,
    s.altitude_max,
        CASE
            WHEN (s.id_nomenclature_life_stage IN ( SELECT excluded_live_stage.id_n_excluded
               FROM excluded_live_stage)) THEN NULL::integer
            ELSE s.id_nomenclature_life_stage
        END AS id_nomenclature_life_stage,
    s.id_nomenclature_valid_status,
    p.spatial_precision,
    p.temporal_precision_days,
    p.active_life_stage,
    p.distance
   FROM gn_synthese.synthese s
     LEFT JOIN taxonomie.taxref t ON s.cd_nom = t.cd_nom
     CROSS JOIN LATERAL gn_profiles.get_parameters(s.cd_nom) p(cd_ref, spatial_precision, temporal_precision_days, active_life_stage, distance)
  WHERE p.spatial_precision IS NOT NULL AND st_maxdistance(st_centroid(s.the_geom_local), s.the_geom_local) < p.spatial_precision::double precision AND s.altitude_max IS NOT NULL AND s.altitude_min IS NOT NULL AND (s.id_nomenclature_valid_status IN ( SELECT regexp_split_to_table(t_parameters.value, ','::text)::integer AS regexp_split_to_table
           FROM gn_profiles.t_parameters
          WHERE t_parameters.name::text = 'id_valid_status_for_profiles'::text)) AND (t.id_rang::text IN ( SELECT regexp_split_to_table(t_parameters.value, ','::text) AS regexp_split_to_table
           FROM gn_profiles.t_parameters
          WHERE t_parameters.name::text = 'id_rang_for_profiles'::text));

COMMENT ON VIEW gn_profiles.v_synthese_for_profiles IS 'View containing synthese data feeding profiles calculation.
 cd_ref, date_min, date_max, the_geom_local, altitude_min, altitude_max and
 id_nomenclature_life_stage fields are mandatory.
 WHERE clauses have to apply your t_parameters filters (valid_status)';


--- vm_cor_taxon_phenology

CREATE MATERIALIZED VIEW gn_profiles.vm_cor_taxon_phenology
TABLESPACE pg_default
AS WITH exlude_live_stage AS (
         SELECT ref_nomenclatures.get_id_nomenclature('STADE_VIE'::character varying, '0'::character varying) AS id_n_excluded
        UNION
         SELECT ref_nomenclatures.get_id_nomenclature('STADE_VIE'::character varying, '1'::character varying) AS id_n_excluded
        ), params AS (
         SELECT parameters.value::double precision / 100::double precision AS proportion_kept_data
           FROM gn_profiles.t_parameters parameters
          WHERE parameters.name::text = 'proportion_kept_data'::text
        ), classified_data AS (
         SELECT DISTINCT vsfp.cd_ref,
            unnest(ARRAY[floor(date_part('doy'::text, vsfp.date_min) / vsfp.temporal_precision_days::double precision) * vsfp.temporal_precision_days::double precision, floor(date_part('doy'::text, vsfp.date_max) / vsfp.temporal_precision_days::double precision) * vsfp.temporal_precision_days::double precision]) AS doy_min,
            unnest(ARRAY[floor(date_part('doy'::text, vsfp.date_min) / vsfp.temporal_precision_days::double precision) * vsfp.temporal_precision_days::double precision + vsfp.temporal_precision_days::double precision, floor(date_part('doy'::text, vsfp.date_max) / vsfp.temporal_precision_days::double precision) * vsfp.temporal_precision_days::double precision + vsfp.temporal_precision_days::double precision]) AS doy_max,
                CASE
                    WHEN vsfp.active_life_stage = true AND NOT (vsfp.id_nomenclature_life_stage IN ( SELECT exlude_live_stage.id_n_excluded
                       FROM exlude_live_stage)) THEN vsfp.id_nomenclature_life_stage
                    ELSE NULL::integer
                END AS id_nomenclature_life_stage,
            count(vsfp.*) AS count_valid_data,
            min(vsfp.altitude_min) AS extreme_altitude_min,
            percentile_disc(( SELECT params.proportion_kept_data
                   FROM params)) WITHIN GROUP (ORDER BY vsfp.altitude_min DESC) AS p_min,
            max(vsfp.altitude_max) AS extreme_altitude_max,
            percentile_disc(( SELECT params.proportion_kept_data
                   FROM params)) WITHIN GROUP (ORDER BY vsfp.altitude_max) AS p_max
           FROM gn_profiles.v_synthese_for_profiles vsfp
          WHERE vsfp.temporal_precision_days IS NOT NULL AND vsfp.spatial_precision IS NOT NULL AND vsfp.active_life_stage IS NOT NULL AND date_part('day'::text, vsfp.date_max - vsfp.date_min) < vsfp.temporal_precision_days::double precision AND vsfp.altitude_min IS NOT NULL AND vsfp.altitude_max IS NOT NULL
          GROUP BY vsfp.cd_ref, (unnest(ARRAY[floor(date_part('doy'::text, vsfp.date_min) / vsfp.temporal_precision_days::double precision) * vsfp.temporal_precision_days::double precision, floor(date_part('doy'::text, vsfp.date_max) / vsfp.temporal_precision_days::double precision) * vsfp.temporal_precision_days::double precision])), (unnest(ARRAY[floor(date_part('doy'::text, vsfp.date_min) / vsfp.temporal_precision_days::double precision) * vsfp.temporal_precision_days::double precision + vsfp.temporal_precision_days::double precision, floor(date_part('doy'::text, vsfp.date_max) / vsfp.temporal_precision_days::double precision) * vsfp.temporal_precision_days::double precision + vsfp.temporal_precision_days::double precision])), (
                CASE
                    WHEN vsfp.active_life_stage = true AND NOT (vsfp.id_nomenclature_life_stage IN ( SELECT exlude_live_stage.id_n_excluded
                       FROM exlude_live_stage)) THEN vsfp.id_nomenclature_life_stage
                    ELSE NULL::integer
                END)
        )
 SELECT cd_ref,
    doy_min,
    doy_max,
    id_nomenclature_life_stage,
    count_valid_data,
    extreme_altitude_min,
    p_min AS calculated_altitude_min,
    extreme_altitude_max,
    p_max AS calculated_altitude_max
   FROM classified_data
WITH DATA;

CREATE INDEX index_vm_cor_taxon_phenology_cd_ref ON gn_profiles.vm_cor_taxon_phenology USING btree (cd_ref);
CREATE UNIQUE INDEX vm_cor_taxon_phenology_cd_ref_period_id_nomenclature_life_s_idx ON gn_profiles.vm_cor_taxon_phenology USING btree (cd_ref, doy_min, doy_max, id_nomenclature_life_stage);

COMMENT ON MATERIALIZED VIEW gn_profiles.vm_cor_taxon_phenology IS 'View containing phenological combinations and corresponding valid data for each taxa';

-- vm_valid_profiles
CREATE MATERIALIZED VIEW gn_profiles.vm_valid_profiles
TABLESPACE pg_default
AS SELECT DISTINCT cd_ref,
    st_union(st_buffer(the_geom_local, COALESCE(spatial_precision, 1)::double precision)) AS valid_distribution,
    min(altitude_min) AS altitude_min,
    max(altitude_max) AS altitude_max,
    min(date_min) AS first_valid_data,
    max(date_max) AS last_valid_data,
    count(vsfp.*) AS count_valid_data,
    active_life_stage
   FROM gn_profiles.v_synthese_for_profiles vsfp
  GROUP BY cd_ref, active_life_stage
WITH DATA;

CREATE UNIQUE INDEX index_vm_valid_profiles_cd_ref ON gn_profiles.vm_valid_profiles USING btree (cd_ref);

-- v_consistancy_data
CREATE OR REPLACE VIEW gn_profiles.v_consistancy_data
AS SELECT s.id_synthese,
    s.unique_id_sinp AS id_sinp,
    t.cd_ref,
    t.lb_nom AS valid_name,
    gn_profiles.check_profile_distribution(s.the_geom_local, p.valid_distribution) AS valid_distribution,
    gn_profiles.check_profile_phenology(t.cd_ref, s.date_min::date, s.date_max::date, s.altitude_min, s.altitude_max, s.id_nomenclature_life_stage, p.active_life_stage) AS valid_phenology,
    gn_profiles.check_profile_altitudes(s.altitude_min, s.altitude_max, p.altitude_min, p.altitude_max) AS valid_altitude,
    n.label_default AS valid_status
   FROM gn_synthese.synthese s
     JOIN taxonomie.taxref t ON s.cd_nom = t.cd_nom
     JOIN gn_profiles.vm_valid_profiles p ON p.cd_ref = t.cd_ref
     LEFT JOIN ref_nomenclatures.t_nomenclatures n ON s.id_nomenclature_valid_status = n.id_nomenclature;

-- v_synthese_for_export
CREATE OR REPLACE VIEW gn_synthese.v_synthese_for_export
AS SELECT s.id_synthese,
    s.date_min::date AS date_debut,
    s.date_max::date AS date_fin,
    s.date_min::time without time zone AS heure_debut,
    s.date_max::time without time zone AS heure_fin,
    t.cd_nom,
    t.cd_ref,
    t.nom_valide,
    t.nom_vern AS nom_vernaculaire,
    s.nom_cite,
    t.regne,
    t.group1_inpn,
    t.group2_inpn,
    t.group3_inpn,
    t.classe,
    t.ordre,
    t.famille,
    t.id_rang AS rang_taxo,
    s.count_min AS nombre_min,
    s.count_max AS nombre_max,
    s.altitude_min AS alti_min,
    s.altitude_max AS alti_max,
    s.depth_min AS prof_min,
    s.depth_max AS prof_max,
    s.observers AS observateurs,
    s.id_digitiser,
    s.determiner AS determinateur,
    sa.communes,
    st_astext(s.the_geom_4326) AS geometrie_wkt_4326,
    st_x(s.the_geom_point) AS x_centroid_4326,
    st_y(s.the_geom_point) AS y_centroid_4326,
    st_asgeojson(s.the_geom_4326) AS geojson_4326,
    st_asgeojson(s.the_geom_local) AS geojson_local,
    s.place_name AS nom_lieu,
    s.comment_context AS comment_releve,
    s.comment_description AS comment_occurrence,
    s.validator AS validateur,
    n21.label_default AS niveau_validation,
    s.meta_validation_date AS date_validation,
    s.validation_comment AS comment_validation,
    s.digital_proof AS preuve_numerique_url,
    s.non_digital_proof AS preuve_non_numerique,
    d.dataset_name AS jdd_nom,
    d.unique_dataset_id AS jdd_uuid,
    d.id_dataset AS jdd_id,
    af.acquisition_framework_name AS ca_nom,
    af.unique_acquisition_framework_id AS ca_uuid,
    d.id_acquisition_framework AS ca_id,
    s.cd_hab AS cd_habref,
    hab.lb_code AS cd_habitat,
    hab.lb_hab_fr AS nom_habitat,
    s."precision" AS precision_geographique,
    n1.label_default AS nature_objet_geo,
    n2.label_default AS type_regroupement,
    s.grp_method AS methode_regroupement,
    n3.label_default AS technique_observation,
    n5.label_default AS biologique_statut,
    n6.label_default AS etat_biologique,
    n22.label_default AS biogeographique_statut,
    n7.label_default AS naturalite,
    n8.label_default AS preuve_existante,
    n9.label_default AS niveau_precision_diffusion,
    n10.label_default AS stade_vie,
    n11.label_default AS sexe,
    n12.label_default AS objet_denombrement,
    n13.label_default AS type_denombrement,
    n14.label_default AS niveau_sensibilite,
    n15.label_default AS statut_observation,
    n16.label_default AS floutage_dee,
    n17.label_default AS statut_source,
    n18.label_default AS type_info_geo,
    n19.label_default AS methode_determination,
    n20.label_default AS comportement,
    s.reference_biblio,
    s.entity_source_pk_value AS id_origine,
    s.unique_id_sinp AS uuid_perm_sinp,
    s.unique_id_sinp_grp AS uuid_perm_grp_sinp,
    s.meta_create_date AS date_creation,
    s.meta_update_date AS date_modification,
    s.additional_data AS champs_additionnels,
    COALESCE(s.meta_update_date, s.meta_create_date) AS derniere_action
   FROM gn_synthese.synthese s
     JOIN taxonomie.taxref t ON t.cd_nom = s.cd_nom
     JOIN gn_meta.t_datasets d ON d.id_dataset = s.id_dataset
     JOIN gn_meta.t_acquisition_frameworks af ON d.id_acquisition_framework = af.id_acquisition_framework
     LEFT JOIN ( SELECT cas.id_synthese,
            string_agg(DISTINCT a_1.area_name::text, ', '::text) AS communes
           FROM gn_synthese.cor_area_synthese cas
             LEFT JOIN ref_geo.l_areas a_1 ON cas.id_area = a_1.id_area
             JOIN ref_geo.bib_areas_types ta ON ta.id_type = a_1.id_type AND ta.type_code::text = 'COM'::text
          GROUP BY cas.id_synthese) sa ON sa.id_synthese = s.id_synthese
     LEFT JOIN ref_nomenclatures.t_nomenclatures n1 ON s.id_nomenclature_geo_object_nature = n1.id_nomenclature
     LEFT JOIN ref_nomenclatures.t_nomenclatures n2 ON s.id_nomenclature_grp_typ = n2.id_nomenclature
     LEFT JOIN ref_nomenclatures.t_nomenclatures n3 ON s.id_nomenclature_obs_technique = n3.id_nomenclature
     LEFT JOIN ref_nomenclatures.t_nomenclatures n5 ON s.id_nomenclature_bio_status = n5.id_nomenclature
     LEFT JOIN ref_nomenclatures.t_nomenclatures n6 ON s.id_nomenclature_bio_condition = n6.id_nomenclature
     LEFT JOIN ref_nomenclatures.t_nomenclatures n7 ON s.id_nomenclature_naturalness = n7.id_nomenclature
     LEFT JOIN ref_nomenclatures.t_nomenclatures n8 ON s.id_nomenclature_exist_proof = n8.id_nomenclature
     LEFT JOIN ref_nomenclatures.t_nomenclatures n9 ON s.id_nomenclature_diffusion_level = n9.id_nomenclature
     LEFT JOIN ref_nomenclatures.t_nomenclatures n10 ON s.id_nomenclature_life_stage = n10.id_nomenclature
     LEFT JOIN ref_nomenclatures.t_nomenclatures n11 ON s.id_nomenclature_sex = n11.id_nomenclature
     LEFT JOIN ref_nomenclatures.t_nomenclatures n12 ON s.id_nomenclature_obj_count = n12.id_nomenclature
     LEFT JOIN ref_nomenclatures.t_nomenclatures n13 ON s.id_nomenclature_type_count = n13.id_nomenclature
     LEFT JOIN ref_nomenclatures.t_nomenclatures n14 ON s.id_nomenclature_sensitivity = n14.id_nomenclature
     LEFT JOIN ref_nomenclatures.t_nomenclatures n15 ON s.id_nomenclature_observation_status = n15.id_nomenclature
     LEFT JOIN ref_nomenclatures.t_nomenclatures n16 ON s.id_nomenclature_blurring = n16.id_nomenclature
     LEFT JOIN ref_nomenclatures.t_nomenclatures n17 ON s.id_nomenclature_source_status = n17.id_nomenclature
     LEFT JOIN ref_nomenclatures.t_nomenclatures n18 ON s.id_nomenclature_info_geo_type = n18.id_nomenclature
     LEFT JOIN ref_nomenclatures.t_nomenclatures n19 ON s.id_nomenclature_determination_method = n19.id_nomenclature
     LEFT JOIN ref_nomenclatures.t_nomenclatures n20 ON s.id_nomenclature_behaviour = n20.id_nomenclature
     LEFT JOIN ref_nomenclatures.t_nomenclatures n21 ON s.id_nomenclature_valid_status = n21.id_nomenclature
     LEFT JOIN ref_nomenclatures.t_nomenclatures n22 ON s.id_nomenclature_biogeo_status = n22.id_nomenclature
     LEFT JOIN ref_habitats.habref hab ON hab.cd_hab = s.cd_hab;

CREATE OR REPLACE VIEW pr_occhab.v_export_sinp
AS SELECT s.id_station,
    s.id_dataset,
    s.id_digitiser,
    s.unique_id_sinp_station AS uuid_station,
    ds.unique_dataset_id AS uuid_jdd,
    to_char(s.date_min, 'DD/MM/YYYY'::text) AS date_debut,
    to_char(s.date_max, 'DD/MM/YYYY'::text) AS date_fin,
    COALESCE(string_agg(DISTINCT (r.nom_role::text || ' '::text) || r.prenom_role::text, ','::text), s.observers_txt::text) AS observateurs,
    nom2.cd_nomenclature AS methode_calcul_surface,
    s.area AS surface,
    st_astext(s.geom_4326) AS geometry,
    st_asgeojson(s.geom_4326) AS geojson,
    s.geom_local,
    nom3.cd_nomenclature AS nature_objet_geo,
    h.unique_id_sinp_hab AS uuid_habitat,
    s.altitude_min,
    s.altitude_max,
    nom5.cd_nomenclature AS exposition,
    h.nom_cite,
    h.cd_hab,
    h.technical_precision AS precision_technique
   FROM pr_occhab.t_stations s
     JOIN pr_occhab.t_habitats h ON h.id_station = s.id_station
     JOIN gn_meta.t_datasets ds ON ds.id_dataset = s.id_dataset
     LEFT JOIN pr_occhab.cor_station_observer cso ON cso.id_station = s.id_station
     LEFT JOIN utilisateurs.t_roles r ON r.id_role = cso.id_role
     LEFT JOIN ref_nomenclatures.t_nomenclatures nom1 ON nom1.id_nomenclature = ds.id_nomenclature_data_origin
     LEFT JOIN ref_nomenclatures.t_nomenclatures nom2 ON nom2.id_nomenclature = s.id_nomenclature_area_surface_calculation
     LEFT JOIN ref_nomenclatures.t_nomenclatures nom3 ON nom3.id_nomenclature = s.id_nomenclature_geographic_object
     LEFT JOIN ref_nomenclatures.t_nomenclatures nom4 ON nom4.id_nomenclature = h.id_nomenclature_collection_technique
     LEFT JOIN ref_nomenclatures.t_nomenclatures nom5 ON nom5.id_nomenclature = s.id_nomenclature_exposure
  GROUP BY s.id_station, s.id_dataset, ds.unique_dataset_id, nom2.cd_nomenclature, h.technical_precision, h.cd_hab, h.nom_cite, nom3.cd_nomenclature, h.unique_id_sinp_hab, nom5.cd_nomenclature;

-- 4) on rafraîchit les matérialisées
REFRESH MATERIALIZED VIEW gn_profiles.vm_cor_taxon_phenology;
REFRESH MATERIALIZED VIEW gn_profiles.vm_valid_profiles;