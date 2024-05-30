import yaml
from pathlib import Path

def read_params():
  # Load the YAML file
  with open(Path('conf/parameters.yml'), 'r') as file:
      parameters = yaml.safe_load(file)
  return parameters 