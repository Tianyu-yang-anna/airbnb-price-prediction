import sys
from pathlib import Path
sys.path.append('housing_price/.')
# sys.path.append('../../../')
from covid.traincovidmodel import traincovid


traincovid('nyc')
traincovid('la')
traincovid('chicago')
# print(Path(sys.path[0]).parent.parent)