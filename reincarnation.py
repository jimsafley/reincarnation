#!/usr/bin/python

import argparse
import urllib2
import json
from urllib import urlencode
from datetime import date

def dbpedia(query, binding=None):
    '''Query the DBpedia SPARQL endpoint'''
    data = urlencode({'format': 'application/sparql-results+json', 'query': query})
    result = json.loads(urllib2.urlopen('http://dbpedia.org/sparql', data).read())\
             .get('results').get('bindings')
    if binding is not None:
        result = [value[binding]['value'] for value in result]
    return result

# Get the birth date from the command line arguments.
parser = argparse.ArgumentParser()
parser.add_argument("-d")
args = parser.parse_args()
birth_date = date(*map(int, args.d.split('-')))

# Select all people whose death date is identical to the provided birth date, 
# ordered by the birth date. 
query = '''
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
SELECT ?person ?birth_date ?label
WHERE {{
  ?person a foaf:Person ;
          dbpedia-owl:deathDate ?death_date .
  OPTIONAL {{ ?person rdfs:label ?label }}
  OPTIONAL {{ ?person dbpedia-owl:birthDate ?birth_date }}
  FILTER regex( ?death_date, '^{0}' )
  FILTER langMatches( lang(?label), "EN" )
}}
ORDER BY ?birth_date'''.format(birth_date)

for p in dbpedia(query):
    person = {'uri': p['person']['value'], 
              'birth_date': date(*map(int, p['birth_date']['value'].split('-')))}
    query = '''
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT ?name
    WHERE {{
      <{0}> foaf:name ?name .
    }}'''.format(person['uri'])
    for name in dbpedia(query, 'name'):
        print name
    print u'{birth_date} <{uri}>'.format(**person)
