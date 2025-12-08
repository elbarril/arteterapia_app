"""Observational questions configuration."""
from flask_babel import lazy_gettext as _l

# Answer options (translatable)
ANSWER_OPTIONS = {
    'yes': _l('Sí'),
    'no': _l('No'),
    'not_sure': _l('No está seguro/a'),
    'not_applicable': _l('No aplica')
}

# Hierarchical question structure
OBSERVATION_CATEGORIES = [
    {
        'id': 'entry',
        'name': _l('INGRESO AL ESPACIO'),
        'questions': [
            {'id': 'entry_on_time', 'text': _l('Llega a horario')},
            {'id': 'entry_resistance', 'text': _l('Muestra resistencia')},
            {'id': 'entry_manages', 'text': _l('Logra ingresar')},
            {'id': 'entry_greeting', 'text': _l('Muestra indicador de saludo')},
        ]
    },
    {
        'id': 'motivation',
        'name': _l('MOTIVACIÓN'),
        'questions': [
            {'id': 'motivation_interest', 'text': _l('Muestra interés')},
            {'id': 'motivation_rejection', 'text': _l('Muestra rechazo')},
            {'id': 'motivation_repetition', 'text': _l('Solicita o necesita repetición')},
        ]
    },
    {
        'id': 'instruction',
        'name': _l('CONSIGNA'),
        'questions': [
            {'id': 'instruction_keeps_mind', 'text': _l('La mantiene en mente')},
            {'id': 'instruction_concentration', 'text': _l('Mantiene la concentración')},
            {'id': 'instruction_requests_repetition', 'text': _l('Solicita repetición')},
            {'id': 'instruction_reiterated', 'text': _l('Se le reitera la consigna')},
            {'id': 'instruction_personal_emergent', 'text': _l('Trae un emergente personal')},
        ]
    },
    {
        'id': 'development',
        'name': _l('DESARROLLO'),
        'subcategories': [
            {
                'id': 'development_beginning',
                'name': _l('Inicio'),
                'questions': [
                    {'id': 'dev_begin_interest', 'text': _l('Muestra interés')},
                ]
            },
            {
                'id': 'development_time',
                'name': _l('Tiempo'),
                'questions': [
                    {'id': 'dev_time_indifferent', 'text': _l('Se muestra indiferente')},
                    {'id': 'dev_time_delayed', 'text': _l('Inicio demorado')},
                    {'id': 'dev_time_expected', 'text': _l('Inicio esperado o establecido')},
                ]
            },
            {
                'id': 'development_materials',
                'name': _l('Materiales'),
                'questions': [
                    {'id': 'dev_mat_explores', 'text': _l('Explora los materiales')},
                    {'id': 'dev_mat_innovative', 'text': _l('Los utiliza de manera innovadora/creativa')},
                    {'id': 'dev_mat_repeats', 'text': _l('Repite el mismo uso')},
                    {'id': 'dev_mat_needs_support', 'text': _l('Necesita apoyo para utilizarlos')},
                    {'id': 'dev_mat_full_use', 'text': _l('Hace uso pleno de ellos')},
                    {'id': 'dev_mat_difficulty', 'text': _l('Muestra dificultad para manipularlos')},
                    {'id': 'dev_mat_asks_other', 'text': _l('Pide otros materiales')},
                ]
            },
            {
                'id': 'development_creativity',
                'name': _l('Creatividad'),
                'questions': [
                    {'id': 'dev_cre_present', 'text': _l('Está presente / conectado/a')},
                    {'id': 'dev_cre_focused', 'text': _l('Se muestra concentrado/a y trabaja')},
                    {'id': 'dev_cre_tolerance', 'text': _l('Muestra tolerancia a la frustración')},
                ]
            },
            {
                'id': 'development_space',
                'name': _l('En el espacio'),
                'questions': [
                    {'id': 'dev_space_asks_help', 'text': _l('Pide ayuda')},
                    {'id': 'dev_space_communicates', 'text': _l('Se comunica')},
                    {'id': 'dev_space_isolates', 'text': _l('Se aísla')},
                    {'id': 'dev_space_helps_others', 'text': _l('Ayuda a otros/as')},
                    {'id': 'dev_space_connection_at', 'text': _l('Establece vínculo con el/la AT')},
                ]
            },
        ]
    },
    {
        'id': 'closure',
        'name': _l('CIERRE'),
        'questions': [
            {'id': 'closure_accepts', 'text': _l('Acepta su propia producción')},
            {'id': 'closure_verbalizes', 'text': _l('Pone en palabras lo producido')},
            {'id': 'closure_denotative', 'text': _l('Hace asociaciones denotativas')},
            {'id': 'closure_connotative', 'text': _l('Expresa asociaciones connotativas')},
            {'id': 'closure_mood_change', 'text': _l('Muestra cambios de ánimo respecto del inicio')},
            {'id': 'closure_bodily_change', 'text': _l('Muestra cambios de actitud corporal respecto del inicio')},
        ]
    },
    {
        'id': 'group',
        'name': _l('GRUPO'),
        'questions': [
            {'id': 'group_respects_turn', 'text': _l('Respeta el turno de habla de los/as otros/as')},
            {'id': 'group_indifferent', 'text': _l('Se muestra indiferente a la palabra de los/as otros/as')},
            {'id': 'group_waits_turn', 'text': _l('Logra esperar su turno')},
            {'id': 'group_registers_presence', 'text': _l('Registra la presencia de otras personas')},
            {'id': 'group_interacts', 'text': _l('Interactúa con otros/as en el espacio')},
        ]
    },
    {
        'id': 'group_climate',
        'name': _l('CLIMA GRUPAL'),
        'questions': [
            {'id': 'climate_favorable', 'text': _l('Favorable')},
            {'id': 'climate_disruptive', 'text': _l('Disruptivo')},
            {'id': 'climate_indifferent', 'text': _l('Indiferente')},
            {'id': 'climate_participatory', 'text': _l('Participativo')},
        ]
    },
]


def get_all_questions():
    """
    Get a flat list of all questions with their category information.
    Returns list of dicts with keys: id, text, category_name, subcategory_name
    """
    questions = []
    
    for category in OBSERVATION_CATEGORIES:
        category_name = category['name']
        
        # Direct questions in category
        if 'questions' in category:
            for q in category['questions']:
                questions.append({
                    'id': q['id'],
                    'text': q['text'],
                    'category': category_name,
                    'subcategory': None
                })
        
        # Questions in subcategories
        if 'subcategories' in category:
            for subcat in category['subcategories']:
                subcat_name = subcat['name']
                for q in subcat['questions']:
                    questions.append({
                        'id': q['id'],
                        'text': q['text'],
                        'category': category_name,
                        'subcategory': subcat_name
                    })
    
    return questions


def get_question_by_index(index):
    """Get a specific question by its index in the flat list."""
    questions = get_all_questions()
    if 0 <= index < len(questions):
        return questions[index]
    return None


def get_total_question_count():
    """Get the total number of questions."""
    return len(get_all_questions())
