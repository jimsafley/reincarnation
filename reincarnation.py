#!/usr/bin/python
# coding: utf-8

import argparse
import urllib2
import json
from urllib import urlencode
from datetime import date

# Get the birth date from the command line arguments.
parser = argparse.ArgumentParser()
parser.add_argument("-d")
args = parser.parse_args()
birth_date = date(*map(int, args.d.split('-')))

# Query the DBpedia SPARQL endpoint. Select all people whose death date is 
# identical to the provided birth date.
data = urlencode({
    'format': 'application/sparql-results+json',
    'query': '''
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?person ?name ?birth_date ?death_date
WHERE {{
  ?person a foaf:Person ;
          dcterms:subject <http://dbpedia.org/resource/Category:{0}_deaths> ;
          foaf:name ?name ;
          dbpedia-owl:birthDate ?birth_date ;
          dbpedia-owl:deathDate ?death_date .
  FILTER regex(?death_date, "{1}")
}}
ORDER BY ?death_date'''.format(birth_date.year, birth_date)
})
people = json.loads(urllib2.urlopen('http://dbpedia.org/sparql', data).read())

for p in people['results']['bindings']:
    person = {'uri': p['person']['value'], 'name': p['name']['value'], 
              'birth_date': date(*map(int, p['birth_date']['value'].split('-'))), 
              'death_date': date(*map(int, p['death_date']['value'].split('-')))}
    print u'{birth_date}–{death_date} {name} <{uri}>'.format(**person)
