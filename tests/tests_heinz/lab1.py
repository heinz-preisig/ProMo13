from rdflib import Graph, Namespace

g = Graph()

ex = Namespace('http://example.org/')

g.bind("ex", ex)

#The Mueller Investigation was lead by Robert Mueller.
g.add((ex.Mueller_Investigation, ex.leadBy, ex.Robert_Muller))

#It involved Paul Manafort, Rick Gates, George Papadopoulos, Michael Flynn, and Roger Stone.
g.add((ex.Mueller_Investigation, ex.involved, ex.Paul_Manafort))
g.add((ex.Mueller_Investigation, ex.involved, ex.Rick_Gates))
g.add((ex.Mueller_Investigation, ex.involved, ex.George_Papadopoulos))
g.add((ex.Mueller_Investigation, ex.involved, ex.Michael_Flynn))
g.add((ex.Mueller_Investigation, ex.involved, ex.Michael_Cohen))
g.add((ex.Mueller_Investigation, ex.involved, ex.Roger_Stone))

# --- Paul Manafort ---
#Paul Manafort was business partner of Rick Gates.
g.add((ex.Paul_Manafort, ex.businessManager, ex.Rick_Gates))
# He was campaign chairman for Trump
g.add((ex.Paul_Manafort, ex.campaignChairman, ex.Donald_Trump))

# He was charged with money laundering, tax evasion, and foreign lobbying.
g.add((ex.Paul_Manafort, ex.chargedWith, ex.MoneyLaundering))
g.add((ex.Paul_Manafort, ex.chargedWith, ex.TaxEvasion))
g.add((ex.Paul_Manafort, ex.chargedWith, ex.ForeignLobbying))

# He was convicted for bank and tax fraud.
g.add((ex.Paul_Manafort, ex.convictedFor, ex.BankFraud))
g.add((ex.Paul_Manafort, ex.convictedFor, ex.TaxFraud))

# He pleaded guilty to conspiracy.
g.add((ex.Paul_Manafort, ex.pleadGuiltyTo, ex.Conspiracy))
# He was sentenced to prison.
g.add((ex.Paul_Manafort, ex.sentencedTo, ex.Prison))
# He negotiated a plea agreement.
g.add((ex.Paul_Manafort, ex.negoiated, ex.PleaBargain))

# --- Rick Gates ---
#Rick Gates was charged with money laundering, tax evasion and foreign lobbying.
g.add((ex.Rick_Gates, ex.chargedWith, ex.MoneyLaundering))
g.add((ex.Rick_Gates, ex.chargedWith, ex.TaxEvasion))
g.add((ex.Rick_Gates, ex.chargedWith, ex.ForeignLobbying))

#He pleaded guilty to conspiracy and lying to FBI.
g.add((ex.Rick_Gates, ex.pleadGuiltyTo, ex.Conspiracy))
g.add((ex.Rick_Gates, ex.pleadGuiltyTo, ex.LyingToFBI))

#Use the serialize method to write out the model in different formats on screen
print(g.serialize(format="ttl"))
# g.serialize("lab1.ttl", format="ttl") #or to file

#Loop through the triples in the model to print out all triples that have pleading guilty as predicate
for subject, object in g[ : ex.pleadGuiltyTo : ]:
    print(subject, ex.pleadGuiltyTo, object)

# Michael Cohen, Michael Flynn and the lying is part of lab 2 and therefore the answer is not provided this week

#Write a method (function) that submits your model for rendering and saves the returned image to file.
import requests
import shutil

def graphToImage(graph):
    data = {"rdf":graph, "from":"ttl", "to":"png"}
    link = "http://www.ldf.fi/service/rdf-grapher"
    response = requests.get(link, params = data, stream=True)
    # print(response.content)
    print(response.raw)
    with open("lab1.png", "wb") as fil:
        shutil.copyfileobj(response.raw, fil)

graph = g.serialize(format="ttl")
graphToImage(graph)
