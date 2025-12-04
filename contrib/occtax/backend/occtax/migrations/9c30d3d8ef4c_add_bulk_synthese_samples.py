"""Add randomized occtax sample data for synthese

Revision ID: 9c30d3d8ef4c
Revises: cce08a64eb4f
Create Date: 2024-05-21 10:00:00.000000

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "9c30d3d8ef4c"
down_revision = "87705981de5e"
depends_on = None


def upgrade():
    op.execute(
        """
        DO $$
        DECLARE
            v_dataset_ids integer[];
            v_local_srid integer := gn_commons.get_default_parameter('local_srid')::integer;
            v_taxref_version text := gn_commons.get_default_parameter('taxref_version');
            v_insert_count integer := 4000;
            v_module_id integer := gn_commons.get_id_module_bycode('OCCTAX');

            v_id_tech_collect integer := ref_nomenclatures.get_id_nomenclature('TECHNIQUE_OBS', '133');
            v_id_grp_typ integer := ref_nomenclatures.get_id_nomenclature('TYP_GRP', 'OBS');
            v_id_geo_object integer := ref_nomenclatures.get_id_nomenclature('NAT_OBJ_GEO', 'In');

            v_id_obs_tech integer := ref_nomenclatures.get_id_nomenclature('METH_OBS', '23');
            v_id_bio_condition integer := ref_nomenclatures.get_id_nomenclature('ETA_BIO', '1');
            v_id_bio_status integer := ref_nomenclatures.get_id_nomenclature('STATUT_BIO', '1');
            v_id_naturalness integer := ref_nomenclatures.get_id_nomenclature('NATURALITE', '1');
            v_id_exist_proof integer := ref_nomenclatures.get_id_nomenclature('PREUVE_EXIST', '0');
            v_id_observation_status integer := ref_nomenclatures.get_id_nomenclature('STATUT_OBS', 'Pr');
            v_id_blurring integer := ref_nomenclatures.get_id_nomenclature('DEE_FLOU', 'NON');
            v_id_diffusion integer := ref_nomenclatures.get_id_nomenclature('NIV_PRECIS', '5');
            v_id_determination_method integer := ref_nomenclatures.get_id_nomenclature('METH_DETERMIN', '2');

            v_life_stages integer[] := ARRAY[
                ref_nomenclatures.get_id_nomenclature('STADE_VIE', '2'),
                ref_nomenclatures.get_id_nomenclature('STADE_VIE', '3'),
                ref_nomenclatures.get_id_nomenclature('STADE_VIE', '4')
            ];
            v_sexes integer[] := ARRAY[
                ref_nomenclatures.get_id_nomenclature('SEXE', '2'),
                ref_nomenclatures.get_id_nomenclature('SEXE', '3'),
                ref_nomenclatures.get_id_nomenclature('SEXE', '4')
            ];
            v_obj_count integer := ref_nomenclatures.get_id_nomenclature('OBJ_DENBR', 'IND');
            v_type_count integer := ref_nomenclatures.get_id_nomenclature('TYP_DENBR', 'Co');
        BEGIN
            SELECT array_agg(id_dataset) INTO v_dataset_ids
            FROM gn_meta.t_datasets
            WHERE unique_dataset_id IN (
                '4d331cae-65e4-4948-b0b2-a11bc5bb46c2',
                'dadab32d-5f9e-4dba-aa1f-c06487d536e8'
            );

            IF COALESCE(array_length(v_dataset_ids, 1), 0) = 0 THEN
                RAISE WARNING 'No occtax sample datasets found; skipping random synthese samples.';
                RETURN;
            END IF;

            WITH taxa AS (
                SELECT
                    row_number() OVER () AS rn,
                    cd_nom,
                    nom_complet
                FROM taxonomie.taxref
                ORDER BY random()
                LIMIT 1000
            ), releves AS (
                SELECT
                    g AS idx,
                    uuid_generate_v4() AS unique_id_sinp_grp,
                    v_dataset_ids[1 + (floor(random() * array_length(v_dataset_ids, 1))::int)] AS id_dataset,
                    (ARRAY[3, 4, 6])[1 + ((g - 1) % 3)] AS observer_role,
                    (date '2019-01-01' + ((random() * 1825)::int))::date AS date_obs,
                    make_time((floor(random() * 21))::int, (floor(random() * 59))::int, 0) AS h_min,
                    400 + (random() * 1800)::int AS altitude_min,
                    400 + (random() * 1800)::int AS altitude_max,
                    ST_SetSRID(
                        ST_MakePoint(5 + random() * 2, 44.5 + random() * 0.8),
                        4326
                    ) AS geom_4326
                FROM generate_series(1, v_insert_count) g
            ), inserted_releves AS (
                INSERT INTO pr_occtax.t_releves_occtax (
                    unique_id_sinp_grp,
                    id_dataset,
                    id_digitiser,
                    id_nomenclature_tech_collect_campanule,
                    id_nomenclature_grp_typ,
                    id_nomenclature_geo_object_nature,
                    date_min,
                    date_max,
                    hour_min,
                    hour_max,
                    altitude_min,
                    altitude_max,
                    meta_device_entry,
                    comment,
                    geom_local,
                    geom_4326,
                    precision,
                    grp_method,
                    id_module
                )
                SELECT
                    r.unique_id_sinp_grp,
                    r.id_dataset,
                    r.observer_role,
                    v_id_tech_collect,
                    v_id_grp_typ,
                    v_id_geo_object,
                    r.date_obs,
                    r.date_obs,
                    r.h_min,
                    (r.h_min + make_interval(mins => 15 + (random() * 90)::int))::time,
                    r.altitude_min,
                    GREATEST(r.altitude_min, r.altitude_max),
                    'script',
                    'occtax-samples bulk synthese',
                    ST_Transform(r.geom_4326, v_local_srid),
                    r.geom_4326,
                    10 + (random() * 40)::int,
                    'echantillonnage aleatoire',
                    v_module_id
                FROM releves r
                RETURNING
                    id_releve_occtax,
                    id_dataset,
                    id_digitiser
            ), numbered_releves AS (
                SELECT
                    ir.*,
                    row_number() OVER (ORDER BY ir.id_releve_occtax) AS rn
                FROM inserted_releves ir
            ), occurrences AS (
                INSERT INTO pr_occtax.t_occurrences_occtax (
                    unique_id_occurence_occtax,
                    id_releve_occtax,
                    id_nomenclature_obs_technique,
                    id_nomenclature_bio_condition,
                    id_nomenclature_bio_status,
                    id_nomenclature_naturalness,
                    id_nomenclature_exist_proof,
                    id_nomenclature_diffusion_level,
                    id_nomenclature_observation_status,
                    id_nomenclature_blurring,
                    id_nomenclature_source_status,
                    id_nomenclature_behaviour,
                    determiner,
                    id_nomenclature_determination_method,
                    cd_nom,
                    nom_cite,
                    meta_v_taxref,
                    sample_number_proof,
                    digital_proof,
                    non_digital_proof,
                    comment
                )
                SELECT
                    uuid_generate_v4(),
                    nr.id_releve_occtax,
                    v_id_obs_tech,
                    v_id_bio_condition,
                    v_id_bio_status,
                    v_id_naturalness,
                    v_id_exist_proof,
                    v_id_diffusion,
                    v_id_observation_status,
                    v_id_blurring,
                    ds.id_nomenclature_source_status,
                    NULL,
                    'auto',
                    v_id_determination_method,
                    tx.cd_nom,
                    tx.nom_complet,
                    v_taxref_version,
                    NULL,
                    NULL,
                    NULL,
                    'occtax-samples bulk synthese'
                FROM numbered_releves nr
                JOIN gn_meta.t_datasets ds ON ds.id_dataset = nr.id_dataset
                JOIN LATERAL (
                    SELECT cd_nom, nom_complet
                    FROM taxa
                    ORDER BY random()
                    LIMIT 1
                ) AS tx ON TRUE
                RETURNING id_occurrence_occtax
            ), countings AS (
                INSERT INTO pr_occtax.cor_counting_occtax (
                    id_occurrence_occtax,
                    id_nomenclature_life_stage,
                    id_nomenclature_sex,
                    id_nomenclature_obj_count,
                    id_nomenclature_type_count,
                    count_min,
                    count_max
                )
                SELECT
                    oc.id_occurrence_occtax,
                    v_life_stages[1 + (floor(random() * array_length(v_life_stages, 1))::int)],
                    v_sexes[1 + (floor(random() * array_length(v_sexes, 1))::int)],
                    v_obj_count,
                    v_type_count,
                    base_counts.c_min,
                    base_counts.c_min + (random() * 5)::int AS count_max
                FROM occurrences oc
                CROSS JOIN LATERAL (SELECT 1 + (random() * 10)::int AS c_min) AS base_counts
                RETURNING id_counting_occtax
            )
            INSERT INTO pr_occtax.cor_role_releves_occtax (id_releve_occtax, id_role)
            SELECT id_releve_occtax, id_digitiser FROM inserted_releves;
        END $$;
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM pr_occtax.t_releves_occtax
        WHERE comment = 'occtax-samples bulk synthese';
        """
    )
