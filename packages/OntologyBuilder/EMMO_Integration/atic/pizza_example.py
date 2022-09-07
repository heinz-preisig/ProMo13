

from owlready2 import *
 #http://test.org/onto.owl") pizza_example.py



def render_func(entity):
    name = entity.label[0] if len(entity.label) == 1 else entity.name
    return "%s.%s" % (entity.namespace.name, name)
owlready2.set_render_func(render_func)


# onto_path.append("/path/to/your/local/ontology/repository")
onto = get_ontology("./pizza/pizza_onto_2.owl")  # is copy of http://www.lesfleursdunormal.fr/static/_downloads/pizza_onto.owl
# onto = get_ontology("./pizza/pizza_xml.owl")  # is copy of http://www.lesfleursdunormal.fr/static/_downloads/pizza_onto.owl
# onto = get_ontology("./pizza/pizza.owl")    #!!! this does not work
# onto = get_ontology("http://www.lesfleursdunormal.fr/static/_downloads/pizza_onto.owl")
onto.load()

# sync_reasoner_pellet()
print("classes ", list(onto.classes()))
for c in onto.classes():
  print(c)

print(onto.Pizza)

with onto:
  class NonVegetarianPizza(onto.Pizza):
    equivalent_to = [
      onto.Pizza
      & (onto.has_topping.some(onto.MeatTopping)
         | onto.has_topping.some(onto.FishTopping)
         )
      ]
    def eat(self):
      answ = "Beurk! I'm vegetarian!"
      return answ

test_pizza = onto.Pizza("test_pizza_owl_identifier")
test_pizza.has_topping = [onto.CheeseTopping(),
                          onto.TomatoTopping(),
                          onto.MeatTopping()]

sync_reasoner_pellet()


print("class :  ", test_pizza.__class__)
print("class :  ", list(onto.classes()))
print("eat   :  ", test_pizza.eat())

onto.save("gugus.owl")