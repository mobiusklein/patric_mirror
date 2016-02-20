PATRIC-Mirror
================

A library for making a local copy of the Pathosystems Resource Integration Center's genome annotations in a relational database.

Some time ago I thought it'd be a great idea to include the annotations derived from PATRIC
in my project. Later I realized that the only programmatic method for accessing their data was
to use their FTP server to bulk download the relevant files and parse them. 

This little library is an attempt to make the process of consuming that data simpler, and provide a simple relational
scheme for representing that data once it is consumed. It uses SQLAlchemy's ORM to structure things.

It currently is hard-coded to use SQLite, however this could easily be changed to use an arbitrary database
connection URI.

.. code:: python
    
    from patric_mirror import mirror, make_session, Genome, Feature, Pathway

    db_file = "path/to/storage.db"
    mirror(db_file)  # mirror all annotations into this database

    # Later, looking for metabolism features

    session = make_session(db_file)
    balneola_vulgaris_metabolism_features = session.query(Feature).filter(Feature.accession == "AQXH01000001").join(
        Pathway).filter(Pathway.description.like("%metabolism%")).all()

    # Elsewhere, looking for features mapped by sequencing of this chromosome/genome

    from collectons import Counter
    mapped_coordinates = get_mapped_coordinates_from_sam_file()
    mapped_go_terms = Counter()

    for read_start, read_end in mapped_coordinates:
        features = session.query(Feature).filter(
            Feature.accession == "AQXH01000001", Feature.spans(read_start) or Feature.spans(read_end)).all()
        for feature in features:
            for go_term in feature.go_terms:
                mapped_go_terms[go_term.description] += 1



If you use data derived from PATRIC, please be sure to cite the relevant publication below:

.. note::
    
    Wattam, A.R., D. Abraham, O. Dalay, T.L. Disz, T. Driscoll, J.L. Gabbard, J.J. Gillespie, R. Gough, D. Hix, R. Kenyon, D. Machi, C. Mao, E.K. Nordberg, R. Olson, R. Overbeek, G.D. Pusch, M. Shukla, J. Schulman, R.L. Stevens, D.E. Sullivan, V. Vonstein, A. Warren, R. Will, M.J.C. Wilson, H. Seung Yoo, C. Zhang, Y. Zhang, B.W. Sobral (2014). “PATRIC, the bacterial bioinformatics database and analysis resource.” Nucl Acids Res 42 (D1): D581-D591.  doi:10.1093/nar/gkt1099.  PMID: 24225323.