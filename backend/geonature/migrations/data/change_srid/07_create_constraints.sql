-- 07_create_constraints.sql

-- ref_geo.l_areas : SRID‐checks
ALTER TABLE ref_geo.l_areas
  ADD CONSTRAINT enforce_srid_l_areas_geom
    CHECK ( ST_SRID(geom) = :new_srid );

ALTER TABLE ref_geo.l_areas
  ADD CONSTRAINT enforce_srid_l_areas_centroid
    CHECK ( ST_SRID(centroid) = :new_srid );


-- synthese : SRID‐check
ALTER TABLE gn_synthese.synthese
  ADD CONSTRAINT enforce_srid_the_geom_local
    CHECK ( ST_SRID(the_geom_local) = :new_srid );
