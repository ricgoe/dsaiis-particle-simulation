<script type="text/javascript" async
  src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
</script>


# Konzepte für die Implementierung von Interaktionen verschiedener Partikel 
<br>

## Verschiedene Fälle könnten integriert werden:
- Partikel vereinen sich bei Kollision - generell
- Partikel stoßen sich bei Kollision ab
- Partikel des gleichen Typs ziehen sich an
- Partikel des gleichen Typs stoßen sich ab
- Partikel verschiedener Typen ziehen sich an
- Partikel verschiedener Typen stoßen sich ab
- Partikel wirken Kräfte aufeinander ohne Kollision
  - Gavitationsähnliche Kräfte
  - Abstoßende Kräfte ähnlich zu gleichen Polen 2er Magneten
  - Ein-Weg Anziehung/Abstoßung

<br>

<p align="center">
<img src="./Images/two_vectors_to_same_point.png" width="440"/>
</p>
<p style="text-align: center;"><em>Abbildung 1: Zwei Partikel kollidieren</em></p>

Ausgehend von dieser Situation gibt es verschiedenste Möglichkeiten die folgenden Bewegung der Partikel zu beschreiben und definieren.

### Partikel vereinen sich bei Kollision
Eine mögliche Herangehensweise wäre das Festlegen, dass sich die Partikel bei Zusammenstoß verbinden und für den restlichen Verlauf der Simulation als Einheit behandelt werden
Es gäbe dann unterschiedliche Verhaltensregeln und -weisen zu definieren, die beschreiben und erklären, wie sich der Partikelhaufen verhält.

#### Die erste Bewegung nach der Fusion
Die erste Bewegung der Partikel-Einheit könnte vorhergesagt werden, indem man die Bewegungsvektoren der beiden Partikel addiert. Diese ergeben sich aus der zurückgelegten Strecke zwischen einem Punkt und einem anderen, die jeweils zufällig zugewiesen werden. Sie setzen sich folgendermaßen zusammen:
$$
V_{Bewegung} = (x_{aktuell} - x_{vorher}, y_{aktuell} - y_{vorher})
$$
Die Vektoren werden im Folgenden als $V_1$ und $V_2$ bezeichnet.
DIe erste Bewegung nach der Verschmelzung ließe sich also beispielsweilse durch den Vektor $V_{neu}$ so beschreiben: 

$$
V_{neu} = V_1 + V_2
$$

<br>
<br>
<p align="center">
<img src="./Images/V_new_as_sum.png" width="440"/>
</p>
<p style="text-align: center;"><em>Abbildung 2: Die erste Bewegung der fusionierten Partikel ist gleich der Summe ihrer Richtungsvektoren</em></p>

Das Addieren dieser Vektoren $V_1$ und $V_2$ bedeutet, dass die Bewegung dieser Partikel noch **zufallsbasiert** ist, in sich aber nicht mehr zufällig ist. Diese erste Bewegung lässt sich präzise vorhersagen.
Daraus ergibt sich jedoch eine weitere Frage: 
- Wie werden die folgenden Bewegungen nach der ersten Kollisionsreaktion der Partikel-Einheit bestimmt?

Um dies zu beschreiben könnten verschiedene Ansätze implementiert werden:

1. Es wird ein zufälliger Wert erzeugt, der auf beide Partikel angewendet wird, sodass sie sich immer als Einheit bewegen
2. Jedes Partikel erhält seine eigene zufällige Bewegung, diese werden dann addiert, ähnlich zur Berechnung von $V_{neu}$ zuvor
3. Die fusionierten Teilchen erhalten gar keine zufällig berechnete Position mehr, sondern folgend in jeder Iteration ihrem zuvorigen Bewegungsvektor, indem sie diesen erneut von ihrer aktuellen Position folgen. Sie bewegene sich also auf einer determinierten Linie, bis sie erneut Kolldieren oder andere Kräfte auf sie wirken
4. Beide Partikel erhalten eine neuen zufälligen Richtungsvektor für die nächste Iteration, jedoch ein Partikel mehr Einfluss als das andere auf die folgende Bewegung. Dies könnte durch einen Koeffienzenten $c_{impact} > 0$ für jeden Bewegungsvektor beschrieben werden.

The implementation of the first feature is most likely to require the least computational power. We keep track of each particle-unit that has formed and apply the randomly-determined movement to all its component-particles.

The idea of adding two randomly-determined moves takes this one step further and requires more calculations and operations to be executed. It could lead to the units moving less predictably, but also more interestingly, as the unit would move in a more chaotic way. This includes much faster moves than each particle on its own, but also slower moves, depending on how the random moves are calculated. If the random moves are calcuated to be equally distributed around zero, the unit will move slower than the particles on their own. If the random moves are calculated to be more likely to be larger than zero, the unit on average will move faster than the particles on their own. This is due to the Expected Value being zero. For example, a random variable $X$ with $E(X) = 0$ will have the same probability of being positive as well as negative, if the distribution is symmetric around zero. This means that is equally likely to calculate a positive number as it is to calculate its negative counterpart. The sum of two such random variables will therefore be more likely to be closer to zero than the sum of two random variables equally diestributed around $E(X) \neq  0$. 

The third feature exceeds the previous one regarding the complexity of the calculations. The coefficient $c_{impact}$ would have to have to be calculated for each particle or at least for each particle-class as compromise between the amount of features implemented and the computational power required. One could apply this coefficient only if the particles merge, or even before, making the particles move more extremly.

#### Collision at certain velocity-threshold
Another question to discuss are the conditions under which particles merge. It would be possible to implement a merge of particles each time two or more will share a location, or implememt a certain velocity-threshold $T_{velocity}$, which has to be exceeded in order for particles to merge. This would make the simulation more realistic, as particles in reality do not merge at every collision. The particles would merge if the following condition is met:
$$
\|V_{1}\| + \|V_{2}\| > T_{velocity} 
$$
If the feature of the impact coefficient $c_{impact}$ is implemented, the calculation should be adjusted to:
$$
c_{impact_1} \cdot \|V_{1}\| + c_{impact_2} \cdot \|V_{2}\| > T_{velocity}
$$
<br>

### Kollisionen ohne Verschmelzung

#### Kollisionen ohne Anziehung- oder Abstoßungskräfte

##### Gleichgroße Partikel
Diese Art der Kollisionen betrachtet ausschließlich das Verhalten von Partikel, die selbst (oder deren Kräfte) ohne Kollision nicht miteinander interagieren.
Das schließt Anziehungskräfte, Abstoßungskräfte und Gravitationskräfte aus und sorgt dafür, dass zunächst nur der eigentliche Prozess des Zusammenstoßes und die darauf folgende Bewegung betrachtet wird.
Die Schwierigkeit besteht hierbei darin, die Bewegung der Partikel nach einem Zusammenstoß angemessen vorherzusagen, ohne die geltenden Regeln der Physik grob zu verletzen. 
Gewisse Abstriche müssen jedoch gemacht werden, um die Simulation in einem angemessenen Zeitrahmen durchführen zu können und ist dem Konzept des Codes geschuldet.
Das Problem ist, dass wir keinen kontinuierlichen Zeitraum haben, sondern immer diskrete Zeitabschnitte betrachten. 
Es muss foglich ein Modell gefunden werden, welches die Bewegung der Partikel bestmöglich beschreibt.
Wir gehen an dieser Stelle von Partikeln aus, die sich in Größe, also dem Radius, nicht unterscheiden.
Ein Konzept zur Berechnung von Bewegungen von Teilchen nach einem Zusammenstoß könnte wie im Folgenden beschrieben aussehen.

##### Ansatz
Wir gehen hierfür von einer prinzipiell zufälligen Bewegung der Partikel aus. 
Während einer jeden Iteration wird jedem Teilchen eine zufällige Bewegung zugewiesen, die sich aus einer zufälligen Bewegung in x- und y-Richtung zusammensetzt.
In dieses rein auf Zufall basierende Modell wird nun die Kollision von zwei Partikeln eingeführt, es wird also ein deterministisches Element eingebracht.

Betrachten wir zunächst die Eigenschaften von Code und Teilchen und die genaue Problematik.
Das Backend iteriert in festgelegten Intervallen ber alle Partikel und schreibt diesen neue Koordinaten zu, welche im Anschluss auf dem User Inferface dargstell werden.
Dabei ist das User Interface bislang einer Interation hinter dem Backend.
Das bedeutet, dass schon eine neue Bewegung für die Partikel berechnet wird, bevor die Bewegung der Partikel aus der vorherigen Iteration dargestellt wurde.
Es sind also für jedes Teilchen zwei Positionen bekannt, die aktuelle und die nächste.
Aus diesen lässt sich entsprechend ein Bewegungsvektor $V_{move}$ berechnen. 
Die Länge dieses Vektors entspricht der Distanz, die das Teilchen in der entsprechenden Iteration zurücklegt.
Es gilt also: 
$$
V_{move} = (x_{next} - x_{current}, y_{next} - y_{current})
$$

sowie

$$
\|V_{move}\| = \sqrt{(x_{next} - x_{current})^2 + (y_{next} - y_{current})^2}
$$

und 

$$
D = \|V_{move}\| \iff D = \sqrt{(x_{next} - x_{current})^2 + (y_{next} - y_{current})^2}
$$

Die Distanz $D$ entspricht also der Länge des Bewegungsvektors $V_{move}$ und gibt an, wie weit sich das Teilchen in der entsprechenden Iteration bewegt.
Da die Partikel allesamt gleich groß und gleich schwer sind, lässt sich sagen, dass die Ernergie eines Partikels proportional zu seiner Geschwindigkeit ist.
Da alle Partikel gleich schwer und gleich groß sind, lassen sich dadurch Energien relativ einfach und intuitiv vergleichen.
Dies wird an späterer Stelle noch wichtig. 

Zusäztlich zu den Koordinaten haben wir außerdem für jedes Teilchen einen Radius. 
Dieser ergibt sich aus der Größe des Teilchens und ist in diesem Modell für alle Partikel gleich.
Der Radius ist entscheident, um im User Interface die Teilchen wirklich sichtbar zu machen.
Genau in diesem Radius liegt jedoch die Problematik bei der Berechnung des Zusammenstoßes und den darauf folgenden Bewegungen.
Um dies zu verdeutlichen gehen wir zunächst einmal davon aus, dass die Eigenschaft des Radius nicht existiert und jedes Partikel quasi einem unendlichen kleine Punkt entspricht, der sich durch den Raum bewegt.
In diesem Fall wäre es relativ einfach, die Bewegung der Partikel nach einem Zusammenstoß zu berechnen.
Zunächst muss überprüft werden, ob sich zwei Partikel in der nächsten Iteration überlappen, also ob ihnen die exakt gleichen Koordinaten zugewiesen werden.
Dies lässt sich auch leicht überprüfen. 
Gleichen sich die Koordinaten in einer Iteration bei 2 Punkten, so gibt es eine Kollision, andernfalls nicht. 

Zunächst betrachten wir eine einfache Frontal-Kollision, in der die Richtungsvektoren der beiden Partikel exakt entgegengesetzt sind, also in einem Winkel von 180 Grad zueinander stehen.
Gibt es nun eine Kollision, lässt sich aus den Puls- und Energieerhaltungssätzen ableiten, sodass gilt:
$$
v'_1 = v_2 \quad \text{und} \quad v'_2 = v_1
$$
Außerdem darf in diesem Modell keine Kraft "verloren" gehen.
Da weder Reibung noch andere Kräfte berücksichtigt werden, muss die Summe der Geschwindigkeiten vor und nach dem Zusammenstoß gleich sein:
$$
\|v_1\| + \|v_2\| = \|v'_1\| + \|v'_2\|
$$

Dabei sind $v_1$ und $v_2$ die Richtungsvektoren der beiden Partikel vor dem Zusammenstoß und $v'_1$ und $v'_2$ die Richtungs der beiden Partikel $1$ und $2$ nach dem Zusammenstoß.
Die Geschwindigkeiten der beiden Partikel werden also getauscht.

Betrachten wir nun den Fall, dass sie sich nicht exakt frontal gegenüber stehen, sondern die Richtungsvekoren der Partikel in einem Winkel $\alpha$ zueinander stehen.
In diesem Fall wird die Bewegung der Partikel nach dem Zusammenstoß komplizierter.

Zunächst muss die Kollisionsachse bestimmt werden. 
Die Kollisionsachse ist die Linie, die die beiden Teilchen im Kollisionspunkt verbindet. 
Sie steht senkrecht auf der Linie, die die beiden Mittelpunkte der Teilchen verbindet, bevor sie kollidieren.
Die Komponente der Geschwindigkeit senkrecht zur Kollisionsachse bleibt unverändert, weil dort keine Kraft wirkt.

<p align="center">
<img src="./Images/Kollisionsachse.png" width="440"/>
</p>
<p style="text-align: center;"><em>Abbildung 3: Kollisionsachse der Partikel $vec{P}_1$ und $vec{P}_2$</em></p>

Betrachten wir also zunächst 2 Teilchen $A$ und $B$ mit Positionen $\vec{P}_A​$ und $\vec{P}_B​$.
Die Kollsisionachse beschreibt die Linie, die senkrecht auf der Verbindungslinie der beiden Teilchen steht, als auch durch den Kollisionspunkt geht. 
Darstellen lässt sich die Verbindungslinine als Gerade $g_{connect} = \vec{{OP}_1} + r \cdot (\vec{P_2} - \vec{P_1})$
Nun benötigen wir eine Normale zur Geraden g, die durch den Kollisionspunkt geht.
Diese Normale ist die Kollisionsachse $g_{collision}$.

##### Berechnung der Kollisionsachse
Die Kollisionsachse lässt sich folgendermaßen berechnen:
Wir suchen zunächst den Punkt $Q$ auf $g_{connect}$, der senkrecht auf $g_{connect}$ steht und Schnittpunkt von $g_{connect}$ und $g_{collision}$ ist.
$Q$ 

Nun müssen wir die Richtungsvektoren $\vec{v_A}$ und $\vec{v_B}$ der beiden Teilchen jeweils in zwei Komponenten zerlegen.
Die eine Komponente zeigt parallel zur Kollisionsachse, die andere steht senkrecht dazu.

**Komponenten der Geschwindigkeit parallel zur Kollisionsachse**
$$
\vec{v_{A,||}} = (\vec{v_A} \cdot \vec{n}) \cdot \vec{n}
$$

$$
\vec{v_{B,||}} = (\vec{v_B} \cdot \vec{n}) \cdot \vec{n}
$$

Diese Vektoren entsprechen der Projektion der Geschwindigkeitsvektoren auf die Kollisionsachse.

**Komponenten der Geschwindigkeit orthogonal zur Kollisionsachse**

$$
\vec{v_{A,\perp}} = \vec{v_A} - \vec{v_{A,||}}
$$
$$
\vec{v_{B,\perp}} = \vec{v_B} - \vec{v_{B,||}}
$$

Wozu brauchen wir diese Komponenten und was passiert bei der Kollision?
Während der Kollision tauschen die Richtungsvektoren der beiden Teilchen ihre Komponenten parallel zur Kollisionsachse.
Die Komponenten orthogonal zur Kollisionsachse bleiben unverändert.

Die Richtungsvektoren der beiden Teilchen nach der Kollision lassen sich also wie folgt berechnen:
$$
\vec{v'_A} = \vec{v_{A,\perp}} + \vec{v_{B,||}}
$$
$$
\vec{v'_B} = \vec{v_{B,\perp}} + \vec{v_{A,||}}
$$

Zuletzt darf nicht vernachlässigt werden, dass die beiden Partikel ${A}$ und ${B}$ in der nächsten Iteration im Anschluss an die Kollision keiner zufälligen Bewegung mehr folgen dürfen. Für sie darf also in der Folgeiteration kein neues zufälliges Koordinatenpaar erzeugt werden, da sonst diese Berechnung hinfällig wäre. Es muss also vermerkt bleiben, für welche Teilchen schon eine Bewegung berchnet wurde. 

