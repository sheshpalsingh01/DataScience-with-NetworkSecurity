"""
 The setup.py file is an esential part of packaging and distributing your 
 project as a python package.. it is used by setup tools to define the configuration 
 of the project such as 
 name, metadata, 
 version, 
 dependencies, 
 entry points 
 and more

 """

from os import name
from setuptools import setup, find_packages
from typing import List

def get_requirements() -> List[str]:
    """ 
     this function return list of the requirements

    """
    requirements_list : List[str] = []
    try:
        with open("requirements.txt",'r') as file_obj:
            requirements = file_obj.readlines()
            
            # remove the "\n" from the requirements
            for line in requirements:
                requirement = line.strip()

                if requirement and requirement !="-e .":
                    requirements_list.append(requirement)
            
            return requirements_list

            
    except FileNotFoundError :
        print("Requirements file is not found.")


setup(
    name="DataScienceNetworkSecurity",
    version = "0.0.1",
    author ="Sheshpal",
    author_email=['sheshpalsingh2024@gmail.com'],
    packages=find_packages(),
    install_requires=get_requirements()
)

print(get_requirements())