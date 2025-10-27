from dataclasses import dataclass

@dataclass
class Meteo:
    data: str
    id: int
    humidite: int
    pluie_intensite_max: float
    pression: int
    type_de_station: str
    pluie: float
    direction_du_vecteur_de_vent_max: int
    direction_du_vecteur_de_rafale_de_vent_max: float
    direction_du_vecteur_vent_moyen: int
    force_moyenne_du_vecteur_vent: int
    force_rafale_max: int
    temperature: float
    heure_de_paris: str
    heure_utc: str
