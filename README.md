# Particle Life Simulation

Eine interaktive Simulation basierend auf Partikel-Lebensmodellen.
Es Visualisiert, wie sich Partikel durch Anziehungs- bzw. Abstoßungskräfte organisieren und Muster Bilden.

![Particle Life Demo](docs/Demo) /////////

## Features
- **Visuelle Animation**: Echtzeit-Dartellung von Partikeln
- **Anpassbare Parameter**: Konfigurierbare Anziehungs- und Abstoßungskräfte
- **Effiziente Implementierung**: Optimiert für große Partikelmengen

## Installation & Setup

### Voraussetzungen
- Python 3.X+ ///////
- Abhängigkeiten: vispy 0.14.3; numpy 2.1.3; PySide6 6.8.2.1; matplotlib 3.9.2
////////

### Installation
```sh
git clone https://github.com/ricgoe/dsaiis-particle-simulation.git
cd dsaiis-particle-simulation
pip install -r requirements.txt
```

### Start der Simulation
```sh
python GUI.py
```

Hierdurch startet sich automatisch die Benutzeroberfläche. In dieser können sowohl Partikeltypen hinzugefügt als auch die Parameter wie beispielsweise Anziehungs- und Abstoßungskräfte manipuliert werden. Um die Partikel auseinander zu halten können die einzelnen Partikeltypen jeweils ihre eigene Farbe erhalten. 
Für jeden Partikeltyp kann einzeln die Menge bestimmt werden.
Weiterhin sind die Anziehungs- und Abstoßungskräfte für jede Relation einzeln einstellbar. 

Sobald die gewünschten Parameter eingestellt sind, kann man die Simulation über den Button 'Save' starten.
Um zu den Standard-Parametern zurückzukehren, kann man den Button 'Reset' verwenden.

## Hintergrund & Algorithmus
Das Projekt beruht auf partikelbasierten Simulationen. Die Partikel interagieren mit einfachen Regeln:

1. **Anziehung**: Bestimmte Partikel ziehen sich an
2. **Abstoßung**: Andere Partikel stoßen sich ab

Hieraus entsteht eine Dynamik, mit der sich die Partikel basierend auf den Kräften anpassen.