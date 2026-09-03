"""Small, dependency-free localization layer for the Fusion add-in UI."""

import locale
import os


SUPPORTED_LANGUAGES = ('en', 'de', 'fr', 'es', 'pl')

_TEXT = {
    'en': {
        'command_description': 'Split models into printable segments and add alignment connectors.',
        'mode': 'Mode', 'create_split': 'Create split operation', 'set_point': 'Set Point',
        'split': 'Split', 'solid_body': 'Solid body',
        'select_body': 'Select one solid body to split.',
        'construction_plane': 'Construction plane',
        'select_plane': 'Select one construction plane as the splitting tool.',
        'scope': 'Version {version} adds English, German, French, Spanish, and Polish user interfaces.',
        'validation': 'Validation', 'select_body_plane': 'Select a solid body and a construction plane.',
        'valid_intersection': 'Valid: the construction plane intersects the solid body.',
        'invalid_intersection': 'Invalid: the construction plane does not intersect the solid body.',
        'positions': 'Positions', 'position_sketch': 'Position sketch',
        'select_sjp_sketch': 'Select an SJP sketch or one of its points.',
        'detected_points': 'Detected points', 'select_position_sketch': 'Select a position sketch.',
        'selected_list': 'Selected list', 'no_positions': 'No positions selected.',
        'connector': 'Connector', 'shape': 'Shape', 'round': 'Round', 'd_shaped': 'D-shaped',
        'oval': 'Oval', 'rounded_rectangle': 'Rounded rectangle', 'hexagon': 'Hexagon',
        'width_diameter': 'Width / diameter', 'height': 'Height', 'corner_radius': 'Corner radius',
        'total_length': 'Total length', 'lead_in': 'Lead-in chamfer', 'fit': 'Fit',
        'radial_clearance': 'Radial clearance per side', 'depth_clearance': 'Depth clearance',
        'point': 'Point {index} ({x:.3f}, {y:.3f} cm)',
        'point_count': '{detected} position point(s) detected; {selected} selected.',
        'selected_point': 'Point {index}: {x:.3f}, {y:.3f} cm',
        'select_one_sketch': 'Select one position sketch.',
        'no_points_found': 'No position points were found.',
        'invalid_connector': 'Select a supported shape and at least one position, enter valid positive dimensions, use non-negative clearances, and keep the lead-in chamfer smaller than both the smallest profile radius and half the total length.',
        'not_sjp_sketch': 'The selected sketch is not a SegmentJoinPilot position sketch.',
        'already_exists': '{name} already exists.',
        'connector_failed': 'The connector operation could not be created.\n\n{error}',
        'split_no_intersection': 'The construction plane does not intersect the selected solid body.\n\nChoose a plane that passes through the body and try again.',
        'split_failed': 'The body could not be split.\n\n{error}\n\nNo partial split feature was retained.',
        'split_complete': '{name}: split completed. Add position points or sketch geometry to {sketch}, then select Finish Sketch.',
        'sketch_unavailable': 'The position sketch is no longer available.',
        'new_sketch_unavailable': 'The newly created position sketch is no longer available.',
        'edit_command_missing': 'Fusion could not find the Edit Sketch command.',
        'open_sketch_failed': 'Fusion could not open the position sketch for editing.',
        'restart_failed': 'SegmentJoinPilot could not be restarted.',
        'connector_success': '{connectors} connector body/bodies and {sockets} socket cut(s) created.',
        'selected_candidates': 'Selected candidates', 'connector_bodies': 'Connector bodies',
    },
    'de': {
        'command_description': 'Modelle in druckbare Segmente teilen und Ausrichtungsverbinder hinzufügen.',
        'mode': 'Modus', 'create_split': 'Teilung erstellen', 'set_point': 'Punkte setzen',
        'split': 'Teilung', 'solid_body': 'Volumenkörper', 'select_body': 'Einen zu teilenden Volumenkörper auswählen.',
        'construction_plane': 'Konstruktionsebene', 'select_plane': 'Eine Konstruktionsebene als Trennwerkzeug auswählen.',
        'scope': 'Version {version} ergänzt deutsche, englische, französische, spanische und polnische Oberflächen.',
        'validation': 'Prüfung', 'select_body_plane': 'Volumenkörper und Konstruktionsebene auswählen.',
        'valid_intersection': 'Gültig: Die Konstruktionsebene schneidet den Volumenkörper.',
        'invalid_intersection': 'Ungültig: Die Konstruktionsebene schneidet den Volumenkörper nicht.',
        'positions': 'Positionen', 'position_sketch': 'Positionsskizze', 'select_sjp_sketch': 'Eine SJP-Skizze oder einen ihrer Punkte auswählen.',
        'detected_points': 'Erkannte Punkte', 'select_position_sketch': 'Eine Positionsskizze auswählen.',
        'selected_list': 'Auswahlliste', 'no_positions': 'Keine Positionen ausgewählt.',
        'connector': 'Verbinder', 'shape': 'Form', 'round': 'Rund', 'd_shaped': 'D-förmig', 'oval': 'Oval',
        'rounded_rectangle': 'Abgerundetes Rechteck', 'hexagon': 'Sechseck',
        'width_diameter': 'Breite / Durchmesser', 'height': 'Höhe', 'corner_radius': 'Eckenradius',
        'total_length': 'Gesamtlänge', 'lead_in': 'Einführfase', 'fit': 'Passung',
        'radial_clearance': 'Radialspiel je Seite', 'depth_clearance': 'Tiefenspiel',
        'point': 'Punkt {index} ({x:.3f}, {y:.3f} cm)', 'point_count': '{detected} Positionspunkt(e) erkannt; {selected} ausgewählt.',
        'selected_point': 'Punkt {index}: {x:.3f}, {y:.3f} cm', 'select_one_sketch': 'Eine Positionsskizze auswählen.',
        'no_points_found': 'Keine Positionspunkte gefunden.', 'invalid_connector': 'Eine unterstützte Form und mindestens eine Position auswählen, gültige positive Maße und nichtnegative Spiele eingeben und die Einführfase kleiner als den kleinsten Profilradius und die halbe Gesamtlänge halten.',
        'not_sjp_sketch': 'Die ausgewählte Skizze ist keine SegmentJoinPilot-Positionsskizze.', 'already_exists': '{name} ist bereits vorhanden.',
        'connector_failed': 'Der Verbindervorgang konnte nicht erstellt werden.\n\n{error}',
        'split_no_intersection': 'Die Konstruktionsebene schneidet den ausgewählten Volumenkörper nicht.\n\nEine Ebene wählen, die durch den Körper verläuft.',
        'split_failed': 'Der Körper konnte nicht geteilt werden.\n\n{error}\n\nEs wurde keine unvollständige Teilung beibehalten.',
        'split_complete': '{name}: Teilung abgeschlossen. Positionspunkte oder Skizziergeometrie zu {sketch} hinzufügen und anschließend Skizze fertig stellen wählen.',
        'sketch_unavailable': 'Die Positionsskizze ist nicht mehr verfügbar.', 'new_sketch_unavailable': 'Die neu erstellte Positionsskizze ist nicht mehr verfügbar.',
        'edit_command_missing': 'Fusion konnte den Befehl Skizze bearbeiten nicht finden.', 'open_sketch_failed': 'Fusion konnte die Positionsskizze nicht zum Bearbeiten öffnen.',
        'restart_failed': 'SegmentJoinPilot konnte nicht neu gestartet werden.',
        'connector_success': '{connectors} Verbinderkörper und {sockets} Aussparung(en) erstellt.',
        'selected_candidates': 'Ausgewählte Positionen', 'connector_bodies': 'Verbinderkörper',
    },
    'fr': {
        'command_description': "Diviser les modèles en segments imprimables et ajouter des connecteurs d'alignement.",
        'mode': 'Mode', 'create_split': 'Créer une division', 'set_point': 'Définir les points', 'split': 'Division',
        'solid_body': 'Corps solide', 'select_body': 'Sélectionnez un corps solide à diviser.',
        'construction_plane': 'Plan de construction', 'select_plane': 'Sélectionnez un plan de construction comme outil de division.',
        'scope': "La version {version} ajoute les interfaces anglaise, allemande, française, espagnole et polonaise.",
        'validation': 'Validation', 'select_body_plane': 'Sélectionnez un corps solide et un plan de construction.',
        'valid_intersection': 'Valide : le plan de construction coupe le corps solide.', 'invalid_intersection': 'Non valide : le plan de construction ne coupe pas le corps solide.',
        'positions': 'Positions', 'position_sketch': 'Esquisse de positions', 'select_sjp_sketch': "Sélectionnez une esquisse SJP ou l'un de ses points.",
        'detected_points': 'Points détectés', 'select_position_sketch': 'Sélectionnez une esquisse de positions.', 'selected_list': 'Liste sélectionnée', 'no_positions': 'Aucune position sélectionnée.',
        'connector': 'Connecteur', 'shape': 'Forme', 'round': 'Rond', 'd_shaped': 'En D', 'oval': 'Ovale', 'rounded_rectangle': 'Rectangle arrondi', 'hexagon': 'Hexagone',
        'width_diameter': 'Largeur / diamètre', 'height': 'Hauteur', 'corner_radius': "Rayon d'angle", 'total_length': 'Longueur totale', 'lead_in': "Chanfrein d'entrée", 'fit': 'Ajustement',
        'radial_clearance': 'Jeu radial par côté', 'depth_clearance': 'Jeu en profondeur',
        'point': 'Point {index} ({x:.3f}, {y:.3f} cm)', 'point_count': '{detected} point(s) de position détecté(s) ; {selected} sélectionné(s).', 'selected_point': 'Point {index} : {x:.3f}, {y:.3f} cm',
        'select_one_sketch': 'Sélectionnez une esquisse de positions.', 'no_points_found': 'Aucun point de position trouvé.',
        'invalid_connector': "Sélectionnez une forme prise en charge et au moins une position, entrez des dimensions positives valides et des jeux non négatifs, puis limitez le chanfrein d'entrée.",
        'not_sjp_sketch': "L'esquisse sélectionnée n'est pas une esquisse de positions SegmentJoinPilot.", 'already_exists': '{name} existe déjà.',
        'connector_failed': "L'opération de connecteur n'a pas pu être créée.\n\n{error}", 'split_no_intersection': 'Le plan de construction ne coupe pas le corps solide sélectionné.\n\nChoisissez un plan traversant le corps.',
        'split_failed': "Le corps n'a pas pu être divisé.\n\n{error}\n\nAucune division partielle n'a été conservée.", 'split_complete': '{name} : division terminée. Ajoutez des points ou une géométrie à {sketch}, puis terminez l’esquisse.',
        'sketch_unavailable': "L'esquisse de positions n'est plus disponible.", 'new_sketch_unavailable': "La nouvelle esquisse de positions n'est plus disponible.", 'edit_command_missing': "Fusion n'a pas trouvé la commande Modifier l'esquisse.",
        'open_sketch_failed': "Fusion n'a pas pu ouvrir l'esquisse de positions.", 'restart_failed': "SegmentJoinPilot n'a pas pu redémarrer.",
        'connector_success': '{connectors} corps de connecteur et {sockets} découpe(s) créés.', 'selected_candidates': 'Positions sélectionnées', 'connector_bodies': 'Corps de connecteur',
    },
    'es': {
        'command_description': 'Dividir modelos en segmentos imprimibles y añadir conectores de alineación.', 'mode': 'Modo', 'create_split': 'Crear división', 'set_point': 'Definir puntos',
        'split': 'División', 'solid_body': 'Cuerpo sólido', 'select_body': 'Seleccione un cuerpo sólido para dividir.', 'construction_plane': 'Plano de construcción', 'select_plane': 'Seleccione un plano de construcción como herramienta de división.',
        'scope': 'La versión {version} añade interfaces en inglés, alemán, francés, español y polaco.', 'validation': 'Validación', 'select_body_plane': 'Seleccione un cuerpo sólido y un plano de construcción.',
        'valid_intersection': 'Válido: el plano de construcción intersecta el cuerpo sólido.', 'invalid_intersection': 'No válido: el plano de construcción no intersecta el cuerpo sólido.',
        'positions': 'Posiciones', 'position_sketch': 'Boceto de posiciones', 'select_sjp_sketch': 'Seleccione un boceto SJP o uno de sus puntos.', 'detected_points': 'Puntos detectados', 'select_position_sketch': 'Seleccione un boceto de posiciones.',
        'selected_list': 'Lista seleccionada', 'no_positions': 'No hay posiciones seleccionadas.', 'connector': 'Conector', 'shape': 'Forma', 'round': 'Redondo', 'd_shaped': 'En D', 'oval': 'Ovalado', 'rounded_rectangle': 'Rectángulo redondeado', 'hexagon': 'Hexágono',
        'width_diameter': 'Anchura / diámetro', 'height': 'Altura', 'corner_radius': 'Radio de esquina', 'total_length': 'Longitud total', 'lead_in': 'Chaflán de entrada', 'fit': 'Ajuste', 'radial_clearance': 'Holgura radial por lado', 'depth_clearance': 'Holgura de profundidad',
        'point': 'Punto {index} ({x:.3f}, {y:.3f} cm)', 'point_count': '{detected} punto(s) de posición detectado(s); {selected} seleccionado(s).', 'selected_point': 'Punto {index}: {x:.3f}, {y:.3f} cm',
        'select_one_sketch': 'Seleccione un boceto de posiciones.', 'no_points_found': 'No se encontraron puntos de posición.', 'invalid_connector': 'Seleccione una forma compatible y al menos una posición, introduzca dimensiones positivas válidas y holguras no negativas, y limite el chaflán de entrada.',
        'not_sjp_sketch': 'El boceto seleccionado no es un boceto de posiciones de SegmentJoinPilot.', 'already_exists': '{name} ya existe.', 'connector_failed': 'No se pudo crear la operación del conector.\n\n{error}',
        'split_no_intersection': 'El plano de construcción no intersecta el cuerpo sólido seleccionado.\n\nElija un plano que atraviese el cuerpo.', 'split_failed': 'No se pudo dividir el cuerpo.\n\n{error}\n\nNo se conservó ninguna división parcial.',
        'split_complete': '{name}: división completada. Añada puntos o geometría a {sketch} y finalice el boceto.', 'sketch_unavailable': 'El boceto de posiciones ya no está disponible.', 'new_sketch_unavailable': 'El boceto de posiciones recién creado ya no está disponible.',
        'edit_command_missing': 'Fusion no encontró el comando Editar boceto.', 'open_sketch_failed': 'Fusion no pudo abrir el boceto de posiciones.', 'restart_failed': 'No se pudo reiniciar SegmentJoinPilot.',
        'connector_success': 'Se crearon {connectors} cuerpo(s) de conector y {sockets} corte(s).', 'selected_candidates': 'Posiciones seleccionadas', 'connector_bodies': 'Cuerpos de conector',
    },
    'pl': {
        'command_description': 'Dziel modele na segmenty do druku i dodawaj łączniki pozycjonujące.', 'mode': 'Tryb', 'create_split': 'Utwórz podział', 'set_point': 'Ustaw punkty',
        'split': 'Podział', 'solid_body': 'Bryła', 'select_body': 'Wybierz jedną bryłę do podziału.', 'construction_plane': 'Płaszczyzna konstrukcyjna', 'select_plane': 'Wybierz płaszczyznę konstrukcyjną jako narzędzie podziału.',
        'scope': 'Wersja {version} dodaje interfejs angielski, niemiecki, francuski, hiszpański i polski.', 'validation': 'Walidacja', 'select_body_plane': 'Wybierz bryłę i płaszczyznę konstrukcyjną.',
        'valid_intersection': 'Prawidłowo: płaszczyzna konstrukcyjna przecina bryłę.', 'invalid_intersection': 'Nieprawidłowo: płaszczyzna konstrukcyjna nie przecina bryły.',
        'positions': 'Pozycje', 'position_sketch': 'Szkic pozycji', 'select_sjp_sketch': 'Wybierz szkic SJP lub jeden z jego punktów.', 'detected_points': 'Wykryte punkty', 'select_position_sketch': 'Wybierz szkic pozycji.',
        'selected_list': 'Wybrane pozycje', 'no_positions': 'Nie wybrano pozycji.', 'connector': 'Łącznik', 'shape': 'Kształt', 'round': 'Okrągły', 'd_shaped': 'W kształcie D', 'oval': 'Owalny', 'rounded_rectangle': 'Zaokrąglony prostokąt', 'hexagon': 'Sześciokąt',
        'width_diameter': 'Szerokość / średnica', 'height': 'Wysokość', 'corner_radius': 'Promień narożnika', 'total_length': 'Długość całkowita', 'lead_in': 'Faza wprowadzająca', 'fit': 'Pasowanie', 'radial_clearance': 'Luz promieniowy na stronę', 'depth_clearance': 'Luz głębokości',
        'point': 'Punkt {index} ({x:.3f}, {y:.3f} cm)', 'point_count': 'Wykryto {detected} punkt(y/ów) pozycji; wybrano {selected}.', 'selected_point': 'Punkt {index}: {x:.3f}, {y:.3f} cm',
        'select_one_sketch': 'Wybierz jeden szkic pozycji.', 'no_points_found': 'Nie znaleziono punktów pozycji.', 'invalid_connector': 'Wybierz obsługiwany kształt i co najmniej jedną pozycję, podaj prawidłowe dodatnie wymiary i nieujemne luzy oraz ogranicz fazę wprowadzającą.',
        'not_sjp_sketch': 'Wybrany szkic nie jest szkicem pozycji SegmentJoinPilot.', 'already_exists': '{name} już istnieje.', 'connector_failed': 'Nie można utworzyć operacji łącznika.\n\n{error}',
        'split_no_intersection': 'Płaszczyzna konstrukcyjna nie przecina wybranej bryły.\n\nWybierz płaszczyznę przechodzącą przez bryłę.', 'split_failed': 'Nie można podzielić bryły.\n\n{error}\n\nNie zachowano częściowego podziału.',
        'split_complete': '{name}: podział zakończony. Dodaj punkty lub geometrię do {sketch}, a następnie zakończ szkic.', 'sketch_unavailable': 'Szkic pozycji nie jest już dostępny.', 'new_sketch_unavailable': 'Nowo utworzony szkic pozycji nie jest już dostępny.',
        'edit_command_missing': 'Fusion nie znalazł polecenia Edytuj szkic.', 'open_sketch_failed': 'Fusion nie mógł otworzyć szkicu pozycji.', 'restart_failed': 'Nie można ponownie uruchomić SegmentJoinPilot.',
        'connector_success': 'Utworzono {connectors} korpus(y) łącznika i {sockets} wycięcie(a).', 'selected_candidates': 'Wybrane pozycje', 'connector_bodies': 'Korpusy łącznika',
    },
}


def _normalize_language(value):
    code = str(value or '').replace('_', '-').split('-', 1)[0].lower()
    return code if code in SUPPORTED_LANGUAGES else None


def current_language():
    override = _normalize_language(os.environ.get('SJP_LANGUAGE'))
    if override:
        return override
    try:
        import adsk.core
        language = adsk.core.Application.get().preferences.generalPreferences.userLanguage
        enum_map = {
            'EnglishLanguage': 'en', 'GermanLanguage': 'de', 'FrenchLanguage': 'fr',
            'SpanishLanguage': 'es', 'PolishLanguage': 'pl',
        }
        for enum_name, code in enum_map.items():
            enum_value = getattr(adsk.core.UserLanguages, enum_name, None)
            if enum_value is not None and language == enum_value:
                return code
    except Exception:
        pass
    try:
        return _normalize_language(locale.getlocale()[0]) or 'en'
    except Exception:
        return 'en'


def tr(key, **values):
    language = current_language()
    template = _TEXT.get(language, {}).get(key, _TEXT['en'].get(key, key))
    return template.format(**values) if values else template
