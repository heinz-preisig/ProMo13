#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 ProMo RDF configuration
===============================================================================
It defines the ontology names and locations

2004-04-25

"""

BASE = "http://example.org"
PROMO = BASE + "#"
PROMOLG = BASE + "/language#"

PROMONWS = BASE + "/networks#"
PROMOVARS = BASE + "/variables#"
PROMOINDICES = BASE + "/indices#"

QUDT = "http://qudt.org/vocab/quantitykind/"
QUDT_units = "http://qudt.org/vocab/unit/"

PROMO_UNIT_PREFIX = "unit"
UNITS = [("time", "SEC"),
         ("length", "M"),
         ("amount", "MOL"),
         ("mass", "KiloGM"),
         ("temperature", "K"),
         ("current", "A"),
         ("light", "CD"),
         ("nil", "UNITLESS"),
         ]