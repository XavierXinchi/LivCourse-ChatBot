from py2neo import Graph
import json
from tqdm import tqdm
import os
from dotenv import load_dotenv
load_dotenv()

class CreateKG():

    def __init__(self, kg_host, kg_port, kg_user, kg_password, data_path):
        uri = f"bolt://{kg_user}:{kg_password}@{kg_host}:{kg_port}"
        self.graph = Graph(uri)

        if not data_path or data_path == '':
            raise Exception("Dataset address is empty")
        if not os.path.exists(data_path):
            raise Exception("Dataset does not exist")
        self.data_path = data_path

    def saveEntity(self, label, data):
        print("\nWrite in entity: ", label)
        for item in tqdm(data, ncols=80):
            try:
                property = []
                for key, value in item.items():
                    value = str(value).replace("'", "")
                    property.append(key + ":" + "'" + value + "'")
                if len(property) == 0:
                    continue
                cql = "MERGE (n:" + label + "{" + ",".join(property) + "})"
                self.graph.run(cql)
            except Exception as e:
                print("Error saving entity:", e)

    def saveRelation(self, s_label, e_label, relation_type, relations):
        print(f"\nWrite in relationships: {relation_type}")
        for relation in tqdm(relations):
            try:
                s_name = relation["s_name"].replace("'", "\\'")
                e_name = relation["e_name"].replace("'", "\\'")
                if relation_type == "INCLUDES_COMPULSORY" or relation_type == "INCLUDES_OPTIONAL":
                    cql = f"MATCH (a:{s_label} {{name: '{s_name}'}}), (b:{e_label} {{code: '{e_name}'}}) MERGE (a)-[r:{relation_type}]->(b)"
                else:
                    cql = f"MATCH (a:{s_label} {{name: '{s_name}'}}), (b:{e_label} {{name: '{e_name}'}}) MERGE (a)-[r:{relation_type}]->(b)"
                self.graph.run(cql)
            except Exception as e:
                print(f"Error saving relation {relation_type}: {e}")

    def init(self):
        # Initialize an empty list of entities and relationships
        universities, degrees, years, compulsoryModules, optionalModules = [], [], [], [], []
        universityDegreeRelations, degreeYearRelations, yearCompulsoryModuleRelations, yearOptionalModuleRelations = [], [], [], []

        with open(self.data_path, 'r', encoding='utf8') as f:
            data = json.load(f)

            # append university entities
            universities.append({"name": data["university"]})

            for degree in data["degrees"]:
                # append degree entities and their relationship with the University
                degrees.append({"name": degree["degree_name"]})
                universityDegreeRelations.append({"s_name": data["university"], "e_name": degree["degree_name"]})

                for year, details in degree["courses"].items():
                    # append year entities and their relationship to degrees
                    yearName = f"{degree['degree_name']} {year.capitalize()}"
                    years.append({"name": yearName})
                    degreeYearRelations.append({"s_name": degree["degree_name"], "e_name": yearName})

                    # append compulsory module entities and their relationship to year entity
                    for module in details.get("compulsory_modules", []):
                        moduleCode = module["module_code"]
                        compulsoryModules.append({
                            "name": module["module_name"],
                            "code": moduleCode,  # Assuming code is used as a unique identifier
                            "credits": module["credits"],
                            "semester": module["semester"],
                            "desc": module["desc"]
                        })
                        yearCompulsoryModuleRelations.append({"s_name": yearName, "e_name": moduleCode})

                    # append optional module entities and their relationship to year entity
                    for module in details.get("optional_modules", []):
                        moduleCode = module["module_code"]
                        optionalModules.append({
                            "name": module["module_name"],
                            "code": moduleCode,  # Assuming code is used as a unique identifier
                            "credits": module["credits"],
                            "semester": module["semester"],
                            "desc": module["desc"]
                        })
                        yearOptionalModuleRelations.append({"s_name": yearName, "e_name": moduleCode})

        # Write in entities and relations
        self.saveEntity("University", universities)
        self.saveEntity("Degree", degrees)
        self.saveEntity("Year", years)
        self.saveEntity("CompulsoryModule", compulsoryModules)
        self.saveEntity("OptionalModule", optionalModules)

        self.saveRelation("University", "Degree", "OFFERS", universityDegreeRelations)
        self.saveRelation("Degree", "Year", "INCLUDES", degreeYearRelations)
        self.saveRelation("Year", "CompulsoryModule", "INCLUDES_COMPULSORY", yearCompulsoryModuleRelations)
        self.saveRelation("Year", "OptionalModule", "INCLUDES_OPTIONAL", yearOptionalModuleRelations)
        
if __name__ == '__main__':
    kg_host = "127.0.0.1"
    kg_port = 7687 # change to your own kg port
    kg_user = os.getenv('NEO4J_USERNAME')
    kg_password = os.getenv('NEO4J_PASSWORD')
    data_path = "./dataset/dataset.json"
    kg = CreateKG(kg_host, kg_port, kg_user, kg_password, data_path)
    kg.init()
