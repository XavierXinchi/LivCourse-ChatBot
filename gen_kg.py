from py2neo import Graph
import json
from tqdm import tqdm
import os

class CreateKG():

    def __init__(self, kg_host, kg_port, kg_user, kg_password, data_path):
        uri = f"bolt://{kg_user}:{kg_password}@{kg_host}:{kg_port}"
        self.graph = Graph(uri)

        if not data_path or data_path == '':
            raise Exception("数据集地址为空")
        if not os.path.exists(data_path):
            raise Exception("数据集不存在")
        self.data_path = data_path

    def saveEntity(self, label, data):
        print("\n写入实体：", label)
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
        print(f"\n写入关系：{relation_type}")
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
        # 初始化实体和关系的空列表
        universities, degrees, years, compulsoryModules, optionalModules = [], [], [], [], []
        universityDegreeRelations, degreeYearRelations, yearCompulsoryModuleRelations, yearOptionalModuleRelations = [], [], [], []

        with open(self.data_path, 'r', encoding='utf8') as f:
            data = json.load(f)

            # 处理大学实体
            universities.append({"name": data["university"]})

            for degree in data["degrees"]:
                # 处理学位实体及其与大学的关系
                degrees.append({"name": degree["degree_name"]})
                universityDegreeRelations.append({"s_name": data["university"], "e_name": degree["degree_name"]})

                for year, details in degree["courses"].items():
                    # 处理年级实体及其与学位的关系
                    yearName = f"{degree['degree_name']} {year.capitalize()}"
                    years.append({"name": yearName})
                    degreeYearRelations.append({"s_name": degree["degree_name"], "e_name": yearName})

                    # 处理必修模块实体及其与年级的关系
                    for module in details.get("compulsory_modules", []):
                        moduleCode = module["module_code"]
                        compulsoryModules.append({
                            "name": module["module_name"],
                            "code": moduleCode,  # 假设使用 code 作为唯一标识符
                            "credits": module["credits"],
                            "semester": module["semester"],
                            "desc": module["desc"]
                        })
                        yearCompulsoryModuleRelations.append({"s_name": yearName, "e_name": moduleCode})

                    # 处理选修模块实体及其与年级的关系
                    for module in details.get("optional_modules", []):
                        moduleCode = module["module_code"]
                        optionalModules.append({
                            "name": module["module_name"],
                            "code": moduleCode,  # 假设使用 code 作为唯一标识符
                            "credits": module["credits"],
                            "semester": module["semester"],
                            "desc": module["desc"]
                        })
                        yearOptionalModuleRelations.append({"s_name": yearName, "e_name": moduleCode})

        # 写入实体和关系
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
    kg_port = 7687 # 7689
    kg_user = "neo4j"
    kg_password = "SXc2002627SXc"
    data_path = "./dataset/dataset.json"
    kg = CreateKG(kg_host, kg_port, kg_user, kg_password, data_path)
    kg.init()
