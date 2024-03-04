GRAPH_TEMPLATE = {
    'university_degrees': {
        'slots': ['University'],
        'question': 'What degrees does %University% offer?',
        'cypher': "MATCH (u:University {name: '%University%'})-[:OFFERS]->(d:Degree) RETURN d.name AS degrees",
        'answer': '%University% offers the following degrees: %degrees%',
    },
    'degree_includes': {
        'slots': ['Degree'],
        'question': 'What are the academic years included in the %Degree%?',
        'cypher': "MATCH (:Degree {name: '%Degree%'})-[:INCLUDES]->(y:Year) RETURN y.name AS years",
        'answer': 'The %Degree% includes: %years%',
    },
    'year_compulsory_modules': {
        'slots': ['Year'],
        'question': 'What compulsory modules does %Year% include?',
        'cypher': "MATCH (:Year {name: '%Year%'})-[:INCLUDES_COMPULSORY]->(m:CompulsoryModule) RETURN m.name AS compulsoryModules",
        'answer': 'The %Year% includes these compulsory modules: %compulsoryModules%',
    },
    'year_optional_modules': {
        'slots': ['Year'],
        'question': 'What optional modules does %Year% include?',
        'cypher': "MATCH (:Year {name: '%Year%'})-[:INCLUDES_OPTIONAL]->(m:OptionalModule) RETURN m.name AS optionalModules",
        'answer': 'The %Year% includes these optional modules: %optionalModules%',
    },
    'year_compulsory_module_count': {
    'slots': ['Year'],
    'question': 'How many compulsory modules does the university of liverpool offered of %Year%?',
    'cypher': """
        MATCH (:Year {name: '%Year%'})-[:INCLUDES_COMPULSORY]->(m)
        RETURN COUNT(m) AS moduleCount
    """,
    'answer': 'There are %moduleCount% compulsory modules in %Year%.',
    },
    'year_optional_module_count': {
    'slots': ['Year'],
    'question': 'How many optional modules does the university of liverpool offered of %Year%?',
    'cypher': """
        MATCH (:Year {name: '%Year%'})-[:INCLUDES_OPTIONAL]->(m)
        RETURN COUNT(m) AS moduleCount
    """,
    'answer': 'There are %moduleCount% optional modules in %Year%.',
    },
    'year_module_count': {
    'slots': ['Year'],
    'question': 'How many modules does the university of liverpool offered of %Year%?',
    'cypher': """
        MATCH (:Year {name: '%Year%'})-[:INCLUDES_COMPULSORY|INCLUDES_OPTIONAL]->(m)
        RETURN COUNT(m) AS moduleCount
    """,
    'answer': 'There are %moduleCount% modules in %Year%.',
    },
    'compulsory_module_code': {
        'slots': ['CompulsoryModule'],
        'question': 'What is the code of %CompulsoryModule%?',
        'cypher': "MATCH (m:CompulsoryModule {name: '%CompulsoryModule%'}) RETURN m.code AS code",
        'answer': 'The code of %CompulsoryModule% is: %code%',
    },
    'compulsory_module_credits': {
        'slots': ['CompulsoryModule'],
        'question': 'How many credits does %CompulsoryModule% have?',
        'cypher': "MATCH (m:CompulsoryModule {name: '%CompulsoryModule%'}) RETURN m.credits AS credits",
        'answer': '%CompulsoryModule% has %credits% credits.',
    },
    'compulsory_module_semester': {
        'slots': ['CompulsoryModule'],
        'question': 'Which semester does %CompulsoryModule% belong to?',
        'cypher': "MATCH (m:CompulsoryModule {name: '%CompulsoryModule%'}) RETURN m.semester AS semester",
        'answer': '%CompulsoryModule% belongs to semester: %semester%',
    },
    'compulsory_module_description': {
        'slots': ['CompulsoryModule'],
        'question': 'What is the description of %CompulsoryModule%?',
        'cypher': "MATCH (m:CompulsoryModule {name: '%CompulsoryModule%'}) RETURN m.desc AS description",
        'answer': 'The description of %CompulsoryModule% is: %description%',
    },
    'optional_module_code': {
        'slots': ['OptionalModule'],
        'question': 'What is the code of %OptionalModule%?',
        'cypher': "MATCH (m:OptionalModule {name: '%OptionalModule%'}) RETURN m.code AS code",
        'answer': 'The code of %OptionalModule% is: %code%',
    },
    'optional_module_credits': {
        'slots': ['OptionalModule'],
        'question': 'How many credits does %OptionalModule% have?',
        'cypher': "MATCH (m:OptionalModule {name: '%OptionalModule%'}) RETURN m.credits AS credits",
        'answer': '%OptionalModule% has %credits% credits.',
    },
    'optional_module_semester': {
        'slots': ['OptionalModule'],
        'question': 'Which semester does %OptionalModule% belong to?',
        'cypher': "MATCH (m:OptionalModule {name: '%OptionalModule%'}) RETURN m.semester AS semester",
        'answer': '%OptionalModule% belongs to semester: %semester%',
    },
    'optional_module_description': {
        'slots': ['OptionalModule'],
        'question': 'What is the description of %OptionalModule%?',
        'cypher': "MATCH (m:OptionalModule {name: '%OptionalModule%'}) RETURN m.desc AS description",
        'answer': 'The description of %OptionalModule% is: %description%',
    },
}