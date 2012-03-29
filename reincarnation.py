#! /usr/bin/python

import argparse
from datetime import date
import urllib2
import urllib
import json

# Get the birth date.
parser = argparse.ArgumentParser()
parser.add_argument("-d")
args = parser.parse_args()

# Set the birth date.
(birth_year, birth_month, birth_day) = args.d.split('-')
birth_date = date(int(birth_year), int(birth_month), int(birth_day))

# Query the DBpedia SPARQL endpoint.
data = urllib.urlencode({
    'format': 'application/sparql-results+json',
    'query': '''
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?person ?name ?death_date
WHERE {{
  ?person a foaf:Person .
  ?person dcterms:subject <http://dbpedia.org/resource/Category:{0}_deaths> .
  ?person foaf:name ?name .
  ?person dbpedia-owl:deathDate ?death_date .
}}
ORDER BY ?death_date'''.format(birth_date.year)
})
f = urllib2.urlopen('http://dbpedia.org/sparql', data)
people = json.loads(f.read())

for person in people['results']['bindings']:
    
    person_uri = person['person']['value']
    person_name = person['name']['value']
    person_death_date = person['death_date']['value']
    
    # Some death dates have no year.
    # ^^<http://www.w3.org/2001/XMLSchema#gMonthDay>
    if person_death_date.startswith('-'):
        continue
    
    (person_death_year, person_death_month, person_death_day) \
        = person_death_date.split('-')
    person_death_date = date(int(person_death_year), 
                             int(person_death_month), 
                             int(person_death_day))
    
    # Some death years do not match the provided death year.
    if birth_date.year != person_death_date.year:
        continue
    
    # Calculate the difference between the two dates in days.
    timedelta = person_death_date - birth_date;
    
    # Ignore people who died on a different month and day.
    if timedelta.days != 0:
        continue
    
    print u'{0} {1} <{2}>'.format(person_death_date, person_name, person_uri)
