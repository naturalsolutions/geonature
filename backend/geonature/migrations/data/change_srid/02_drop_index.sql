-- 02_drop_index.sql
DROP INDEX IF EXISTS ref_geo.ref_geo_l_linears_geom_idx;
-- t_releves_occtax (si vous aviez un index GiST sur geom_local)
DROP INDEX IF EXISTS pr_occtax.idx_t_releves_occtax_geom_local;